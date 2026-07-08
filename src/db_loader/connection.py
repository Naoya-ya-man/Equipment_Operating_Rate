"""SSMSへのDB接続(BR-1: Windows統合認証、ODBCドライバのフォールバック)。"""
from __future__ import annotations

import pyodbc

from .config import DB_DATABASE, DB_SERVER, ODBC_DRIVER_CANDIDATES


def get_connection() -> pyodbc.Connection:
    """ODBCドライバ候補を順に試行し、最初に成功した接続を返す。"""
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
