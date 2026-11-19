# -*- coding: utf-8 -*-
"""
fused_silu.py
Triton 实现的 SiLU and Mul (SwiGLU 核心激活) 融合算子
减少中间张量写回 HBM 的内存带宽损耗
"""

import torch
import triton
import triton.language as tl

@triton.jit
def _silu_and_mul_kernel(
    Gate_ptr, Up_ptr, Out_ptr,
    N_elements,
    BLOCK_SIZE: tl.constexpr
):
    pid = tl.program_id(0)
    offsets = pid * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
    mask = offsets < N_elements

    gate = tl.load(Gate_ptr + offsets, mask=mask, other=0.0)
    up = tl.load(Up_ptr + offsets, mask=mask, other=0.0)

    # 寄存器级别 FP32 激活计算: silu(gate) = gate * sigmoid(gate)
    gate_fp32 = gate.to(tl.float32)
    up_fp32 = up.to(tl.float32)
    
    silu = gate_fp32 / (1.0 + tl.exp(-gate_fp32))
    out = silu * up_fp32

    tl.store(Out_ptr + offsets, out.to(gate.dtype), mask=mask)

def fused_silu_and_mul(gate: torch.Tensor, up: torch.Tensor) -> torch.Tensor:
    assert gate.shape == up.shape
    out = torch.empty_like(gate)
    n_elements = gate.numel()
    BLOCK_SIZE = 1024
    grid = (triton.cdiv(n_elements, BLOCK_SIZE),)
    _silu_and_mul_kernel[grid](gate, up, out, n_elements, BLOCK_SIZE=BLOCK_SIZE)
    return out
