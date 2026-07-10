"""SSMSへのDB接続(Windows統合認証、ODBCドライバのフォールバック)。"""
from __future__ import annotations

from typing import TYPE_CHECKING

from .config import DB_DATABASE, DB_SERVER, ODBC_DRIVER_CANDIDATES

if TYPE_CHECKING:
    import pyodbc


def get_connection() -> "pyodbc.Connection":
    """ODBCドライバ候補を順に試行し、最初に成功した接続を返す。

    `pyodbc`はこの関数の呼び出し時にのみimportする(理由は`src/db_loader/connection.py`と同様。
    ポートフォリオデモ(`src/demo/`)が`utilization.calculator`の集計ロジックのみを再利用する際、
    実DB接続が不要にもかかわらずpyodbcの読み込みで失敗することを防ぐ)。
    """
    import pyodbc

    last_error: Exception | None = None

    for driver in ODBC_DRIVER_CANDIDATES:
        connection_string = (
            f"Driver={{{driver}}};"
            f"Server={DB_SERVER};"
            f"Database={DB_DATABASE};"
            "Trusted_Connection=yes;"
        )
        try:
            return pyodbc.connect(connection_string)
        except pyodbc.Error as exc:
            last_error = exc
            continue

    raise ConnectionError(
        f"SSMSへの接続に失敗しました(試行したドライバ: {ODBC_DRIVER_CANDIDATES}): {last_error}"
    ) from last_error
