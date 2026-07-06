"""ドメインエンティティ定義(functional-design/domain-entities.md 対応)。"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ExecutionWindow:
    """1回のGitHub Actions実行(12時間ごと)が対象とする時間帯。"""

    window_start: datetime
    window_end: datetime
    is_holiday: bool
    available_seconds: int
    earliest_start: datetime  # 非稼働時間(月曜0-9時等)を除いた、この窓内で最初に加工を開始できる時刻


@dataclass
class ProcessingRecord:
    """CSVの1行・DBの1レコードに対応する加工実績。"""

    product_number: str
    machine_name: str
    machine_number: int
    processing_start_time: datetime
    processing_completion_time: datetime
    sum_datetime: int
    pass_judgment: str


@dataclass
class ProductChain:
    """1製品がA→B→C→D→Eの5工程を通過する一連の処理。"""

    base_product_id: str
    stages: list[ProcessingRecord] = field(default_factory=list)

    @property
    def is_completed(self) -> bool:
        return len(self.stages) == 5
