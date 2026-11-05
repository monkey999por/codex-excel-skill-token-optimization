# Microsoft Copilotアプリで本番リポジトリを調べる方法

確認日：2026-11-04。ここでいうCopilotは**Microsoft Copilotアプリ**であり、GitHub Copilotではない。本番リポジトリはこの資料のリポジトリとは別物で、こちらから実物を検証できていない。アカウント、ライセンス、管理者設定、アプリ内で使う機能によって可否が変わる。

## 結論：ZIPリンクから調べる運用はやめる

Microsoftの[Copilotへのファイルアップロード資料](https://support.microsoft.com/en-gb/microsoft-365-copilot/file-upload-in-microsoft-copilot)および[対応形式一覧](https://support.microsoft.com/en-au/microsoft-365-copilot/file-formats-supported-by-microsoft-365-copilot)にZIPはない。実際にZIPを展開できなかった今回の観測とも整合する。「ZIPのOneDriveリンクを渡せば中身を解析できる」とは扱わない。

展開済みリポジトリをOneDriveへアップロードすること自体は可能でも、**保存できることとCopilotが全ソースを読めることは別**。[OneDriveの同期上の推奨事項](https://support.microsoft.com/en-gb/onedrive/restrictions-and-limitations-in-onedrive-and-sharepoint?ad=gb&rs=en-gb&ui=en-us)は大量ファイルの処理に時間がかかると説明する。一方、[OneDrive内のCopilot](https://support.microsoft.com/en-us/onedrive/frequently-asked-questions-about-copilot-in-onedrive)は複数ファイルの質問が最大5件で、フォルダーQ&Aは非対応。[Copilot Chatのファイル参照](https://support.microsoft.com/en-us/microsoft-365-copilot/refer-to-specific-files-and-more-in-microsoft-365-copilot?preview=true)にはフォルダー添付機能の記載があるが、これは別の画面・機能であり、「数百・数千ファイルを網羅して読んだ」ことを保証しない。フォルダーを選べても、網羅性は必ず実測する。

## 推奨する分岐

| 利用環境 | 使い方 | 全体の網羅性 |
|---|---|---|
| Microsoft Copilotアプリの通常チャットのみ | 調査テーマごとに選別したファイル、または根拠付きの小さなソースパックを添付する | 添付した範囲に限定。既定の推奨手順 |
| アプリに「Code」タブがあり、ローカルプロジェクトが許可されている | 本番ではない作業用コピーのローカルフォルダーを開き、[00](00-access-check.md)で探索能力を検証する | フォルダー内を探索できる可能性が高いが、実際に読んだファイルを確認する |
| OneDrive内のCopilotを使う | 最大5件の関連ファイルを選択して質問する | 選択ファイル内だけ。リポジトリ全体の調査には単独では不向き |

通常チャットへの[ファイルアップロード](https://support.microsoft.com/en-gb/microsoft-365-copilot/file-upload-in-microsoft-copilot)は1会話20件、1件50 MBまでと案内されている。共通の対応形式はPDF、DOCX、XLSX、PPTX、TXT、JSON、CSV、MD等。[職場・学校アカウントでCopilotライセンスがある場合](https://support.microsoft.com/en-au/microsoft-365-copilot/file-formats-supported-by-microsoft-365-copilot)は `.py`、`.js`、`.sh`、`.yaml` なども対象に含まれる。対象環境で実際に添付・本文参照ができるかを試すこと。個人アカウントや別画面に職場向け対応をそのまま当てはめない。

Microsoftの[Copilot Code（Frontier）](https://learn.microsoft.com/en-us/copilot/code/get-started)はプレビューで、Codeタブの有効化と条件を満たす環境が必要。利用可能なら[ローカルの既存フォルダー](https://learn.microsoft.com/en-us/copilot/code/use-code)を開ける。ただし、**開いたプロジェクト内のファイルを承認なしに読み書きできる**。調査の指示文だけで変更を防ぐことはできない。社内規程が許す、秘密情報を除いた隔離コピーを使い、必要ならOS側で書き込みを制限する。Codeタブがなければこの方法は飛ばす。

## 通常チャットでの具体的な進め方

1. 社内ポリシー上、Copilotへの入力が許された**調査用コピー**を用意する。`.env`、鍵、認証情報、顧客データ、実データExcel、ログ、生成物、`.git`、依存ライブラリは対象から外す。除外後にも機密が残らないか人が確認する。
2. 構成を知らなくても、まずローカルで相対パス・拡張子・サイズ・件数の**機械的な目録**を作れる。次にファイル名や静的な参照から入口候補を抽出する。目録は探索範囲と欠落を可視化するためのもので、本文の根拠とはみなさない。具体的な開始方法は[未知のリポジトリを探索する手順](00a-repository-discovery.md)を参照。
3. 1テーマにつき、入口の `SKILL.md`、呼ぶscript、集計script、設定、対応するテストなど、**原本の関連ファイルだけ**を少数選ぶ。パス構造が添付で失われるなら、閲覧用 `.md`/`.txt` に原本の相対パスと必要な行範囲を明記する。原本を加工した場合は「閲覧用コピー」であると明記する。
4. [00. アクセス確認](00-access-check.md)で本文が読めるか検証し、[索引](README.md)の個別プロンプトを一問ずつ使う。回答には「読めたファイル」「未確認ファイル」「根拠」を要求する。次に必要なディレクトリ一覧・原本ファイルはCopilot自身に相対パス・理由・確認点付きで選ばせる。アクセスできるものはCopilotが読み、通常チャットで読めないものは要求に沿って次の回で追加する。追加した本文から新たな呼出し先が見つかれば、さらに追跡する。
5. 統合フローなど複数テーマにまたがる結論は、前回のAI要約だけでつながず、必要な原本を再添付して照合する。全体の網羅的な結論は、目録上の対象ファイルと実際に読めたファイルの差分を確認してから出す。

### ローカルで取得するOneDrive URLについて

OneDrive同期フォルダーをローカルで列挙すれば、ローカル相対パスの目録は作れる。ただし、ローカルパスから共有URLを文字列連結で作ることは避ける。正式なURLが必要なら、組織が許可した認証・権限の下で[Microsoft Graphのフォルダー列挙API](https://learn.microsoft.com/en-us/graph/api/driveitem-list-children?view=graph-rest-1.0)を使い、各項目の[`webUrl`](https://learn.microsoft.com/en-us/graph/api/resources/driveitem?view=graph-rest-1.0)を取得する。子フォルダーを再帰的にたどり、`@odata.nextLink`のページ送りも処理する。URLは「その項目をブラウザーで開く場所」であり、アクセス権の付与でもCopilotによる本文読解の証明でもない。URL一覧だけを渡して全コードの分析を期待しない。

ソースパックの例（内容は架空。実ファイルを見てから選ぶ）：

```text
調査テーマ: まとめ用スキルから個別チェックへの呼出し
対象版: 調査用コピーの作成日・コミットID（分かる場合）
目録: skills/aggregate/SKILL.md, skills/check-a/SKILL.md,
      scripts/run_aggregate.py, scripts/check_a.py, tests/test_aggregate.py
今回添付: skills/aggregate/SKILL.md, scripts/run_aggregate.py,
          skills/check-a/SKILL.md
未添付: scripts/check_a.py, tests/test_aggregate.py
問い: まとめ→個別チェックの呼出し経路を、今回読めた本文だけで追跡。
      未添付ファイルに依存する結論は保留して、次に必要なファイルを挙げる。
```

**注意**：複数のコードを1つの文書に結合する場合、各節に `原本相対パス` と `元の行番号` を付け、行の省略・加工を明示する。単なるAI要約やファイル名一覧をソースの代用にしない。大量のコードを1巨大文書へまとめると参照漏れ・文脈欠落の検証が難しくなるため、テーマ別に分割する。

## 失敗を見分ける基準

- ファイル名だけ挙げ、本文中の関数名・設定キー・短い根拠を示せない → 本文アクセス未確認。
- 目録にはあるのに、関連する呼出し先・テストを読めない → その範囲の結論を保留。
- 行番号が画面から得られない → 行番号を捏造せず、相対パス＋関数名・見出しで示す。
- 「全て」「存在しない」などの断定 → 探索対象数と読めた件数を照合し、未確認範囲を示す。

[Microsoftの出力検証ガイド](https://support.microsoft.com/en-gb/microsoft-365-copilot/validate-copilot-output)も重要な主張を元資料へ戻って確認することを勧めている。Copilotの回答は本番実装の保証ではなく、根拠確認付きのキャッチアップ資料として扱う。
