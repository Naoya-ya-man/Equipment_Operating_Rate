# ビジネスロジックモデル（UOW-2: DbLoader）

## 全体ワークフロー

```
1. データ転送前/ のCSVファイル一覧を取得（ファイル名昇順） (BR-8)

2. 各CSVファイルについて:
   a. CSVを読み込み、DbRecordのリストに型変換する (BR-4)
   b. DB接続を確立する（ODBCドライバをフォールバックしながら試行） (BR-1)
   c. テーブル・インデックスの存在を確認し、なければ作成する (BR-2, BR-3)
   d. 各DbRecordについてMERGE文を実行する (BR-5)
   e. 全件成功したらコミットし、CSVを データ転送後/ に移動する (BR-6)
   f. 途中で例外が発生したらロールバックし、CSVを エラー項目/ に移動する (BR-6)
   g. LoadResult（成功可否・行数・エラー内容）を記録する

3. 全ファイルのLoadResultのリストを返す
```

## 入出力
- **入力**: `データ転送前/` 配下のCSVファイル（0件以上）
- **出力**: SSMS `[dbo].[A1_ProcessingMachine_Utilization_Rate]` テーブルへのMERGE結果、`データ転送後/` または `エラー項目/` へのファイル移動、`LoadResult` のリスト

## MERGE文の構造
```sql
MERGE [dbo].[A1_ProcessingMachine_Utilization_Rate] AS target
USING (SELECT ? AS Product_Number, ? AS Machine_Number) AS source
ON target.Product_Number = source.Product_Number
   AND target.Machine_Number = source.Machine_Number
WHEN NOT MATCHED THEN
    INSERT (Product_Number, Machine_Name, Machine_Number,
            Processing_Start_Time, Processing_Completion_Time,
            Sum_DateTime, Pass_judgment)
    VALUES (?, ?, ?, ?, ?, ?, ?);
```

## エラーハンドリング・エッジケース
- **接続失敗**（全ドライバ候補で失敗）: そのファイルを エラー項目/ に移動し、`LoadResult.error_message` に接続エラーの内容を記録
- **CSVのカラム構成不正**: 読み込み時点でエラーとし、DB接続前にエラー項目/へ移動
- **0件データのCSV**: 正常系として扱い、テーブル・インデックスの存在確認のみ行いデータ転送後/へ移動
- **`データ転送前/` が空 or 存在しない**: 何もせず空のLoadResultリストを返す（エラーにしない）
