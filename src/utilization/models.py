"""ドメインエンティティ定義(functional-design/domain-entities.md 対応)。"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class UtilizationRow:
    """号機単位・日別/月別の稼働率行(実績+想定)。"""

    machine_name: str
    machine_number: int
    actual_seconds: int
    planned_seconds: int
    utilization_rate: float
    processed_count: int
    expected_utilization_rate: float


@dataclass
class WeeklyUtilizationRow:
    """号機単位・週別の稼働率行(実績+想定)。"""

    machine_name: str
    machine_number: int
    actual_seconds: int
    planned_seconds: int
    processed_count: int
    actual_utilization_rate: float
    expected_utilization_rate: float


@dataclass
class MachineTypeUtilizationRow:
    """加工機タイプ単位(5号機合算)・日別/月別の稼働率行(BR-8)。"""

    machine_name: str
    actual_seconds: int
    planned_seconds: int
    utilization_rate: float
    processed_count: int
    expected_utilization_rate: float


@dataclass
class MachineTypeWeeklyUtilizationRow:
    """加工機タイプ単位(5号機合算)・週別の稼働率行(BR-8)。"""

    machine_name: str
    actual_seconds: int
    planned_seconds: int
    processed_count: int
    actual_utilization_rate: float
    expected_utilization_rate: float
