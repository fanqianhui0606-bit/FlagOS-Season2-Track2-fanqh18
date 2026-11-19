#!/usr/bin/env bash
# ==============================================================================
# FlagOS 赛道二：端到端推理吞吐基准自动化评测脚本 (带执行护栏与消融开关)
# 模型: OpenBMB/MiniCPM5-2B
# 硬件支持: Iluvatar CoreX BI-V150 / MetaX 曦云 C500 64GB
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEVICE=${1:-"bi150"} # bi150 或 c500
SCENARIO=${2:-"all"}  # 4k, 16k 或 all
MODEL_PATH=${MODEL_PATH:-"openbmb/MiniCPM5-2B"}

echo "=== [1/3] 载入硬件架构特定配置 ==="
if [ "$DEVICE" == "bi150" ]; then
    echo ">> 当前评测设备: 天数智芯 (Iluvatar CoreX BI-V150)"
    CONFIG_FILE="${SCRIPT_DIR}/benchmark/config/iluvatar_bi150.env"
elif [ "$DEVICE" == "c500" ]; then
    echo ">> 当前评测设备: 沐曦 (MetaX 曦云 C500 64GB)"
    CONFIG_FILE="${SCRIPT_DIR}/benchmark/config/metax_c500.env"
else
    echo "错误: 未知硬件架构: $DEVICE (支持 bi150 / c500)"
    exit 1
fi

if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
    echo ">> 已加载配置: $CONFIG_FILE"
fi

# 核心框架插件与算子环境变量
export VLLM_PLUGINS='fl'

# 消融实验开关默认值 (可通过环境变量覆盖)
export FLAGOS_ENABLE_METADATA_CACHE=${FLAGOS_ENABLE_METADATA_CACHE:-1}
export FLAGOS_ENABLE_FUSED_RMSNORM=${FLAGOS_ENABLE_FUSED_RMSNORM:-1}
export FLAGOS_ENABLE_GRAPH_CAPTURE=${FLAGOS_ENABLE_GRAPH_CAPTURE:-1}

echo "=== [2/3] 当前优化特性开关 (消融配置) ==="
echo "  FLAGOS_ENABLE_METADATA_CACHE : $FLAGOS_ENABLE_METADATA_CACHE"
echo "  FLAGOS_ENABLE_FUSED_RMSNORM  : $FLAGOS_ENABLE_FUSED_RMSNORM"
echo "  FLAGOS_ENABLE_GRAPH_CAPTURE  : $FLAGOS_ENABLE_GRAPH_CAPTURE"

LOG_DIR="${SCRIPT_DIR}/logs_and_artifacts/${DEVICE}"
mkdir -p "$LOG_DIR"

# ==============================================================================
# 评测场景 1: 4K 场景 (input=4096, output=1024, concurrency=64, num_prompts=256)
# ==============================================================================
run_4k() {
    echo "------------------------------------------------------------------"
    echo ">>> 开始执行 4K 场景基准评测..."
    echo "  [官方严格参数] input=4096, output=1024, concurrency=64, prompts=256"
    echo "------------------------------------------------------------------"
    
    # 4K 显存安全，允许完整启用 Graph Capture
    export VLLM_GRAPH_CAPTURE_MAX_BATCH_SIZE=64
    
    python3 "${SCRIPT_DIR}/benchmark/benchmark_throughput.py" \
        --model "$MODEL_PATH" \
        --input-len 4096 \
        --output-len 1024 \
        --concurrency 64 \
        --num-prompts 256 \
        2>&1 | tee "${LOG_DIR}/4k_throughput_$(date +%Y%m%d_%H%M%S).log"
}

# ==============================================================================
# 评测场景 2: 16K 场景 (input=16384, output=1024, concurrency=64, num_prompts=128)
# ==============================================================================
run_16k() {
    echo "------------------------------------------------------------------"
    echo ">>> 开始执行 16K 场景基准评测..."
    echo "  [官方严格参数] input=16384, output=1024, concurrency=64, prompts=128"
    echo "------------------------------------------------------------------"
    
    # 16K 超长上下文显存保护: 限制 Graph 捕获批大小，严防 64GB 显存 OOM
    export VLLM_GRAPH_CAPTURE_MAX_BATCH_SIZE=16
    
    python3 "${SCRIPT_DIR}/benchmark/benchmark_throughput.py" \
        --model "$MODEL_PATH" \
        --input-len 16384 \
        --output-len 1024 \
        --concurrency 64 \
        --num-prompts 128 \
        2>&1 | tee "${LOG_DIR}/16k_throughput_$(date +%Y%m%d_%H%M%S).log"
}

echo "=== [3/3] 启动跑测 ==="
case $SCENARIO in
    4k)
        run_4k
        ;;
    16k)
        run_16k
        ;;
    all)
        run_4k
        run_16k
        ;;
    *)
        echo "未知评测场景: $SCENARIO (支持 4k, 16k, all)"
        exit 1
        ;;
esac

echo "=== 评测完成，日志已存入: $LOG_DIR ==="
