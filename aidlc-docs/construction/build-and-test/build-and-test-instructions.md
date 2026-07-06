# ビルド・テスト手順書

## ビルド

### 前提条件
- Windows PC（自宅/社内の作業PC。将来Self-hosted Runnerとしても使用）
- Python 3.13系（`.venv`作成時に使用したバージョン）
- SQL Server Express（`.\SQLEXPRESS`）がローカルにインストール済みで、Windows統合認証でアクセス可能なこと
- GitHubリポジトリ（既存のものを使用。まだ接続していない場合は `git init` / `git remote add origin ...` を行う）

### ビルド手順（依存関係のインストール）
```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### ビルド成功の確認
- `pip install` がエラーなく完了すること
- `pyodbc`, `pandas`, `plotly`, `streamlit`, `pytest` が `.venv` にインストールされていること:
  ```powershell
  .venv\Scripts\python.exe -m pip list
  ```

### トラブルシューティング
| 症状 | 対処 |
|---|---|
| `pyodbc` のインストールに失敗する | Microsoft ODBC Driver for SQL Server（17または18）が未インストールの可能性。[Microsoft公式](https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server)からインストールする |
| `streamlit` コマンドが見つからない | `.venv` を有効化(`.venv\Scripts\Activate.ps1`)してから実行するか、`.venv\Scripts\streamlit.exe` を直接指定する |

---

## ユニットテスト

### 実行コマンド
```powershell
.venv\Scripts\python.exe -m pytest tests -v
```

### 期待される結果
- **60件全てPASS**（UOW-1: 14件, UOW-2: 14件, UOW-3: 12件, UOW-4: 13件, UOW-5: 5件, 統合テスト: 2件）
- 実行時間は数秒程度（実DB接続を伴わないため高速）

### 失敗時の対処
1. どのテストが失敗したかログで確認する
2. 該当ユニットの `aidlc-docs/construction/{unit-name}/code/README.md` に記載された既知の制約・バグ修正履歴を確認する
3. 実装コードまたはテストコードの期待値を見直す

---

## 統合テスト

### 目的
UOW-1(CsvGenerator)〜UOW-4(DashboardApp)の間で、CSVフォーマット・型変換・集計結果の受け渡しが正しく機能することを検証する。実際のSSMS接続は行わず、CsvGeneratorの出力をそのまま疑似DBとして扱うことで、実DB環境がなくてもユニット間のデータ整合性を検証できるようにしている。

### テストシナリオ
- `test_csv_generator_output_is_readable_by_db_loader`: UOW-1のCSV出力をUOW-2がそのまま読み込み・型変換できることを確認
- `test_full_pipeline_from_csv_to_dashboard_chart`: UOW-1の生成データを疑似DBとして、UOW-3の稼働率算出・UOW-4のダッシュボード用データ整形・グラフ構築まで一気通貫でデータが流れることを確認

### 実行コマンド
```powershell
.venv\Scripts\python.exe -m pytest tests/integration -v
```

### 検証手順（実SSMS接続を伴う手動確認、初回導入時に実施推奨）
1. SSMSで `Equipment_Utilization_Rate` データベースを作成する（未作成の場合）
2. `.venv\Scripts\python.exe src\scheduling\run_ingestion.py` を実行し、CSV生成→SSMS取り込みが正常終了(exit code 0)することを確認する
3. SSMSで `[dbo].[A1_ProcessingMachine_Utilization_Rate]` テーブルおよびインデックス（`IX_A1_ProductNumber_MachineNumber`, `IX_A1_MachineName_StartTime`）が作成されていることを確認する
4. `.venv\Scripts\python.exe src\scheduling\run_reporting_refresh.py` を実行し、正常終了することを確認する
5. `.venv\Scripts\streamlit.exe run src\dashboard\app.py` を実行し、ブラウザでダッシュボードが表示され、投入したデータに応じたグラフが描画されることを確認する

### クリーンアップ
- テスト実行で作成された `.venv`, `.pytest_cache`, `__pycache__` はGitに含めない（`.gitignore` で除外済み）
- 手動確認で投入したテストデータをSSMSから削除したい場合は、`DELETE FROM [dbo].[A1_ProcessingMachine_Utilization_Rate]` を実行する
