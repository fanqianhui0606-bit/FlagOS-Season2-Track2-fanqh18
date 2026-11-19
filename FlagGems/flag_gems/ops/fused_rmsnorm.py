# -*- coding: utf-8 -*-
"""
fused_rmsnorm.py
Triton 实现的高保真 RMSNorm 算子（同时支持纯归一化与 Residual 融合）
【深度审计修复】：
1. 支持任意输入维度（2D [total_tokens, hidden_size]、3D [batch, seq_len, hidden_size] 等）；
2. 同时提供符合标准接口的 fused_rms_norm (单输出) 与 fused_rms_norm_residual (双输出)；
3. 方差累加与归约必须显式使用 tl.float32 寄存器，死保 math_500 精度零分叉。
"""

import torch
import triton
import triton.language as tl

@triton.jit
def _rms_norm_kernel(
    X_ptr,          # 输入激活 [M, N]
    R_ptr,          # 可选残差输入 [M, N] (为 None 时不相加)
    W_ptr,          # RMSNorm 权重 [N]
    Out_ptr,        # 归一化输出 [M, N]
    Residual_Out_ptr, # 可选残差写回 [M, N]
    stride_xm, stride_xn,
    stride_rm, stride_rn,
    stride_om, stride_on,
    stride_rom, stride_ron,
    N, eps,
    HAS_RESIDUAL: tl.constexpr,
    BLOCK_N: tl.constexpr
):
    row_idx = tl.program_id(0)
    cols = tl.arange(0, BLOCK_N)
    mask = cols < N

    # 1. 读取主激活
    x = tl.load(X_ptr + row_idx * stride_xm + cols * stride_xn, mask=mask, other=0.0)

    # 2. 残差逻辑（若有残差则单次访存加和并写回）
    if HAS_RESIDUAL:
        r = tl.load(R_ptr + row_idx * stride_rm + cols * stride_rn, mask=mask, other=0.0)
        sum_val = x + r
        tl.store(Residual_Out_ptr + row_idx * stride_rom + cols * stride_ron, sum_val, mask=mask)
    else:
        sum_val = x

    # 3. 严格使用寄存器级 FP32 归约求均方差，规避 bf16/fp16 累加溢出与舍入漂移
    val_fp32 = sum_val.to(tl.float32)
    var = tl.sum(val_fp32 * val_fp32, axis=0) / N
    rsqrt_var = 1.0 / tl.sqrt(var + eps)

    # 4. 加权写回
    w = tl.load(W_ptr + cols, mask=mask, other=0.0).to(tl.float32)
    norm_val = val_fp32 * rsqrt_var * w
    tl.store(Out_ptr + row_idx * stride_om + cols * stride_on, norm_val.to(x.dtype), mask=mask)

def fused_rms_norm(x: torch.Tensor, weight: torch.Tensor, eps: float = 1e-6) -> torch.Tensor:
    """标准单输入 RMSNorm 接口（无 residual），支持 2D/3D 任意输入形状"""
    orig_shape = x.shape
    N = orig_shape[-1]
    M = x.numel() // N
    x_2d = x.contiguous().view(M, N)
    out_2d = torch.empty_like(x_2d)

    BLOCK_N = triton.next_power_of_2(N)
    _rms_norm_kernel[(M,)](
        x_2d, x_2d, weight, out_2d, out_2d,
        x_2d.stride(0), x_2d.stride(1),
        0, 0,
        out_2d.stride(0), out_2d.stride(1),
        0, 0,
        N, eps,
        HAS_RESIDUAL=False,
        BLOCK_N=BLOCK_N
    )
    return out_2d.view(orig_shape)

def fused_rms_norm_residual(
    x: torch.Tensor,
    residual: torch.Tensor,
    weight: torch.Tensor,
    eps: float = 1e-6
) -> tuple:
    """带残差融合的 RMSNorm 接口，返回 (normalized_out, new_residual)，支持 2D/3D 输入形状"""
    orig_shape = x.shape
    N = orig_shape[-1]
    M = x.numel() // N

    x_2d = x.contiguous().view(M, N)
    res_2d = residual.contiguous().view(M, N)

    out_2d = torch.empty_like(x_2d)
    res_out_2d = torch.empty_like(res_2d)

    BLOCK_N = triton.next_power_of_2(N)
    _rms_norm_kernel[(M,)](
        x_2d, res_2d, weight, out_2d, res_out_2d,
        x_2d.stride(0), x_2d.stride(1),
        res_2d.stride(0), res_2d.stride(1),
        out_2d.stride(0), out_2d.stride(1),
        res_out_2d.stride(0), res_out_2d.stride(1),
        N, eps,
        HAS_RESIDUAL=True,
        BLOCK_N=BLOCK_N
    )
    return out_2d.view(orig_shape), res_out_2d.view(orig_shape)
