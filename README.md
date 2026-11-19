# FlagOS 赛道二：MiniCPM5-2B 推理吞吐性能优化（fanqh18 团队）

[![FlagOS](https://img.shields.io/badge/FlagOS-Season%202-blue.svg)](https://flagos.io)
[![PR](https://img.shields.io/badge/GitHub-PR%20%23778-blue.svg)](https://github.com/flagos-ai/vllm-plugin-FL/pull/778)
[![Model](https://img.shields.io/badge/Model-MiniCPM5--2B-green.svg)](https://modelscope.cn/models/OpenBMB/MiniCPM5-2B)
[![Accuracy](https://img.shields.io/badge/math__500-100%25%20Match-brightgreen.svg)]()
[![Hardware](https://img.shields.io/badge/Hardware-Iluvatar%20BI150%20%7C%20MetaX%20C500-orange.svg)]()

> **队伍名称**：fanqh18  
> **所属单位**：中国科学院数学与系统科学研究院  
> **赛道名称**：赛道二 · MiniCPM5-2B 模型推理吞吐性能优化  
> **官方 PR 链接**：https://github.com/flagos-ai/vllm-plugin-FL/pull/778  
> **核心硬件**：天数智芯（Iluvatar CoreX BI-V150） / 沐曦（MetaX 曦云 C500 64GB）  

---

## 一、 快速一键复现（Quick Start）

评审专家在官方硬件容器中仅需执行以下两步：

```bash
# 1. 自动化环境配置与优化插件源码安装 (耗时约 2 分钟)
bash env_setup.sh

# 2. 一键精度门禁验证 (100% 匹配通过)
bash run_eval_accuracy.sh bi150   # 若在沐曦上测试则替换为 c500

# 3. 一键端到端吞吐评测 (4K + 16K 官方负载跑测并输出指标)
bash run_benchmark.sh bi150 all   # 若在沐曦上测试则替换为 c500
```

---

## 二、 官方基准实测成绩对比

所有测试均在官方固定参数（4K: 4096 in/1024 out/c=64/256 reqs；16K: 16384 in/1024 out/c=64/128 reqs）下重复 3 次取中位数：

| 硬件平台 | 场景 | Baseline 吞吐 (tps) | 优化版吞吐 (tps) | 端到端加速比 | TTFT 降低 | 精度门禁 (math_500) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **天数 BI150** | 4K | 4642.0 | **5752.1** | **+23.91%** | -14.13% | **100% 对齐 (PASS)** |
| **天数 BI150** | 16K | 2852.0 | **3460.5** | **+21.34%** | -12.16% | **100% 对齐 (PASS)** |
| **沐曦 C500** | 4K | 4830.1 | **6030.5** | **+24.85%** | -15.19% | **100% 对齐 (PASS)** |
| **沐曦 C500** | 16K | 2960.0 | **3635.2** | **+22.81%** | -13.12% | **100% 对齐 (PASS)** |

---

## 三、 系统架构与关键优化技术

```
[Layer 1: 业务负载层] 4K (4096 in/1024 out) & 16K (16384 in/1024 out) @ Concurrency=64
       │
[Layer 2: 调度与框架层] vllm-plugin-FL 静态元数据缓存 + 异步 H2D 流水，消除调度空泡
       │
[Layer 3: 显存与 KV 层] 轻量化 Block 状态机 + 16K 场景自适应 Graph Capture 水线 (防 64GB OOM)
       │
[Layer 4: 算子计算层] FlagGems 高保真融合算子 (RMSNorm+Residual / SiLU / RoPE 强制 FP32 累加)
```

1. **零开销跨芯片解耦**：上层逻辑统一，硬件差异通过 `benchmark/config/iluvatar_bi150.env` 与 `metax_c500.env` 隔离，模块化即插即用；
2. **高保真算子融合**：归约求和强制在寄存器内使用 `tl.float32`，算子最大绝对误差控制在 FP32 核心 $\le 1.19 \times 10^{-7}$ / BF16 写回 $\le 7.8125 \times 10^{-3}$ (1 ULP)，杜绝多步自回归精度分叉；
3. **16K 显存安全保护**：4K 满血开启 Graph Capture；16K 动态限制批上限，防止 64GB 显存发生 OOM。

---

## 四、 交付目录结构说明

```text
fanqh18/
├── README.md                      # 本说明文档
├── report.pdf / report_draft.md   # 核心技术报告 (含 Roofline 模型、消融实验与理论证明)
├── requirements.txt               # 精确锁定的 Python 依赖
├── env_setup.sh                   # 自动化依赖与插件源码安装
├── run_benchmark.sh               # 一键端到端吞吐评测入口
├── run_eval_accuracy.sh           # 一键 math_500 Level 3 精度验证
├── build_package.py               # 交付包生成与卫生审计工具
│
├── src/                           # 优化源代码
│   ├── vllm-plugin-FL/            # 针对官方 flagos-2026-s2 分支的修改
│   ├── flag_gems/                 # FlagGems 优化算子实现
│   └── diff/optimization.patch    # Git Patch 补丁文件
│
├── benchmark/                     # 评测配置与执行脚本
│   ├── config/                    # 双芯片专属环境变量 (iluvatar_bi150.env, metax_c500.env)
│   ├── benchmark_throughput.py    # 吞吐量压测入口
│   └── eval_math500.py            # 精度门禁入口
│
└── logs_and_artifacts/            # 官方硬件实测日志与消融数据
    ├── iluvatar/                  # 天数 BI150 运行日志 (4K / 16K / math500)
    ├── metax/                     # 沐曦 C500 运行日志 (4K / 16K / math500)
    └── ablation/                  # 逐项消融实验数据
```

---

## 五、 合规性声明

本队伍严格遵守大赛一切评测规则与道德底线：
* 未修改 `vllm serve` 外部 CLI 任何启动参数；
* 未使用任何形式的有损量化或投机采样；
* 未篡改 benchmark 评测脚本或注入任何针对测试 prompt 的硬编码逻辑；
* 所有性能提升均来自于真实的系统工程优化与算子融合，数据真实、完整、可 100% 复现。
