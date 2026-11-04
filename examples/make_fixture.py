#!/usr/bin/env python3
"""Generate entirely fictional Excel specifications for the demo."""

from pathlib import Path
import json

from openpyxl import Workbook


ROOT = Path(__file__).resolve().parent
DATA = {
    "function": [
        ("F-1", "税込金額", "税抜価格に消費税を加算する", "税込金額を表示する"),
        ("F-2", "在庫引当", "注文時に在庫を引き当てる", ""),
        ("F-3", "金額表示", "税込金額を表示する", "税抜金額を表示する"),
        ("F-4", "検索", "商品名で検索する", "一致する商品を表示する"),
    ],
    "screen": [
        ("S-1", "ログイン", "IDとパスワードで認証する", "成功時にホーム画面へ移動する"),
        ("S-1", "ログアウト", "セッションを破棄する", "ログイン画面へ移動する"),
        ("S-3", "登録", "氏名は必須入力である", "氏名が未入力でも保存する"),
        ("S-4", "一覧", "商品一覧を表示する", "商品を行単位で表示する"),
    ],
    "report": [
        ("R-1", "売上帳票", "日別売上を表示する", "日付ごとに金額を表示する"),
        ("R-2", "在庫帳票", "", "商品ごとの在庫数を表示する"),
        ("R-3", "合計", "合計は明細金額の総和とする", "合計欄には常に0を表示する"),
        ("R-4", "請求書", "請求先を表示する", "請求先名と住所を表示する"),
    ],
}


def main() -> None:
    target = ROOT / "fixture"
    target.mkdir(exist_ok=True)
    expected = {}
    for kind, rows in DATA.items():
        wb = Workbook()
        ws = wb.active
        ws.title = "仕様"
        ws.append(("id", "kind", "title", "description", "expected_result"))
        for excel_row, (item_id, title, description, result) in enumerate(rows, start=2):
            ws.append((item_id, kind, title, description, result))
            expected[f"{kind}.xlsx:{excel_row}"] = "issue" if excel_row in {
                "function": {3, 4}, "screen": {3, 4}, "report": {3, 4}
            }[kind] else "ok"
        wb.save(target / f"{kind}.xlsx")
    (target / "expected.json").write_text(
        json.dumps(expected, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Created {len(DATA)} workbooks in {target}")


if __name__ == "__main__":
    main()
