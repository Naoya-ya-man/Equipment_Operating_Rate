"""MERGE処理(BR-5: Product_Number + Machine_Number による重複防止)。

実SSMS環境での動作確認の結果、対象テーブルの不良判定列は要件定義書の原文どおり
`Pass judgment`(半角スペース区切り)であることが判明した(コード内部の属性名は
可読性のため`pass_judgment`のまま。SQL上の列参照のみ実際の列名に合わせている)。
"""
from __future__ import annotations

from .config import TABLE_NAME
from .models import DbRecord

MERGE_SQL = f"""
MERGE {TABLE_NAME} AS target
USING (SELECT ? AS Product_Number, ? AS Machine_Number) AS source
ON target.Product_Number = source.Product_Number
   AND target.Machine_Number = source.Machine_Number
WHEN NOT MATCHED THEN
    INSERT (Product_Number, Machine_Name, Machine_Number,
            Processing_Start_Time, Processing_Completion_Time,
            Sum_DateTime, [Pass judgment])
    VALUES (?, ?, ?, ?, ?, ?, ?);
""".strip()


def merge_records(connection, records: list[DbRecord]) -> int:
    """各DbRecordをMERGE文で取り込む。処理した(試行した)件数を返す。"""
    cursor = connection.cursor()
    for record in records:
        cursor.execute(
            MERGE_SQL,
            record.product_number,
            record.machine_number,
            record.product_number,
            record.machine_name,
            record.machine_number,
            record.processing_start_time,
            record.processing_completion_time,
            record.sum_datetime,
            record.pass_judgment,
        )
    return len(records)
