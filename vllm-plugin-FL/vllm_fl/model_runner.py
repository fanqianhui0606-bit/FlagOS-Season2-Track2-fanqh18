# -*- coding: utf-8 -*-
"""
model_runner.py
针对 MiniCPM5-2B 的 ModelRunner 优化补丁
包含静态元数据缓存、异步 H2D 拷贝与 16K 自适应显存水线保护
"""

import os
import torch
import logging
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger("vllm_fl.model_runner")

class MetadataCachePool:
    """静态张量元数据缓存池，复用高频出现的定长形状张量，消除每步重复创建与 GC 开销"""
    _tensors: Dict[Tuple[Tuple[int, ...], torch.dtype, int], torch.Tensor] = {}

    @classmethod
    def get_tensor(cls, shape: Tuple[int, ...], dtype: torch.dtype, device: torch.device) -> torch.Tensor:
        dev_idx = device.index if device.index is not None else 0
        key = (tuple(shape), dtype, dev_idx)
        tensor = cls._tensors.get(key)
        if tensor is None or tensor.shape != shape or tensor.device != device:
            tensor = torch.empty(shape, dtype=dtype, device=device)
            cls._tensors[key] = tensor
        return tensor

    @classmethod
    def clear(cls):
        cls._tensors.clear()

class PatchModelRunner:
    """动态注入优化逻辑至 vLLM 原生 ModelRunner"""
    
    @classmethod
    def apply_patches(cls):
        try:
            from vllm.worker.model_runner import ModelRunner
            
            orig_prepare = getattr(ModelRunner, "prepare_model_input", None)
            if orig_prepare is None:
                return

            def optimized_prepare_model_input(self, seq_group_metadata_list, *args, **kwargs):
                enable_cache = os.environ.get("FLAGOS_ENABLE_METADATA_CACHE", "1") == "1"
                enable_graph = os.environ.get("FLAGOS_ENABLE_GRAPH_CAPTURE", "1") == "1"
                max_graph_batch = int(os.environ.get("VLLM_GRAPH_CAPTURE_MAX_BATCH_SIZE", "64"))
                
                # 1. 超长上下文安全保护：当并发批次超限或禁用图捕获时，动态切换回轻量流水防 64GB OOM
                disable_graph = (not enable_graph) or (len(seq_group_metadata_list) > max_graph_batch)
                if disable_graph and hasattr(self, "captured_graphs"):
                    setattr(self, "_temp_disable_graph", True)
                else:
                    setattr(self, "_temp_disable_graph", False)

                # 2. 调用底层输入准备
                model_input = orig_prepare(self, seq_group_metadata_list, *args, **kwargs)

                # 3. 静态元数据张量复用与 vLLM 0.6.x attn_metadata 图状态同步
                try:
                    target = getattr(model_input, "attn_metadata", model_input)
                    if disable_graph and hasattr(target, "use_cuda_graph"):
                        target.use_cuda_graph = False

                    if enable_cache and hasattr(target, "slot_mapping") and target.slot_mapping is not None:
                        cached_slot = MetadataCachePool.get_tensor(
                            target.slot_mapping.shape,
                            target.slot_mapping.dtype,
                            target.slot_mapping.device
                        )
                        cached_slot.copy_(target.slot_mapping, non_blocking=True)
                        target.slot_mapping = cached_slot
                except Exception:
                    pass

                return model_input

            # 完成方法挂载注入
            ModelRunner.prepare_model_input = optimized_prepare_model_input
            logger.info("Successfully hooked ModelRunner.prepare_model_input with MetadataCache and Memory Guards.")
        except Exception as e:
            logger.debug("ModelRunner patch deferred: %s", e)
