# コンポーネント依存関係（Component Dependency）

## 依存関係マトリクス

| コンポーネント | 依存先 | 依存の種類 |
|---|---|---|
| CsvGenerator | なし | 独立（純粋なデータ生成） |
| DbLoader | CsvGenerator（ファイル経由）, SSMS DB | ファイルシステム / DB接続 |
| UtilizationCalculator | SSMS DB | DB接続（読み取り専用クエリ） |
| DashboardApp | UtilizationCalculator | 関数呼び出し（同一プロセス内） |
| SchedulingOrchestration | CsvGenerator, DbLoader, UtilizationCalculator | エントリーポイント呼び出し（スケジュール実行） |

## データフロー図（ASCII）

```
+----------------+     CSV      +------------------+
|  CsvGenerator  | -----------> | データ転送前/     |
+----------------+              +------------------+
                                          |
                                          v
                                 +------------------+
                                 |     DbLoader      |
                                 +------------------+
                                   |             |
                              成功  |             | 失敗
                                   v             v
                       +----------------+  +----------------+
                       | データ転送後/   |  | エラー項目/     |
                       +----------------+  +----------------+
                                   |
                                   v (MERGE)
                          +------------------+
                          |     SSMS DB      |
                          +------------------+
                                   ^
                                   | クエリ（読み取り）
                          +------------------------+
                          | UtilizationCalculator  |
                          +------------------------+
                                   |
                                   v
                          +------------------+
                          |   DashboardApp   |
                          +------------------+
                                   |
                                   v
                          +------------------+
                          |  ブラウザ(ユーザー)|
                          +------------------+

+-------------------------------------------------+
| SchedulingOrchestration (Self-hosted Runner,     |
| 12時間毎)                                          |
| 1. CsvGenerator -> DbLoader を実行                |
| 2. UtilizationCalculator の更新処理を実行(補助)    |
+-------------------------------------------------+
```

## 通信パターン
- CsvGenerator → DbLoader: ファイルシステム経由（CSV読み書き）。プロセス間の直接呼び出しは行わない
- DbLoader ⇄ SSMS: `pyodbc` 等のDBドライバ経由の同期SQL実行（MERGE文）
- UtilizationCalculator ⇄ SSMS: 同期SQLクエリ（SELECT）
- DashboardApp ⇄ UtilizationCalculator: 同一Pythonプロセス内の関数呼び出し（Streamlitアプリ内でインポートして使用）
- SchedulingOrchestration → 各コンポーネント: CLIエントリーポイント（`python -m ...`）としてGitHub Actionsのステップから呼び出し
