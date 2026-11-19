#!/usr/bin/env bash
# ==============================================================================
# FlagOS 赛道二：一票否决精度门禁校验脚本 (evalscope / math_500 Level 3)
# 模型: OpenBMB/MiniCPM5-2B
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEVICE=${1:-"bi150"} # bi150 或 c500
MODEL_PATH=${MODEL_PATH:-"openbmb/MiniCPM5-2B"}

echo "=== [1/2] 精度门禁初始化 (硬件: $DEVICE) ==="

if [ "$DEVICE" == "bi150" ]; then
    CONFIG_FILE="${SCRIPT_DIR}/benchmark/config/iluvatar_bi150.env"
elif [ "$DEVICE" == "c500" ]; then
    CONFIG_FILE="${SCRIPT_DIR}/benchmark/config/metax_c500.env"
fi

if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
fi

export VLLM_PLUGINS='fl'

LOG_DIR="${SCRIPT_DIR}/logs_and_artifacts/${DEVICE}"
mkdir -p "$LOG_DIR"
ACCURACY_LOG="${LOG_DIR}/math500_accuracy_$(date +%Y%m%d_%H%M%S).log"

echo "=== [2/2] 启动 math_500 Level 3 评测 ==="
echo ">> 正在验证模型输出一致性与数学推理精确匹配率..."

python3 "${SCRIPT_DIR}/benchmark/eval_math500.py" \
    --model "$MODEL_PATH" \
    --dataset "math_500" \
    --level 3 \
    2>&1 | tee "$ACCURACY_LOG"

RET_CODE=${PIPESTATUS[0]}

if [ $RET_CODE -eq 0 ]; then
    echo "=================================================================="
    echo "  [PASS] 精度门禁测试通过！输出结果符合官方 Baseline 口径。"
    echo "  日志详情保存在: $ACCURACY_LOG"
    echo "=================================================================="
    exit 0
else
    echo "=================================================================="
    echo "  [FAIL] 警告：精度门禁测试失败 (Exit Code: $RET_CODE)！"
    echo "  根据官方规则，未通过正确性测试将被判定为无效提交 (0 分)。"
    echo "  请立即检查融合算子中是否保留了 FP32 累加精度，或回退最新算子修改！"
    echo "=================================================================="
    exit $RET_CODE
fi
