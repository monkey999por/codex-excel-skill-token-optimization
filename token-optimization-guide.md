# Codex の Excel 仕様書チェックスキル：トークン削減の実践手順

最終確認日：2026-11-04。対象は Codex CLI。実スキルと実データは共有されていないため、改善案は仮説として扱い、同じ入力で実測して採否を決める。

few-shot、プロンプト、スキルとスクリプトの受け渡し、ツール出力については[具体的な修正例](concrete-optimization-examples.md)を参照。

## 何を減らすか

主指標は **1回の作業が完了するまでの総トークン**（入力＋出力）。入力にはキャッシュ済みトークンも含まれる。キャッシュは費用と待ち時間に効くが、総トークンを減らしたことにはならない。判定漏れや誤判定、出力欠損、実行失敗を増やして得た削減は不採用とする。

この構成では、消費が膨らむ箇所は主に以下の四つと推測できる。

| 箇所 | 確認する現象 | 最初に試す変更 |
|---|---|---|
| スキル起動 | 長い説明や関連外スキルまで読み込む | `description` を用途が分かる短い文にし、詳細は必要な参照ファイルへ |
| Excel 読み込み | 全シート、空欄、装飾、既知のエラーまで会話に載る | スクリプトで列を選び、空行・定型エラーを先に処理 |
| 行判定 | 各行で同じ規則や過去の結果を繰り返し送る | 行 ID と必要列のみをまとめ、短い判定コードで返す |
| 統合・俯瞰 | 全チェック結果を再度 AI に読ませる | 全件の結合と件数はスクリプト、AI には件数と代表例だけ |

