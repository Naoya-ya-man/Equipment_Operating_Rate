"""CSV疑似データ生成の設定値(BR-1〜BR-10で参照するパラメータ)。"""
from __future__ import annotations

MACHINE_TYPES = ["A", "B", "C", "D", "E"]

STANDARD_MINUTES = {
    "A": 20,
    "B": 30,
    "C": 40,
    "D": 25,
    "E": 15,
}

BOTTLENECK_MACHINE = "C"

UNIT_NUMBERS = [1, 2, 3, 4, 5]

# 休憩時間帯 (start_hour, start_minute, end_hour, end_minute)
BREAK_WINDOWS = [
    (10, 0, 10, 20),
    (12, 15, 13, 15),
    (15, 0, 15, 15),
    (18, 0, 18, 45),
    (21, 0, 21, 15),
    (2, 0, 2, 45),
    (5, 0, 5, 15),
]

MONDAY_NON_WORKING_END_HOUR = 9  # 月曜 0:00-9:00 は非稼働

NG_RATE = 0.03
BREAKDOWN_RATE = 0.01
BREAKDOWN_MULTIPLIER_RANGE = (2.0, 3.0)
PROCESSING_TIME_JITTER_MINUTES = 10  # 標準加工時間 ±10分

SAFETY_MARGIN_SECONDS = 300  # チェーン開始可否判定の安全マージン
CAPACITY_LOWER_BOUND_RATIO = 0.6  # 実際の生成数の下限(理論上限に対する比率)

CSV_COLUMNS = [
    "Product_Number",
    "Machine_Name",
    "Machine_Number",
    "Processing_Start_Time",
    "Processing_Completion_Time",
    "Sum_DateTime",
    "Pass_judgment",
]

OUTPUT_DIR_NAME = "データ転送前"
OUTPUT_FILE_NAME = "A1_ProcessingMachine_Utilization_Rate.csv"
