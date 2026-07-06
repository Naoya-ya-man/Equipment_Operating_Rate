# ビジネスロジックモデル（UOW-1: CsvGenerator）

## 全体ワークフロー

```
1. 実行窓(ExecutionWindow)の決定
   - 実行時刻から window_start / window_end を算出
   - 日曜日判定 → 全休なら available_seconds=0 で以降スキップ
   - 月曜日判定 → 0:00-9:00を非稼働として除外

2. 稼働可能秒数の算出 (BR-2)
   - 窓の長さ - 休憩時間 - 非稼働時間

3. 加工機タイプ(A~E)ごとの理論生産数上限を算出 (BR-3)
   - ボトルネック工程(C)の値をこの窓の完成品数上限とする

4. 実際に生成する完成品(ProductChain)数を決定 (BR-4)
   - 上限を超えない範囲で、故障・不良の実効影響を考慮しランダム決定

5. ProductChainをひとつずつ生成 (BR-5, BR-6, BR-9, BR-10)
   ループ:
     a. 品番ベース(base_product_id)を採番
     b. 開始時刻の候補を決定（残り窓時間・休憩時間帯を考慮）
     c. 残り窓時間で標準加工時間合計(A+B+C+D+E)が収まらない場合 → 生成打ち切り
     d. A→B→C→D→Eの順に、各工程の号機(1~5)を均等配分でランダム割当
     e. 各工程の開始/終了時刻を、前工程の終了時刻以降・休憩時間帯を避けて決定
     f. 低確率(約1%)で設備停止相当(2~3倍時間)を適用 (BR-7)、窓を超えないようクリップ
     g. 低確率(約3%)でNG判定を適用 (BR-8)
     h. 5件のProcessingRecordを確定し、ProductChainに追加

6. 全ProductChainのProcessingRecordをCSVカラム順に整形して出力
   - `データ転送前/A1_ProcessingMachine_Utilization_Rate.csv`
```

## 入出力
- **入力**: 実行時刻（GitHub Actionsのトリガー時刻、またはローカル実行時の現在時刻）
- **出力**: `データ転送前/A1_ProcessingMachine_Utilization_Rate.csv`（この実行窓で生成された全ProcessingRecordを含む）
- **出力なし（スキップ）の条件**: 実行窓が日曜日に該当する場合

## 主要な計算ロジック

### 理論生産数上限の計算式（BR-3）
```
unit_capacity(machine_type) = floor(available_seconds / standard_seconds(machine_type))
type_capacity(machine_type) = unit_capacity(machine_type) * 5  # 5号機

window_capacity = type_capacity(bottleneck_machine)  # 基準値ではC
```

### チェーン開始可否の判定（BR-6）
```
required_seconds = sum(standard_seconds(A..E)) + safety_margin
if remaining_window_seconds >= required_seconds:
    このチェーンを開始する
else:
    この窓でのチェーン生成を終了する
```

## エラーハンドリング・エッジケース
- **日曜日**: CSVファイル自体を生成しない（空ファイルも作らない。DbLoader側は当該実行を「対象ファイルなし」として正常にスキップする）
- **理論上限が0以下になるケース**（極端に短い稼働可能秒数）: チェーン生成を0件とし、空のCSV（ヘッダーのみ）を出力する
- **設備停止による窓超過**: BR-7に従い、その工程の時間を窓の残り時間にクリップして必ず窓内に収める
