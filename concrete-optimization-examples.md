# Excel 仕様書チェックスキルの具体的な修正例

調査日：2026-11-04。対象は **Codex CLI のスキル**。実スキルは非公開のため、以下はこのリポジトリの架空データに沿った移植例であり、効果を実測した結果ではない。先に[改善・計測手順](token-optimization-guide.md)で基準値を取り、各変更を一つずつ評価する。

## 1. few-shot：例を足す条件と、削る条件

few-shot は、入力と期待出力の例を数個示して判定形式や境界を伝える方法。OpenAI の[プロンプト設計資料](https://developers.openai.com/api/docs/guides/prompt-engineering)は、例を使うなら多様なケースを選ぶことを勧める。一方、[最新モデルの指針](https://developers.openai.com/api/docs/guides/latest-model)は、重複した例を削って評価し直すことを勧める。したがって「まず例なしで測る → 実際の誤判定を直す最小限の例だけ追加する」が出発点になる。

### 変更前：長い例を各行に繰り返す

```text
この仕様が正しいか、以下の10件の完全な仕様書とその判定を参考にしてください。
（毎回、数千字の例を再掲）
今回のExcel行を詳しく説明してください。正常な場合も理由を3段落書いてください。
```

### 変更後：判定規則を先に、境界例を必要時だけ

```text
description と expected_result の意味が明確に矛盾する場合だけ issue。
矛盾がない場合は ok。行内の記述にない前提は補わない。
各候補について row_key, verdict, code, evidence を返す。
ok の code は OK、evidence は空文字。issue の evidence は矛盾する語句を短く示す。

例（この境界を誤る場合だけ残す）:
入力: {"row_key":"example:1","description":"氏名は必須","expected_result":"未入力でも保存"}
出力: {"row_key":"example:1","verdict":"issue","code":"CONTRADICTION","evidence":"必須と未入力保存が矛盾"}
```

上の例は架空の学習例。評価用データに同じ行を混ぜて精度が上がったと判定しない。正常行の誤検出が多いなら、その失敗を表す短い `ok` 例を1件追加する。例を追加するたびに入力トークンと判定品質を比較し、改善しなければ外す。few-shot の量を固定値で決めない。

実運用で「資料不足」と「問題なし」を分ける必要があるなら、`needs_review` を出力契約と集計スクリプトの双方へ追加する。**このリポジトリの現行 `pipeline.py` は `ok` / `issue` の2値だけ**を受け付けるため、プロンプトだけに `needs_review` を書いても動かない。

## 2. プロンプト：仕事の境界と出力契約を短く書く

長い思考手順、各行での自己紹介、全規則の再掲は、期待する出力に直結しない場合がある。[最新モデルの指針](https://developers.openai.com/api/docs/guides/latest-model)は、指示を一度だけ書き、重複した指示・例・不要なツール説明を削って評価することを勧める。

### 変更前：曖昧なゴールと冗長な出力

```text
Excelをすべて詳しく読んで総合的にレビューしてください。
各行について考えたことを説明し、判断理由も丁寧に書いてください。
最後に全文を表形式で再掲し、集計結果も自然文で詳しく説明してください。
```

### 変更後：入力、判定、出力、失敗時を明示

```text
入力: out/function.ai.json の candidates のみ。
判定: description と expected_result に明確な矛盾がある行だけ issue。
出力: out/function.review.json に results 配列を保存。
各要素: row_key, verdict(ok|issue), code, evidence。
正常行は code=OK, evidence=""。問題行の evidence は短い引用・要約。
すべての row_key をちょうど一度含める。入力にない行を追加しない。
保存後、merge コマンドの検証が失敗した行だけ修正する。
```

この形式は[サンプルの `demo-check` スキル](examples/.agents/skills/demo-check/SKILL.md)と[`pipeline.py`](examples/pipeline.py)の入出力契約に対応する。実スキルでは、必須の根拠や指摘分類を削ってはいけない。短くした結果、再試行や人手確認が増えるなら総トークンはかえって増える。

## 3. `skill → Python → skill` の連結で何が増えるか

**スキルを順に呼ぶこと自体が、必ず新しいモデルセッションや固定のトークン課金を発生させるわけではない。** 見直す対象は、途中でモデルに返す大量の `stdout`、同じファイルの再読込、判定前後の全件再掲、モデル判断を必要としない段階ごとの往復である。これは[Shell ツールの入出力](https://developers.openai.com/api/docs/guides/tools-shell)と[Programmatic Tool Calling の設計指針](https://developers.openai.com/api/docs/guides/tools-programmatic-tool-calling)から、この構成に適用した推論。Codex CLI 内の段階別トークン内訳が自動で得られるという意味ではない。

### 変更前：全件を何度もモデルへ戻す

```text
check-skill → Python がExcel全行を標準出力に表示
            → Codex が全行を読んで判定
            → Python が判定済み全行を標準出力に表示
summary-skill → 結果ファイルをすべて読み直して再表示
              → Codex が全行を要約し、件数も数える
```

### 変更後：判断が必要な境界だけモデルへ渡す

```text
check-skill
  Python: Excelから必要列を抽出し、空欄・重複などを機械判定
  ├─ packet.json   全件と機械判定を保持（Python用）
  └─ ai.json       意味判断が必要な候補のみ（Codex用）
  Codex: ai.json を読み、review.json に候補ごとの判断を保存
  Python: packet.json と review.json を照合し、check.xlsx を作成

summary-skill
  Python: 各 check.xlsx の結合・件数集計
  ├─ summary.packet.json  全件詳細（Python用）
  └─ summary.ai.json      件数とコード別代表例（Codex用）
  Codex: summary.ai.json から俯瞰文だけを作る
  Python: 詳細・件数・俯瞰文を summary.xlsx に保存
```

実際に[サンプルスクリプト](examples/pipeline.py)は、次のように AI 用の小さいファイルを別に作る。コマンドの標準出力は件数だけで、詳細行は表示しない。

```bash
cd examples
python3 pipeline.py prepare \
  --input fixture/function.xlsx \
  --out out/function.packet.json \
  --ai-out out/function.ai.json
```

この例の `function.xlsx` では4行中1行を機械的に指摘し、AI 候補は3行になる。ファイル分割だけでは節約にならない。**Codex が `packet.json` と `ai.json` の両方を読めば、削減効果は失われる。** スキルの指示で「読むのは `ai.json`」とし、スクリプト側は `packet.json` を使って欠落・重複・ID 対応を検証する。

判断不要な連続処理が複数ある場合、Python 側に1つのオーケストレーターを置いてまとめて実行し、Codex には最終的な小さい結果だけ返す方法を試す。ただし、途中のエラーと入力ごとの追跡が失われないよう、終了コード・件数・失敗ファイル名は残す。API で独自のツール群を構築している場合の[Programmatic Tool Calling](https://developers.openai.com/api/docs/guides/tools-programmatic-tool-calling)も同じ発想だが、Codex CLI スキルにその設定を追加する手順ではない。

## 4. スキルの重複指示と段階的読み込み

### 変更前：統合スキルが個別スキルの全文を複製

```text
summary/SKILL.md: 機能仕様の全チェック規則、画面仕様の全チェック規則、帳票仕様の全チェック規則、
                  各スクリプトのコード全文、全出力例を掲載
check-*/SKILL.md: 同じ規則とコード全文を再掲
```

### 変更後：共有契約を一か所に置く

```text
summary/SKILL.md: 対象スキルを選ぶ条件、入力と出力の対応、統合後の終了条件だけ
check-*/SKILL.md: 各種類に固有の判断基準だけ
references/: 特定の種類を処理するときだけ必要な詳細規則・例
scripts/: Excel の読取、機械チェック、結合、集計
```

スキルの `description` は「いつ使うか」が分かる短い文にする。OpenAI の[Codex 向け記事](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)は、長い説明がスキル選択を難しくし、必要時だけ資料を読む段階的な構成が文脈消費を抑えると説明している。一方、全種類の規則を単一スキルにまとめるのが常に最適とは限らない。単独実行という既存要件と、種類ごとの判断基準を維持する。

## 5. ツール仕様・ツール出力を節約する

### Codex CLI のスキルで直接できること

- スクリプトの `stdout` を `処理行数 / AI候補数 / エラー件数 / 出力先` 程度にする。大量データはファイルに保存し、Codex が必要な小さいファイルだけ読む。エラー時は原因と対象行を残す。
- 同じ Excel や JSON を複数スキルが読み直さないよう、入力・出力ファイルを受け渡す。既存結果を再利用する場合は、入力の版と結果の対応を検証する。
- 各行ごとのツール呼び出しを避け、スクリプトで候補をまとめる。1回の巨大な候補入力で品質が落ちる場合は、測定して分割する。
- `SKILL.md` にスクリプトの実装全文を貼らず、呼び出し方と入出力契約だけを記す。詳細は該当時だけ参照する。

### 自作の API / MCP ツールがある場合だけ検討

- ツール名・説明・引数を用途が分かる最短の形に整理し、重複ツールを見直す。[最新モデルの指針](https://developers.openai.com/api/docs/guides/latest-model)は、関連ツールだけを公開し、説明を簡潔にすることを勧める。
- 多数のツールを自前の Responses API に登録しているなら、[Tool search](https://developers.openai.com/api/docs/guides/tools-tool-search)で定義を必要時に読み込む選択肢がある。**Codex CLI の組み込みツールを `SKILL.md` から `defer_loading` にする機能ではない。**
- ツールが全件を返す設計なら、`count`、`issue_samples`、`artifact_path` のような構造化された結果に変える。ただし必要な根拠を切り捨てず、詳細は参照可能なファイルとして残す。[Programmatic Tool Calling の資料](https://developers.openai.com/api/docs/guides/tools-programmatic-tool-calling)は、複数結果をコードで絞り込む場合に中間出力を減らせると説明している。

## 6. 変更前後の判定表

| 変更 | まず見る指標 | 採用条件 |
|---|---|---|
| few-shot を0→1件、または冗長な例を削除 | 入力トークン、境界ケースの誤判定 | 判定品質が維持・改善し、総トークンが下がる |
| スキル説明と参照資料の整理 | 起動率、誤起動、最初の文脈量 | 必要なスキルが選ばれ、不要な資料読込が減る |
| `packet.json` / `ai.json` の分離 | モデルが読んだデータ、行対応 | 全行を漏れなく処理し、不要な行の再読込が減る |
| 機械チェック・集計の Python 化 | AI 候補数、集計一致 | 指摘の取りこぼしと件数差がない |
| ツールの短い結果 | ツール出力、失敗時の診断可能性 | 正常時の出力が減り、失敗原因は追える |

実測は[既存の `measure.py`](examples/measure.py)で `codex exec --json` の入力・出力・キャッシュ済み入力を確認する。正解データで行単位の品質と集計値も照合する。キャッシュ済み入力は総入力の内数であり、キャッシュ率上昇だけを「総トークン削減」と呼ばない。[OpenAI のキャッシュ資料](https://developers.openai.com/api/docs/guides/prompt-caching)

### この文書の適用範囲

ここで示した「変更前」は典型的な無駄の例で、ユーザーの非公開スキルに実際に存在すると断定していない。Codex CLI で有効な改善と、自作 API / MCP に限定される機能を分けた。削減量は入力データ、モデル、実行方法、キャッシュ状態に依存するため、公開資料の数値をこのスキルの予測値として転用しない。
