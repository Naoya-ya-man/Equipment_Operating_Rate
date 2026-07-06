"""CSV疑似データ生成のエントリーポイント(UOW-1: CsvGenerator)。"""
from __future__ import annotations

import csv
import random
from datetime import datetime
from pathlib import Path
from typing import Optional

from .calendar_utils import resolve_execution_window
from .capacity import compute_window_capacity
from .chain_builder import generate_product_chains
from .config import CAPACITY_LOWER_BOUND_RATIO, CSV_COLUMNS, OUTPUT_DIR_NAME, OUTPUT_FILE_NAME
from .models import ProductChain

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]


def generate_daily_csv(
    reference_time: Optional[datetime] = None,
    workspace_root: Optional[Path] = None,
) -> Optional[Path]:
    """実行時刻を基準に、この実行窓(12時間)分の疑似データCSVを生成する。

    日曜日に該当する実行窓の場合はCSVを生成せず、Noneを返す。
    """
    reference_time = reference_time or datetime.now()
    root = workspace_root or WORKSPACE_ROOT

    window = resolve_execution_window(reference_time)
    if window.is_holiday:
        return None

    target_count = _decide_target_chain_count(window.available_seconds)
    chains = generate_product_chains(window, target_count)

    output_path = root / OUTPUT_DIR_NAME / OUTPUT_FILE_NAME
    _write_csv(chains, output_path)
    return output_path


def _decide_target_chain_count(available_seconds: int) -> int:
    """BR-4: 理論上限を超えない範囲で、故障・不良による実効生産数の低下を見込んでランダム決定する。"""
    capacity = compute_window_capacity(available_seconds)
    if capacity <= 0:
        return 0
    lower_bound = max(int(capacity * CAPACITY_LOWER_BOUND_RATIO), 0)
    if capacity <= lower_bound:
        return capacity
    return random.randint(lower_bound, capacity)


def _write_csv(chains: list[ProductChain], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_COLUMNS)
        for chain in chains:
            for record in chain.stages:
                writer.writerow(
                    [
                        record.product_number,
                        record.machine_name,
                        record.machine_number,
                        record.processing_start_time.strftime("%Y-%m-%d %H:%M:%S"),
                        record.processing_completion_time.strftime("%Y-%m-%d %H:%M:%S"),
                        record.sum_datetime,
                        record.pass_judgment,
                    ]
                )


if __name__ == "__main__":
    generated_path = generate_daily_csv()
    if generated_path is None:
        print("Skipped: 実行窓が日曜日のためCSVを生成しませんでした。")
    else:
        print(f"Generated: {generated_path}")
