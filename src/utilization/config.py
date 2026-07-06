"""UtilizationCalculatorの設定値。"""
from __future__ import annotations

DB_SERVER = r".\SQLEXPRESS"
DB_DATABASE = "Equipment_Utilization_Rate"

ODBC_DRIVER_CANDIDATES = [
    "ODBC Driver 18 for SQL Server",
    "ODBC Driver 17 for SQL Server",
    "SQL Server",
]

TABLE_NAME = "[dbo].[A1_ProcessingMachine_Utilization_Rate]"

MACHINE_TYPES = ["A", "B", "C", "D", "E"]
UNIT_NUMBERS = [1, 2, 3, 4, 5]

STANDARD_MINUTES = {
    "A": 20,
    "B": 30,
    "C": 40,
    "D": 25,
    "E": 15,
}

DAY_SECONDS = 86400
MONDAY_NON_WORKING_SECONDS = 9 * 3600
