"""テーブル・インデックスの冪等セットアップ(BR-2)。"""
from __future__ import annotations

import re
from pathlib import Path

SCHEMA_SQL_PATH = Path(__file__).resolve().parent / "schema.sql"

# 行全体がこのパターンに一致する場合のみ区切りとして扱う(コメント文中に同じ文字列が
# 現れても誤って分割されないようにするため、部分一致ではなく行単位で判定する)。
STATEMENT_DELIMITER_PATTERN = re.compile(r"^\s*-- STATEMENT --\s*$", re.MULTILINE)


def ensure_schema(connection) -> None:
    """schema.sqlに定義されたテーブル・インデックスが存在しなければ作成する。"""
    statements = _load_statements()
    cursor = connection.cursor()
    for statement in statements:
        cursor.execute(statement)
    connection.commit()


def _load_statements() -> list[str]:
    sql_text = SCHEMA_SQL_PATH.read_text(encoding="utf-8")
    # 先頭の区切り行より前のプリアンブル(ファイル冒頭の説明コメント)は文として扱わない
    parts = STATEMENT_DELIMITER_PATTERN.split(sql_text)[1:]
    return [s.strip() for s in parts if s.strip()]
