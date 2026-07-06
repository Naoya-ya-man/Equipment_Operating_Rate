# ビジネスルール（UOW-2: DbLoader）

## BR-1: DB接続（Windows統合認証）
- `requirements.md` の決定に従い、Windows統合認証（Trusted Connection）で接続する。ユーザー名・パスワードは不要
- 接続先: サーバー `.\SQLEXPRESS`、データベース `Equipment_Utilization_Rate`
- ODBCドライバはインストール状況が環境によって異なりうるため、`ODBC Driver 18 for SQL Server` → `ODBC Driver 17 for SQL Server` → `SQL Server` の順にフォールバックして接続を試行する（低リスクな実装上の防御策として、ユーザーへの追加確認は行わない）

## BR-2: テーブル・インデックスの冪等セットアップ
- 初回接続時に、対象テーブルが存在しなければ作成する（`IF NOT EXISTS` によるべき等な作成）
- インデックスも同様に、存在しなければ作成する

## BR-3: インデックス設計（NFR-1対応）
- **一意複合インデックス**: `(Product_Number, Machine_Number)` — MERGE条件のマッチングを高速化し、重複防止のキーとしても機能する
- **副次インデックス**: `(Machine_Name, Processing_Start_Time)` — UOW-3（稼働率算出）が号機別・期間別に集計する際の参照負荷を軽減する

## BR-4: 型変換ルール
- `Machine_Number`: CSV上はint(1〜5)だが、DBカラム定義がVARCHAR(50)のため文字列に変換する
- `Processing_Start_Time` / `Processing_Completion_Time`: CSVの `"%Y-%m-%d %H:%M:%S"` 形式文字列をdatetime型にパースする
- `Sum_DateTime`: CSV上の文字列をintに変換する
- その他カラムはそのまま文字列として扱う

## BR-5: MERGE条件（重複防止）
- `Product_Number` + `Machine_Number` の組み合わせで既存行の有無を判定する
- 一致する行が存在しない場合のみ INSERT する（`WHEN NOT MATCHED THEN INSERT`）。既存の場合は何もしない

## BR-6: ファイル単位のトランザクション・成否判定
- 1ファイルの取り込みは1つのDBトランザクションとして扱う
- 全行のMERGEが成功した場合のみコミットし、CSVファイルを `データ転送後/` に移動する
- 途中で例外が発生した場合はロールバックし、CSVファイルを `エラー項目/` に移動する（部分的な取り込みは残さない）

## BR-7: 空CSV・0件データの扱い
- ヘッダーのみ（0件データ）のCSVも正常な取り込みとして扱い、`データ転送後/` に移動する（日曜日等でCsvGeneratorがファイル自体を生成しなかった場合は対象外）

## BR-8: 複数ファイルの処理順序
- `データ転送前/` に複数のCSVファイルが存在する場合、ファイル名の昇順で1件ずつ処理する
- 1ファイルの失敗が他のファイルの処理に影響しないようにする（ファイル単位で独立して成否を判定する）
