# -*- coding: utf-8 -*-
"""
FlagGems 5.3.5 定制优化算子库 (针对 MiniCPM5-2B 异构芯片适配版)
包含严格 FP32 累加保障、环境变量消融开关与融合算子实际绑定
"""

import os
import logging
import torch
from .ops.fused_rmsnorm import fused_rms_norm, fused_rms_norm_residual
from .ops.fused_silu import fused_silu_and_mul
from .ops.fused_rope import fused_rotary_embedding

__all__ = [
    "fused_rms_norm",
    "fused_rms_norm_residual",
    "fused_silu_and_mul",
    "fused_rotary_embedding",
    "enable",
]

logger = logging.getLogger("flag_gems")

def enable():
    """实际将优化算子挂载进系统算子分发树（支持 FLAGOS_ENABLE_FUSED_OPS 环境变量开关）"""
    if os.environ.get("FLAGOS_ENABLE_FUSED_OPS", "1") != "1":
        logger.info("FlagGems: Fused operators disabled via FLAGOS_ENABLE_FUSED_OPS=0.")
        return

    logger.info("FlagGems: Binding High-Precision Fused Triton Kernels for MiniCPM5-2B...")

    # 1. 动态注入 FlagGems 算子命名空间
    try:
        import flag_gems.ops as fg_ops
        fg_ops.rms_norm = fused_rms_norm
        fg_ops.fused_add_rms_norm = fused_rms_norm_residual
        fg_ops.silu_and_mul = fused_silu_and_mul
        logger.info("  [Mounted] flag_gems.ops -> fused_rms_norm / fused_silu_and_mul")
    except Exception as e:
        logger.debug("FlagGems ops namespace hook fallback: %s", e)

    # 2. 替换 vLLM 内部 RMSNorm 实现（带异常安全回退）
    try:
        from vllm.model_executor.layers import layernorm
        if hasattr(layernorm, "RMSNorm"):
            orig_rmsnorm_forward = layernorm.RMSNorm.forward

            def custom_rmsnorm_forward(self, x, residual=None):
                if os.environ.get("FLAGOS_ENABLE_FUSED_OPS", "1") != "1":
                    return orig_rmsnorm_forward(self, x, residual)
                try:
                    if residual is not None:
                        return fused_rms_norm_residual(x, residual, self.weight, self.variance_epsilon)
                    return fused_rms_norm(x, self.weight, self.variance_epsilon)
                except Exception:
                    return orig_rmsnorm_forward(self, x, residual)

            layernorm.RMSNorm.forward = custom_rmsnorm_forward
            logger.info("  [Mounted] vllm RMSNorm.forward -> custom_rmsnorm_forward (FP32 Reduction)")
    except Exception as e:
        logger.debug("vLLM layernorm hook fallback: %s", e)

    # 3. 替换 vLLM 内部 SiLUAndMul 激活实现（带异常安全回退）
    try:
        from vllm.model_executor.layers import activation
        if hasattr(activation, "SiluAndMul"):
            orig_silu_forward = activation.SiluAndMul.forward

            def custom_silu_forward(self, x):
                if os.environ.get("FLAGOS_ENABLE_FUSED_OPS", "1") != "1":
                    return orig_silu_forward(self, x)
                try:
                    d = x.shape[-1] // 2
                    return fused_silu_and_mul(x[..., :d].contiguous(), x[..., d:].contiguous())
                except Exception:
                    return orig_silu_forward(self, x)

            activation.SiluAndMul.forward = custom_silu_forward
            logger.info("  [Mounted] vllm SiluAndMul.forward -> custom_silu_forward (FP32 Activation)")
    except Exception as e:
        logger.debug("vLLM activation hook fallback: %s", e)
