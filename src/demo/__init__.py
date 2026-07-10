"""ポートフォリオ公開用デモパッケージ。

実際のSSMSには一切接続せず、`CsvGenerator`のロジックで生成した疑似データを
SQLiteファイル(`demo_data.db`)に保存し、それを参照するダッシュボードを提供する。
Streamlit Community Cloud等、外部のクラウド環境に公開することを想定している。
"""
