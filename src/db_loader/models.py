"""ドメインエンティティ定義(functional-design/domain-entities.md 対応)。"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class DbRecord:
    """SSMSカラム型に型変換済みの1レコード。"""

    product_number: str
    machine_name: str
    machine_number: str
    processing_start_time: datetime
    processing_completion_time: datetime
    sum_datetime: int
    pass_judgment: str


@dataclass
class LoadResult:
    """1CSVファイルあたりの取り込み結果。"""

    file_path: Path
    success: bool
    row_count: int
    error_message: Optional[str] = None
