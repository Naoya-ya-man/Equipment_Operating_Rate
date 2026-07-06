"""製品チェーン生成ロジック(BR-5, BR-6, BR-7, BR-8, BR-9, BR-10)。"""
from __future__ import annotations

import random
from datetime import datetime, timedelta

from .calendar_utils import is_within_break_time
from .config import (
    BREAKDOWN_MULTIPLIER_RANGE,
    BREAKDOWN_RATE,
    MACHINE_TYPES,
    NG_RATE,
    PROCESSING_TIME_JITTER_MINUTES,
    SAFETY_MARGIN_SECONDS,
    STANDARD_MINUTES,
    UNIT_NUMBERS,
)
from .models import ExecutionWindow, ProcessingRecord, ProductChain

TOTAL_STANDARD_SECONDS = sum(STANDARD_MINUTES[m] * 60 for m in MACHINE_TYPES)
MIN_PROCESSING_SECONDS = 60


class UnitAssignmentTracker:
    """加工機タイプごとに号機(1〜5)の割当回数を管理し、均等配分する(BR-9)。"""

    def __init__(self) -> None:
        self._counts = {machine: {unit: 0 for unit in UNIT_NUMBERS} for machine in MACHINE_TYPES}

    def assign_unit(self, machine_name: str) -> int:
        counts = self._counts[machine_name]
        min_count = min(counts.values())
        candidates = [unit for unit, count in counts.items() if count == min_count]
        chosen = random.choice(candidates)
        counts[chosen] += 1
        return chosen


def generate_product_chains(window: ExecutionWindow, target_chain_count: int) -> list[ProductChain]:
    """理論上限内でtarget_chain_count件を上限にProductChainを生成する。

    実行窓をまたぐチェーンは生成しない(BR-6): 残り時間が
    標準加工時間合計+安全マージンに満たない場合は生成を打ち切る。
    """
    chains: list[ProductChain] = []
    if target_chain_count <= 0 or window.is_holiday:
        return chains

    tracker = UnitAssignmentTracker()
    cursor = window.earliest_start
    sequence = 0

    while len(chains) < target_chain_count:
        cursor = _advance_past_break_time(cursor, window.window_end)
        remaining_seconds = (window.window_end - cursor).total_seconds()

        if remaining_seconds < TOTAL_STANDARD_SECONDS + SAFETY_MARGIN_SECONDS:
            break  # BR-6: 残り時間不足のため、この窓でのチェーン生成を終了する

        sequence += 1
        base_product_id = _generate_base_product_id(window.window_start, sequence)
        chain, cursor = _build_chain(base_product_id, cursor, window.window_end, tracker)
        chains.append(chain)

    return chains


def _build_chain(
    base_product_id: str,
    start_cursor: datetime,
    window_end: datetime,
    tracker: UnitAssignmentTracker,
) -> tuple[ProductChain, datetime]:
    chain = ProductChain(base_product_id=base_product_id)
    cursor = start_cursor

    for machine_name in MACHINE_TYPES:
        cursor = _advance_past_break_time(cursor, window_end)

        duration_seconds = _draw_processing_duration(machine_name)
        completion = cursor + timedelta(seconds=duration_seconds)

        if completion > window_end:
            # BR-7: 設備停止等で窓を超える場合は残り時間にクリップする
            completion = window_end
            duration_seconds = max(int((completion - cursor).total_seconds()), 1)

        unit_number = tracker.assign_unit(machine_name)
        record = ProcessingRecord(
            product_number=f"{base_product_id}{machine_name}",
            machine_name=machine_name,
            machine_number=unit_number,
            processing_start_time=cursor,
            processing_completion_time=completion,
            sum_datetime=duration_seconds,
            pass_judgment="NG" if random.random() < NG_RATE else "OK",
        )
        chain.stages.append(record)
        cursor = completion

    return chain, cursor


def _draw_processing_duration(machine_name: str) -> int:
    """標準加工時間 ±10分のランダム変動、および低確率の設備停止相当(2〜3倍)を適用する(BR-7)。"""
    standard_seconds = STANDARD_MINUTES[machine_name] * 60
    jitter_seconds = PROCESSING_TIME_JITTER_MINUTES * 60
    duration = standard_seconds + random.randint(-jitter_seconds, jitter_seconds)
    duration = max(duration, MIN_PROCESSING_SECONDS)

    if random.random() < BREAKDOWN_RATE:
        multiplier = random.uniform(*BREAKDOWN_MULTIPLIER_RANGE)
        duration = int(duration * multiplier)

    return duration


def _advance_past_break_time(moment: datetime, window_end: datetime) -> datetime:
    """momentが休憩時間帯に入っている場合、休憩終了時刻まで進める。"""
    while moment < window_end and is_within_break_time(moment):
        moment += timedelta(minutes=1)
    return min(moment, window_end)


def _generate_base_product_id(window_start: datetime, sequence: int) -> str:
    """6桁の品番ベースを採番する(BR-10)。年間通日+実行窓内の連番から一意性を持たせる。"""
    day_of_year = window_start.timetuple().tm_yday  # 1〜366
    return f"{day_of_year:03d}{sequence:03d}"
