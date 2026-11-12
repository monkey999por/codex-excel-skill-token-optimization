# Codex Excel Skill Token Optimization

本番で運用する Excel 仕様書チェックスキルのトークン消費・統合実行時の品質低下・停止に見える事象を調べるための手順と、架空データで動かせるサンプルです。本番のスキルやログはこのリポジトリに含みません。

- [改善・計測ガイド](token-optimization-guide.md)
- [具体的な修正例](concrete-optimization-examples.md)
- [統合実行時だけ品質が下がる場合の原因と切り分け](integrated-run-quality-diagnosis.md)
- [本番の統合実行が停止したように見える場合の判断と安全な再開](long-running-recovery-guide.md)
- [本番リポジトリの初期キャッチアップ用プロンプト集](prompts/README.md)
- [ChatGPTにZIPを渡して本番リポジトリを調べる方法](prompts/chatgpt-zip-usage.md)
- [サンプルコードと架空 Excel](examples/)

実際の業務スキルや業務データは含みません。最初は `examples/` で `python3 make_fixture.py` を実行し、ガイドの「動くサンプル」に沿って確認できます。Codex による判定とトークン計測には、認証済みの Codex CLI が必要です。
