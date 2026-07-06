# ユニット・要件マッピング（Unit of Work Story Map）

> 本プロジェクトはUser Storiesステージをスキップしたため（単一ユーザー向け社内ツールのため）、ここではStoryの代わりに `requirements.md` の機能要件(FR)番号を各ユニットにマッピングする。

## マッピング表

| ユニット | 対応する機能要件 | カバレッジ |
|---|---|---|
| UOW-1: CsvGenerator | FR-1（CSV疑似データ生成） | ✅ |
| UOW-2: DbLoader | FR-2（CSV → SSMS 取り込み） | ✅ |
| UOW-3: UtilizationCalculator | FR-3（稼働率算出） | ✅ |
| UOW-4: DashboardApp | FR-4（WEB画面表示） | ✅ |
| UOW-5: SchedulingOrchestration | FR-5（定期実行の自動化） | ✅ |

## カバレッジ検証
`requirements.md` に記載された全ての機能要件（FR-1〜FR-5）が、いずれか1つのユニットに過不足なく割り当てられていることを確認済み。

## ユニット内優先順位
各ユニットは単一の機能要件に対応するため、ユニット内でのさらなる優先順位付けは不要。ユニット間の着手順序は `unit-of-work-dependency.md` の推奨構築順序（UOW-1 → UOW-2 → UOW-3 → UOW-4 → UOW-5）に従う。
