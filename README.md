# 設備稼働率監視ボード (Equipment Operating Rate Dashboard)

製造業の加工設備（5種類 × 各5号機、計25台）の稼働データを自動収集し、日別・週別・月別の稼働率をWebダッシュボードで可視化するシステムです。データ生成からDB取り込み、可視化、定期実行までを完全に自動化しています。

**🔗 デモを見る（誰でもアクセス可能・自動更新）**: https://equipmentoperatingrate-ololljouuxxujijb6mcrjz.streamlit.app

<!-- スクリーンショットを追加する場合は、画像を docs/screenshot.png として保存し、下記のコメントを外してください
![Dashboard Screenshot](docs/screenshot.png)
-->

---

## このプロジェクトについて

工場のライン管理でよくある「各設備がどれくらい稼働しているか」を可視化する課題を題材に、**データ生成 → DB蓄積 → 可視化 → 自動実行**までを一気通貫で構築しました。実際にローカル環境（Windows + SQL Server Express）へデプロイし、GitHub Actions Self-hosted Runnerで12時間ごとの自動実行を運用しています。

### 主な特徴
- **完全自動のデータパイプライン**: 疑似稼働データの生成 → SQL Serverへの取り込み（重複防止付きMERGE） → 稼働率算出 → ダッシュボード表示までを自動化
- **5号機並行稼働のシミュレーション**: 5つの加工工程（A→B→C→D→E）それぞれに5台の号機を持つ生産ラインを、号機ごとの空き時間を管理する独自のスケジューリングロジックでモデル化
- **実績 vs 理論値の比較**: 号機ごと・加工機タイプごとに、実績稼働率と理論上の想定稼働率を並べて確認できる機能
- **本番/デモの2系統構成**: 実データを扱う本番環境（SQL Server + Self-hosted Runner）と、誰でもアクセスできるポートフォリオ用デモ環境（SQLite + GitHub-hosted Runner）を分離し、実運用データを外部に公開せずに常時アクセス可能なデモを実現
- **74件超の自動テスト**（pytest）と、実運用で発見した不具合の調査・修正ログを完備

## アーキテクチャ

```
[CsvGenerator] → CSVファイル → [DbLoader] → SQL Server (MERGE取り込み)
                                                    |
                                                    v
                                          [UtilizationCalculator]
                                                    |
                                                    v
                                          [DashboardApp (Streamlit)]

自動実行: GitHub Actions (Self-hosted Runner, 12時間毎) が上記パイプラインを駆動
```

デモ環境は上記と同じロジックを再利用しつつ、SQL ServerをSQLiteに置き換え、GitHub-hosted Runnerで毎日データを自動更新しています。

## 技術スタック

| 分類 | 技術 |
|---|---|
| 言語 | Python 3.13 |
| Web / 可視化 | Streamlit, Plotly, pandas |
| データベース | SQL Server Express（本番）, SQLite（デモ） |
| DB接続 | pyodbc（Windows統合認証） |
| 自動化 | GitHub Actions（Self-hosted Runner / Hosted Runner） |
| テスト | pytest（74件超） |

## エンジニアリング上の工夫

- **リソース制約付きスケジューリング**: 号機ごとに「次に空く時刻」を個別管理し、複数の製品が並行して生産ラインを流れる状況をシミュレート
- **冪等なDB設計**: MERGE文とインデックス設計により、同一データの重複投入を防止しつつ参照性能を確保
- **CI/CDの使い分け**: 実データに依存する本番パイプラインはSelf-hosted Runner、外部依存のないデモデータ生成はコストの低いHosted Runnerで実行という設計判断
- **段階的なデバッグ**: 実運用テストを通じて発見した問題（DB列名の不一致、シェル環境差異、DB権限設定、並行処理ロジックの不具合など）を1つずつ切り分け・検証・修正

詳細な設計判断や発見した不具合の一覧は [`docs/システム概要・仕様書.pdf`](docs/システム概要・仕様書.pdf) にまとめています。

## ローカルでの実行方法

```bash
git clone https://github.com/Naoya-ya-man/Equipment_Operating_Rate.git
cd Equipment_Operating_Rate
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt

# テストの実行
.venv\Scripts\python.exe -m pytest tests -q

# デモ版ダッシュボードの起動（SQLite、実DB不要ですぐ動作確認できます）
.venv\Scripts\streamlit.exe run src\demo\app.py
```

## ドキュメント
- [システム概要・仕様書 (PDF)](docs/システム概要・仕様書.pdf) — アーキテクチャ、画面の使い方、データ問い合わせ方法、稼働率の算出ロジック、発見・修正した不具合一覧など
