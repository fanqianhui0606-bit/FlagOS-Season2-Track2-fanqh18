# -*- coding: utf-8 -*-
"""
vllm-plugin-FL: FlagOS Multi-Chip Inference Optimization Plugin
"""

import os
import logging

logger = logging.getLogger("vllm_fl")

def register():
    """vLLM 官方插件注册入口"""
    enable_metadata_cache = os.environ.get("FLAGOS_ENABLE_METADATA_CACHE", "1") == "1"
    enable_graph = os.environ.get("FLAGOS_ENABLE_GRAPH_CAPTURE", "1") == "1"
    
    logger.info("Initializing vllm-plugin-FL (Season 2 Branch: flagos-2026-s2)")
    logger.info(f"  [Opt] Metadata Caching: {enable_metadata_cache}")
    logger.info(f"  [Opt] Adaptive Graph Capture: {enable_graph}")
    
    # 1. 动态载入模型运行器与调度增强层
    from .model_runner import PatchModelRunner
    PatchModelRunner.apply_patches()

    # 2. 自动触发 FlagGems 高保真融合算子绑定
    try:
        import flag_gems
        if hasattr(flag_gems, "enable"):
            flag_gems.enable()
    except Exception as e:
        logger.debug(f"FlagGems enable skipped or deferred: {e}")