近年の OpenAI の指針も、スキル説明の簡潔化、必要な資料だけの段階的読み込み、反復指示の削除を勧めている。[スキル設計](https://developers.openai.com/plugins/build/skills)、[Codex のスキルとプロンプトの見直し](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)、[GPT-6 系のプロンプト指針](https://developers.openai.com/api/docs/guides/latest-model)

## 改善の順序

1. **基準値を固定する。** 小・中・大の架空または社内で許可された入力を選び、単独チェックと統合実行をそれぞれ複数回走らせる。Codex のバージョン、モデル、推論設定、入力行数、成功・失敗、所要時間、出力品質を記録する。比較では同じ条件を使い、中央値を見る。
2. **増加箇所を特定する。** `codex exec --json` の `turn.completed.usage` を保存する。チェック単独と統合実行の総量、入力・出力・キャッシュ済み入力、コマンドの回数、重複したファイル読み込みを確認する。単一ターン内のスキル別トークン内訳は取得できないので、ステージの境界が必要なら別実行で測る。ただし別実行の値を統合実行の正確な内訳として扱わない。
3. **高確度の機械処理から縮める。** 空欄・形式・ID 重複・件数・結合・並べ替えはスクリプトで行う。AI に渡す前に、必要列だけを行 ID 付きで抽出する。同一文面の重複除去は、行ごとの出力対応を保てる場合に限る。
4. **AI の入出力を短くする。** 意味判断が必要な候補だけを渡す。判定結果は `row_key`、`verdict`、短い `code`、問題箇所の `evidence` に限定する。長い説明が必要な例外だけ詳述し、正常行には説明を繰り返さない。バッチ化は有効な場合があるが、巨大な一括入力で見落としが増える可能性もあるので、候補数を変えて品質と総量を比較する。[OpenAI の遅延最適化資料](https://developers.openai.com/api/docs/guides/latency-optimization)
5. **統合段階の再読込を止める。** 詳細な指摘はファイルに保持し、AI の俯瞰には種類別件数・指摘コード別件数・代表例を渡す。代表例から全件の傾向を断定しない。全件に基づく意味判断が必要なら、その要件に限って対象行を追加する。
6. **一変更ずつ再評価する。** 行 ID の対応、指摘・正常の取りこぼし、件数一致、俯瞰文の根拠を確認する。品質が落ちたら元に戻し、必要な文脈だけ戻す。問題が残る行だけ再試行する。モデル変更は最後に別実験とし、トークン削減と費用削減を混同しない。

固定の「最適バッチサイズ」や削減率は設定しない。入力の長さ、判定難度、モデル、キャッシュ状態で変わる。頻繁な全件再試行や、出力を削りすぎた結果の再判定は総量を増やす。

## 計測ツールの選定

| ツール | 用途 | この案件での位置づけ |
|---|---|---|
| Codex 標準 `codex exec --json` ＋ `examples/measure.py` | 1実行ごとの実測値、改善前後の比較 | **主ツール**。追加の計測サービス不要。`turn.completed.usage` を使う |
| [ccusage](https://github.com/ccusage/ccusage/blob/main/docs/guide/codex/index.md) | 既存セッションの日・月・セッション別傾向 | 補助。Codex ログ対応は実験的で、スキル単位の厳密比較には向かない |
| トークナイザーによる事前推定 | 抽出した入力テキストの相対的な大きさ | 補助。実行中の再読込・推論出力・キャッシュは計れない |

OpenAI の[スキル評価ガイド](https://developers.openai.com/blog/eval-skills)は `codex exec --json` と `turn.completed.usage` を使った計測を示す。`usage.input_tokens` はキャッシュ済み入力を含むため、`cached_input_tokens` を足し直さない。`reasoning_output_tokens` がある場合は `output_tokens` の内数なので足し直さない。[Codex のイベント定義](https://github.com/openai/codex/blob/main/codex-rs/exec/src/exec_events.rs)

失敗・中断した実行では `turn.completed` がなく使用量が欠けることがある。この場合、**ゼロトークン**と記録しない。計測器は `NA` と表示する。[Codex の既知の制約](https://github.com/openai/codex/issues/50586)。トレースには入力や出力の内容が含まれ得るので、実データのトレースは利用環境の保管規則に従う。

## 動くサンプル

`examples/` には、機能・画面・帳票の架空仕様書を生成する `make_fixture.py`、Excel 処理の `pipeline.py`、計測用 `measure.py`、2つのサンプルスキルがある。`sample_reviews/` は AI を呼ばずにデータ処理を確認するための模擬判定であり、Codex による判断の正解として読み込ませない。

計測器だけを試す場合は `python3 measure.py sample_trace.jsonl` を実行する。架空のトレースから入力1,200、キャッシュ済み入力400、出力200、総量1,400が表示される。

### 1. AI を使わずにデータ処理を確認

作業ディレクトリを `examples/` にして実行する。Python 3.11 と `openpyxl` 3.1 系が必要。未導入なら `python3 -m pip install -r requirements.txt`。

```bash
cd examples
python3 make_fixture.py
mkdir -p out
python3 pipeline.py prepare --input fixture/function.xlsx --out out/function.packet.json --ai-out out/function.ai.json
python3 pipeline.py merge --packet out/function.packet.json --review sample_reviews/function.review.json --out out/function.check.xlsx
python3 pipeline.py prepare --input fixture/screen.xlsx --out out/screen.packet.json --ai-out out/screen.ai.json
python3 pipeline.py merge --packet out/screen.packet.json --review sample_reviews/screen.review.json --out out/screen.check.xlsx
python3 pipeline.py prepare --input fixture/report.xlsx --out out/report.packet.json --ai-out out/report.ai.json
python3 pipeline.py merge --packet out/report.packet.json --review sample_reviews/report.review.json --out out/report.check.xlsx
python3 pipeline.py verify --expected fixture/expected.json --checks out/function.check.xlsx out/screen.check.xlsx out/report.check.xlsx
python3 pipeline.py aggregate-prepare --checks out/function.check.xlsx out/screen.check.xlsx out/report.check.xlsx --out out/summary.packet.json --ai-out out/summary.ai.json
python3 pipeline.py aggregate-finalize --packet out/summary.packet.json --overview sample_reviews/overview.json --out out/summary.xlsx
```

期待値は12行、指摘6件。`out/summary.xlsx` に詳細、件数、俯瞰文が入る。`out/*.ai.json` は AI に見せる小さな入力、`out/*.packet.json` はスクリプトが扱う全件データである。

### 2. Codex のスキルで判定する

最初に上の `make_fixture.py` を実行する。以下も `examples/` から実行する。認証済みの Codex CLI が必要。実行先の `out/` は作業用ファイルを生成する。

`out/` がまだなければ `mkdir -p out` を先に実行する。

```bash
codex exec --json --skip-git-repo-check -C . -s workspace-write 'Use the demo-check skill to check fixture/function.xlsx.' > out/check-trace.jsonl
python3 measure.py out/check-trace.jsonl
```

統合実行では `demo-summary` が3種類のチェック手順を実行してから集計する。統合実行のトレースは**全体**の使用量であり、個別スキルへの正確な配賦はできない。

```bash
codex exec --json --skip-git-repo-check -C . -s workspace-write 'Use the demo-summary skill to check all three fixture workbooks and make the aggregate workbook.' > out/summary-trace.jsonl
python3 measure.py out/check-trace.jsonl out/summary-trace.jsonl
python3 pipeline.py verify --expected fixture/expected.json --checks out/function.check.xlsx out/screen.check.xlsx out/report.check.xlsx
```

`measure.py --json` で機械処理しやすい結果を出せる。実運用では入力一式を固定し、改善前後それぞれを新しい作業コピーで複数回実行する。過去の `out/` を再利用すると、スキルが作業を省略して比較が歪むためである。

## 実スキルへ移すときの確認事項

サンプルの列名や矛盾判定は説明用である。実際には、機能・画面・帳票ごとの入力列、確定的に判定できる規則、AI に必要な文脈、根拠の粒度、最終ファイル形式を洗い出す。既存の出力列・指摘の意味・再現性を保ちながら、AI 入力と出力だけを段階的に縮める。

プロンプトキャッシュは、同じ長い接頭部を再利用できる場合の費用・遅延対策として後から検討する。Codex CLI のスキルで Responses API のキャッシュ設定を直接操作する前提にはしない。キャッシュ率と総トークンを別々に記録する。[OpenAI のキャッシュ資料](https://developers.openai.com/api/docs/guides/prompt-caching)
