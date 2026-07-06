"""CsvGenerator (UOW-1): 設備稼働率監視ボード向け疑似データCSV生成モジュール。"""
from .generator import generate_daily_csv

__all__ = ["generate_daily_csv"]
