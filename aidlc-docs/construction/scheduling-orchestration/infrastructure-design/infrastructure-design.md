# インフラストラクチャ設計（UOW-5: SchedulingOrchestration）

## 対象インフラ
- **実行環境**: GitHub Actions **Self-hosted Runner**（ユーザーのローカルPC上に構築、Windows）
- **DB**: 既存のローカルSQL Server Express（`.\SQLEXPRESS`）— 新規インフラなし
- **シークレット管理**: 不要（Windows統合認証のため、GitHub Secretsに登録すべき資格情報はない）

## Self-hosted Runnerのセットアップ（ユーザー側の作業）
1. GitHubリポジトリの Settings → Actions → Runners から Self-hosted Runner を追加する
2. 表示される手順に従い、ローカルPC上にランナーエージェントをダウンロード・登録する
3. ランナーをサービスとして常時稼働させる（PCが起動している必要がある — `requirements.md` のNFR-3で既知の制約として明記済み）
4. ランナーのラベルは既定の `self-hosted` を使用する（`runs-on: self-hosted` でジョブが実行される）

### 運用上の注意点（ユーザー確認済み: PCはシャットダウンしない運用）
- **PCをシャットダウンしない運用であれば、追加のインフラ変更は不要**（現状のSelf-hosted Runner + ローカルDB構成のままでよい）
- ただし以下2点は必ず設定すること:
  1. **スリープ/休止状態を無効化する**（電源設定: 「PCをスリープ状態にする: なし」）。シャットダウンしていなくても、スリープ中はネットワークが停止しRunnerが応答できずスケジュール実行に失敗するため
  2. **Runnerをサービスとしてインストールする**（GitHub公式インストーラーの「サービスとして実行」オプション）。Windows起動時やWindows Update後の再起動時に自動復旧させるため

## スケジュール設計（cron、UTC変換に注意）
- GitHub Actionsの `schedule` トリガーは常に **UTC** で解釈される
- 目標: JST 0:00 と JST 12:00 の2回（12時間毎）に実行する
- 変換: JST 0:00 = 前日 UTC 15:00 / JST 12:00 = UTC 3:00
- **cron式**: `0 3,15 * * *`（UTC 3:00とUTC 15:00に実行 = JST 12:00とJST 0:00に相当）
- `workflow_dispatch` も併設し、手動実行によるテスト・リカバリを可能にする
- **既知の制約**: GitHub Actionsのスケジュール実行は数分程度の遅延が発生することがある（GitHub側の一般的な制約）。`CsvGenerator`の実行窓判定は起動時の実時刻(`datetime.now()`)を基準にするため、多少の遅延は実害がない

## Python実行環境
- ランナー上でリポジトリ直下に `.venv` を作成（未作成の場合のみ）し、`requirements.txt` を都度インストールする（依存関係の更新に自動追従するため）
- DB接続はWindows統合認証のため、ランナーを実行するWindowsアカウントがSSMSへのアクセス権を持っている必要がある

## ジョブ構成
1. `actions/checkout` でリポジトリをランナーのワークスペースにチェックアウトする
2. Python仮想環境のセットアップ・依存関係インストール
3. `src/scheduling/run_ingestion.py` を実行（CSV生成 + SSMS取り込み）
4. `src/scheduling/run_reporting_refresh.py` を実行（稼働率算出の疎通確認、補助経路）

## 失敗時の可視化
- 各スクリプトはエラー時に非ゼロの終了コードを返し、GitHub ActionsのUI上でジョブ失敗として明示的に表示されるようにする
