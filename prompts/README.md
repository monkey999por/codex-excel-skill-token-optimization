# 本番リポジトリの初期キャッチアップ用プロンプト

Microsoft Copilotアプリで本番リポジトリの調査用コピーを扱う前提。まず[アクセス方法と制約](copilot-onedrive-usage.md)を読む。ZIPリンクを渡す方法は使わない。通常チャットでは関連する原本ファイルを小分けに添付する。Codeタブが利用可能な環境では、許可済みローカルコピーを開く方法も選べる。[00. アクセス確認](00-access-check.md)で、実際に本文を読める範囲を調べる。**OneDrive上のフォルダー名が見えるだけで深い分析はできない。**

各ファイルのコードブロックをCopilotへ**一問ずつ**貼り付ける。このリポジトリには本番の skill、script、実データがないため、回答は本番リポジトリの根拠で確認する。01〜22は読み取り専用で、編集・本番データ閲覧・スクリプト実行を依頼しない。各問の冒頭で「今回本文を読めた相対パス」と「未確認範囲」を示させ、読めない対象について結論を出させない。**01〜22の本文には、README・docsだけで結論を出さず、実装・設定・テストと呼出し経路を深く調べる絶対ルールを入れた。**

00でアクセスを確認し、構成が分からない場合は[00a. 未知のリポジトリを探索](00a-repository-discovery.md)してから、01〜07で目的・入口・構造・処理経路を把握する。次に08〜12で品質と運用の境界を確認し、必要に応じて13〜22を選ぶ。回答を受けたら[追加の問いかけガイド](follow-up-guide.md)に沿って根拠と矛盾を確認する。**一度に全問を投げない**。回答が膨らみ、重要な根拠を追えなくなる。

| 順 | 質問 | 主に分かること |
|---|---|---|
| 00 | [Microsoft Copilotアプリの本文アクセス確認](00-access-check.md) | Copilotが実際に本文を読める範囲 |
| 00a | [未知のリポジトリを探索](00a-repository-discovery.md) | 目録から入口候補を見つける |
| 01 | [目的・利用者・成果物](01-purpose-and-users.md) | 何のための仕組みか |
| 02 | [機能一覧と実行入口](02-capabilities-and-entrypoints.md) | 何ができ、どこから始まるか |
| 03 | [ディレクトリ構造と役割](03-directory-map.md) | どこに何があるか |
| 04 | [チェックスキル一覧](04-check-skill-catalog.md) | 種類別の起動条件と責務 |
| 05 | [アーキテクチャと責務分担](05-architecture-and-ownership.md) | 構成要素のつながり |
| 06 | [個別チェックの処理フロー](06-single-check-flow.md) | 単独実行の道筋 |
| 07 | [まとめ用スキルからの一括実行](07-aggregate-flow.md) | 統合実行の道筋と単独との差 |
| 08 | [入出力契約](08-data-contracts.md) | Excel・JSON・行IDの対応 |
| 09 | [AIとスクリプトの境界](09-ai-vs-script-boundary.md) | 何を誰が判断するか |
| 10 | [品質保証とテスト](10-quality-and-tests.md) | 何を検証しているか |
| 11 | [実行環境と依存関係](11-runtime-and-dependencies.md) | 設定・権限・依存 |
| 12 | [進捗と再開](12-progress-and-recovery.md) | 長時間実行・中断の扱い |
| 13 | [変更・配布・運用](13-release-and-operations.md) | 本番へ届く経路 |
| 14 | [入力1件の追跡](14-trace-one-record.md) | 行がどう変換されるか |
| 15 | [未解決事項](15-open-questions.md) | 次に確認すべきこと |
| 16 | [変更履歴と設計判断](16-history-and-decisions.md) | 現在の形になった理由 |
| 17 | [暗黙の契約](17-cross-component-contracts.md) | 破れやすい連携条件 |
| 18 | [機密・権限・データ境界](18-security-and-data-boundaries.md) | データの扱いと外部送信 |
| 19 | [性能・トークン消費](19-performance-and-token-hotspots.md) | 重くなる候補と計測箇所 |
| 20 | [境界条件と失敗パターン](20-edge-cases-and-failure-modes.md) | 異常系の挙動 |
| 21 | [所有者と問い合わせ先](21-ownership-and-support.md) | 誰に何を確認するか |
| 22 | [用語集と読む順番](22-terms-and-reading-path.md) | 新規参加者の学習経路 |

本番で既に報告されている「統合時だけ品質が下がる」問題には 07・08・09・10・17・19 を、「停止したように見える」問題には 07・11・12・17・19・20 を優先する。調査の判断枠組みは[品質低下ガイド](../integrated-run-quality-diagnosis.md)と[安全な再開ガイド](../long-running-recovery-guide.md)を参照。

Codex skill の一般的な構成は[公式 OpenAI Docs](https://developers.openai.com/plugins/concepts/skills)で確認した。ただし、**本番リポジトリがその構成を採用しているとは仮定しない**。
