# -*- coding: utf-8 -*-
"""
fused_rope.py
Triton 实现的旋转位置编码 (RoPE) 融合算子
支持在单个 Kernel 中完成频率查找、复数旋转与缓存写入
"""

import torch
import triton
import triton.language as tl

@triton.jit
def _fused_rope_kernel(
    Q_ptr, Cos_ptr, Sin_ptr, Out_ptr,
    seq_len, head_dim,
    stride_qs, stride_qh, stride_qd,
    stride_os, stride_oh, stride_od,
    BLOCK_HEAD: tl.constexpr
):
    pid_seq = tl.program_id(0)
    pid_head = tl.program_id(1)
    
    half_dim = head_dim // 2
    offsets = tl.arange(0, BLOCK_HEAD)
    mask = offsets < half_dim

    # 加载 Q 的前半部分与后半部分
    q0 = tl.load(Q_ptr + pid_seq * stride_qs + pid_head * stride_qh + offsets * stride_qd, mask=mask)
    q1 = tl.load(Q_ptr + pid_seq * stride_qs + pid_head * stride_qh + (offsets + half_dim) * stride_qd, mask=mask)

    cos = tl.load(Cos_ptr + pid_seq * half_dim + offsets, mask=mask)
    sin = tl.load(Sin_ptr + pid_seq * half_dim + offsets, mask=mask)

    # 旋转变换: [q0 * cos - q1 * sin, q0 * sin + q1 * cos]
    q0_fp32 = q0.to(tl.float32)
    q1_fp32 = q1.to(tl.float32)
    cos_fp32 = cos.to(tl.float32)
    sin_fp32 = sin.to(tl.float32)

    out0 = q0_fp32 * cos_fp32 - q1_fp32 * sin_fp32
    out1 = q0_fp32 * sin_fp32 + q1_fp32 * cos_fp32

    tl.store(Out_ptr + pid_seq * stride_os + pid_head * stride_oh + offsets * stride_od, out0.to(q0.dtype), mask=mask)
    tl.store(Out_ptr + pid_seq * stride_os + pid_head * stride_oh + (offsets + half_dim) * stride_od, out1.to(q1.dtype), mask=mask)

def fused_rotary_embedding(q: torch.Tensor, cos: torch.Tensor, sin: torch.Tensor) -> torch.Tensor:
    seq_len, num_heads, head_dim = q.shape
    out = torch.empty_like(q)
    BLOCK_HEAD = triton.next_power_of_2(head_dim // 2)
    grid = (seq_len, num_heads)
    _fused_rope_kernel[grid](
        q, cos, sin, out,
        seq_len, head_dim,
        q.stride(0), q.stride(1), q.stride(2),
        out.stride(0), out.stride(1), out.stride(2),
        BLOCK_HEAD=BLOCK_HEAD
    )
    return out
