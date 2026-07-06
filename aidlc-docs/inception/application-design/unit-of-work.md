# 作業ユニット定義（Unit of Work）

> 本プロジェクトはモノリス構成（単一Pythonコードベース + Streamlitアプリ）。各ユニットはApplication Designで定義したコンポーネントと1対1で対応する論理モジュールとして扱う。

## UOW-1: CsvGenerator（CSV疑似データ生成）
- **目的**: A→B→C→D→Eの生産フローに沿った疑似データCSVを生成する（FR-1）
- **含まれるコンポーネント/モジュール**: `CsvGenerator`
- **依存関係**: なし（他ユニットに依存しない、最初に着手可能）

## UOW-2: DbLoader（SSMSスキーマ・DB取り込み）
- **目的**: SSMSテーブル・インデックスのセットアップ、CSVの型変換・MERGE取り込み、ファイル移動（FR-2）
- **含まれるコンポーネント/モジュール**: `DbLoader`、DBスキーマ定義（DDL: テーブル作成・インデックス作成）
- **依存関係**: UOW-1が定義するCSVフォーマットに依存

## UOW-3: UtilizationCalculator（稼働率算出エンジン）
- **目的**: 日別/週別/週間想定/月別の稼働率を算出する（FR-3）
- **含まれるコンポーネント/モジュール**: `UtilizationCalculator`
- **依存関係**: UOW-2で確定するDBスキーマ・データに依存（開発自体はモックデータで先行着手可能）

## UOW-4: DashboardApp（Streamlit WEBダッシュボード）
- **目的**: 稼働率データをBIツール風に可視化する（FR-4）
- **含まれるコンポーネント/モジュール**: `DashboardApp`
- **依存関係**: UOW-3が返すデータ形式に依存（UI自体はモックデータで先行着手可能）

## UOW-5: SchedulingOrchestration（定期実行基盤）
- **目的**: GitHub Actions（Self-hosted Runner）による12時間毎の自動実行を構成する（FR-5）
- **含まれるコンポーネント/モジュール**: `SchedulingOrchestration`、`.github/workflows/*.yml`
- **依存関係**: UOW-1, UOW-2, UOW-3のCLIエントリーポイントが揃っていることが前提（最後に統合）

## コード organization戦略（Greenfield）

```
<workspace-root>/
├── src/
│   ├── csv_generator/
│   │   ├── __init__.py
│   │   └── generator.py          (UOW-1)
│   ├── db_loader/
│   │   ├── __init__.py
│   │   ├── schema.sql            (UOW-2: テーブル/インデックスDDL)
│   │   └── loader.py             (UOW-2)
│   ├── utilization/
│   │   ├── __init__.py
│   │   └── calculator.py         (UOW-3)
│   ├── dashboard/
│   │   ├── __init__.py
│   │   └── app.py                (UOW-4: Streamlitエントリーポイント)
│   └── scheduling/
│       ├── run_ingestion.py      (UOW-5: スクリプト①)
│       └── run_reporting_refresh.py (UOW-5: スクリプト②)
├── tests/
│   ├── test_csv_generator.py
│   ├── test_db_loader.py
│   └── test_utilization.py
├── .github/
│   └── workflows/
│       └── scheduled-pipeline.yml  (UOW-5)
├── requirements.txt
├── データ転送前/    （既存）
├── データ転送後/    （既存）
└── エラー項目/      （既存）
```
