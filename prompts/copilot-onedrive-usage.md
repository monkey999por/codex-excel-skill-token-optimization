# Microsoft Copilotアプリ＋OneDriveで使う前提と手順

確認日：2026-11-04。Microsoft Copilotアプリの種類、アカウント、ライセンス、管理者設定によって、参照・添付できる形式と範囲は異なる。**OneDriveにZIPがあるだけで、その中のリポジトリ全体をCopilotが解凍・横断探索できるとはみなさない。** Microsoftの[一般向けアップロード対応形式](https://support.microsoft.com/en-gb/microsoft-365-copilot/file-upload-in-microsoft-copilot)と[職場・学校向け対応形式](https://support.microsoft.com/en-au/microsoft-365-copilot/file-formats-supported-by-microsoft-365-copilot)の確認済み一覧に `.zip` は含まれていない。これは「どのCopilot環境でも絶対に展開できない」という断定ではなく、**プロンプトだけで展開可能だと保証できない**という意味である。

## 最初に行うこと

1. 本番リポジトリのコピーを扱うことが社内ポリシー上許可されているか確認する。ZIPを含め、`.env`、秘密鍵、認証情報、実データ、ログ等を不用意に添付しない。OneDrive上の共有範囲とCopilotのアカウントを確認する。
2. Copilotアプリで対象を添付・参照し、[00. アクセス確認](00-access-check.md)を実行する。名前が見えたことではなく、`SKILL.md`・script・設定/テストの**実際の本文**を一部読めたかで判断する。
3. ZIP内部を読めない場合は、利用者側で許可された方法でローカルに展開し、必要なファイルだけをOneDriveへ置く。展開後の相対パスを保つ。CopilotへZIPの内容を想像させない。
4. 個別ファイルを読める状態で、[索引](README.md)から質問を一問ずつ選ぶ。各回答冒頭の「今回読めたファイル」と「未確認範囲」を確認してから、その結論を使う。

職場・学校向けMicrosoft Copilotには `.py`、`.js`、`.json`、`.yaml`、`.md` などの[対応形式一覧](https://support.microsoft.com/en-au/microsoft-365-copilot/file-formats-supported-by-microsoft-365-copilot)がある一方、一般向けの[ファイルアップロード資料](https://support.microsoft.com/en-gb/microsoft-365-copilot/file-upload-in-microsoft-copilot)にある形式は異なる。対象のアプリとアカウントで実際に読めるか確認する。対応しないソース形式しかない場合、社内ポリシーが許すなら、**元の相対パスを本文先頭に記した** `.txt` または `.md` の閲覧用コピーを用意する選択肢がある。コピーを原本や本番実装と混同しない。

## ファイルを渡す単位

リポジトリ全体を一度の回答に押し込むより、質問ごとに関連ファイルをまとめる。例：

| 質問 | まず参照させるファイル群 |
|---|---|
| 01〜05 全体像 | 主要な `SKILL.md`、入口スクリプト、設定、README、ディレクトリ一覧 |
| 06 個別フロー | 対象の `SKILL.md`、その参照資料、呼ぶscript、検証コード、テスト |
| 07 統合フロー | まとめ用 `SKILL.md`、個別起動箇所、集計script、入出力形式、テスト |
| 08〜10 品質・データ | Excel/JSON変換、判定規則、検証、fixture、期待値 |
| 11〜13 運用 | 設定、依存定義、CI、起動手順、ログ・再開処理 |
| 16〜21 深掘り | 問題の入口、関連する呼出し元・先、設定、テスト、変更履歴 |

上表は**渡す候補**であって、実リポジトリにそのファイルがあると仮定しない。関連ファイルが他にあるとCopilotが示したら追加で参照させる。Microsoftの[Copilot Chat資料](https://support.microsoft.com/en-gb/microsoft-365-copilot/add-content-to-microsoft-365-copilot-chat-prompts)はOneDriveのファイルを添付する手段を説明している。別の[参照資料](https://support.microsoft.com/en-us/microsoft-365-copilot/refer-to-specific-files-and-more-in-microsoft-365-copilot?preview=true)にはフォルダー参照の説明もあるが、Copilot in OneDriveの[FAQ](https://support.microsoft.com/en-us/onedrive/frequently-asked-questions-about-copilot-in-onedrive)にはフォルダーQ&A非対応の記述がある。製品面が異なるため、**フォルダーを選べても全ファイル本文を横断できたとは扱わない**。ファイル数・サイズの上限も利用面ごとに確認する。

## 回答の品質ゲート

- 各回答に「読めた相対パス」「未確認のパス・種類」「結論ごとの根拠」を求める。
- 行番号がCopilotの画面から分からない場合、相対パス＋関数名・見出し＋短い非機密の根拠でよい。**行番号を捏造させない。**
- 「ない」「全て」「必ず」といった断定は、探索範囲が十分か[追加質問ガイド](follow-up-guide.md)で確かめる。
- 複数回に分けてファイルを渡した場合、前回の回答だけを根拠に横断結論を出さず、必要な原本を再添付・再参照する。

Microsoftも[Copilot出力の検証](https://support.microsoft.com/en-gb/microsoft-365-copilot/validate-copilot-output)で、重要な主張を元資料へ遡って確認することを勧めている。今回の質問集はそのための調査補助であり、本番システムの正しさをCopilotだけで保証するものではない。
