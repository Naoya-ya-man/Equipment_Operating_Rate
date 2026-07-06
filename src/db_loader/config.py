"""DbLoaderの設定値(BR-1〜BR-8で参照するパラメータ)。"""
from __future__ import annotations

DB_SERVER = r".\SQLEXPRESS"
DB_DATABASE = "Equipment_Utilization_Rate"

# 環境によってインストール済みODBCドライバが異なるため、順に接続を試行する(BR-1)
ODBC_DRIVER_CANDIDATES = [
    "ODBC Driver 18 for SQL Server",
    "ODBC Driver 17 for SQL Server",
    "SQL Server",
]

TABLE_NAME = "[dbo].[A1_ProcessingMachine_Utilization_Rate]"

CSV_COLUMNS = [
    "Product_Number",
    "Machine_Name",
    "Machine_Number",
    "Processing_Start_Time",
    "Processing_Completion_Time",
    "Sum_DateTime",
    "Pass_judgment",
]

INPUT_DIR_NAME = "データ転送前"
SUCCESS_DIR_NAME = "データ転送後"
ERROR_DIR_NAME = "エラー項目"

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
