#!/usr/bin/env python3
"""Deterministic preparation, validation, merge and aggregation for the demo."""

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

from openpyxl import Workbook, load_workbook


HEADERS = ("id", "kind", "title", "description", "expected_result")
CHECK_HEADERS = ("row_key", "kind", "id", "verdict", "code", "evidence")


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def text(value):
    return "" if value is None else str(value).strip()


def prepare(args):
    source = Path(args.input)
    ws = load_workbook(source, read_only=True, data_only=True).active
    headers = tuple(text(cell.value) for cell in next(ws.iter_rows(min_row=1, max_row=1)))
    if headers != HEADERS:
        raise ValueError(f"Expected columns {HEADERS}, got {headers}")
    seen = set()
    rules, candidates = [], []
    for cells in ws.iter_rows(min_row=2):
        values = dict(zip(HEADERS, (text(cell.value) for cell in cells)))
        if not any(values.values()):
            continue
        row_key = f"{source.name}:{cells[0].row}"
        values["row_key"] = row_key
        missing = [name for name in HEADERS if not values[name]]
        duplicate = bool(values["id"] and values["id"] in seen)
        if values["id"]:
            seen.add(values["id"])
        if missing or duplicate:
            codes = (["MISSING_" + name.upper() for name in missing]
                     + (["DUPLICATE_ID"] if duplicate else []))
            rules.append({"row_key": row_key, "kind": values["kind"], "id": values["id"],
                          "verdict": "issue", "code": "+".join(codes),
                          "evidence": "必須項目の空欄またはID重複"})
        else:
            candidates.append(values)
    write_json(args.out, {"source": str(source), "rules": rules, "candidates": candidates})
    write_json(args.ai_out, {"candidates": candidates})
    print(f"{source.name}: rule issues={len(rules)}, AI candidates={len(candidates)}")


def merge(args):
    packet = read_json(args.packet)
    review = read_json(args.review)
    if set(review) != {"results"} or not isinstance(review["results"], list):
        raise ValueError("Review must be an object with a results list")
    candidates = {row["row_key"]: row for row in packet["candidates"]}
    decisions = {}
    for row in review["results"]:
        if set(row) != {"row_key", "verdict", "code", "evidence"}:
            raise ValueError(f"Unexpected review fields: {row}")
        key = row["row_key"]
        if key not in candidates or key in decisions:
            raise ValueError(f"Unknown or repeated row_key: {key}")
        if row["verdict"] not in ("ok", "issue"):
            raise ValueError(f"Invalid verdict for {key}")
        if row["verdict"] == "issue" and (not text(row["code"]) or not text(row["evidence"])):
            raise ValueError(f"Issue needs code and evidence: {key}")
        decisions[key] = {"row_key": key, "kind": candidates[key]["kind"],
                          "id": candidates[key]["id"], "verdict": row["verdict"],
                          "code": row["code"] if row["verdict"] == "issue" else "OK",
                          "evidence": row["evidence"] if row["verdict"] == "issue" else ""}
    if set(decisions) != set(candidates):
        raise ValueError(f"Missing AI decisions: {sorted(set(candidates) - set(decisions))}")
    rows = packet["rules"] + list(decisions.values())
    rows.sort(key=lambda row: (row["row_key"].split(":")[0], int(row["row_key"].split(":")[1])))
    wb = Workbook()
    ws = wb.active
    ws.title = "check_results"
    ws.append(CHECK_HEADERS)
    for row in rows:
        ws.append(tuple(row[name] for name in CHECK_HEADERS))
    target = Path(args.out)
    target.parent.mkdir(parents=True, exist_ok=True)
    wb.save(target)
    print(f"Wrote {len(rows)} checked rows to {target}")


def read_checks(paths):
    rows = []
    for path in paths:
        ws = load_workbook(path, read_only=True, data_only=True).active
        headers = tuple(text(cell.value) for cell in next(ws.iter_rows(min_row=1, max_row=1)))
        if headers != CHECK_HEADERS:
            raise ValueError(f"Invalid check result columns in {path}")
        for cells in ws.iter_rows(min_row=2, values_only=True):
            if any(cell is not None for cell in cells):
                rows.append(dict(zip(CHECK_HEADERS, (text(cell) for cell in cells))))
    keys = [row["row_key"] for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate row_key across check files")
    return rows


def aggregate_prepare(args):
    rows = read_checks(args.checks)
    by_kind = Counter(row["kind"] for row in rows)
    by_code = Counter(row["code"] for row in rows if row["verdict"] == "issue")
    samples = defaultdict(list)
    for row in rows:
        if row["verdict"] == "issue" and len(samples[row["code"]]) < 2:
            samples[row["code"]].append({"row_key": row["row_key"], "evidence": row["evidence"]})
    metrics = {"total": len(rows), "issues": sum(by_code.values()),
               "by_kind": dict(sorted(by_kind.items())), "by_code": dict(sorted(by_code.items()))}
    ai_context = {"metrics": metrics, "issue_samples": dict(sorted(samples.items())),
                  "sample_limit_per_code": 2}
    write_json(args.out, {**ai_context, "rows": rows})
    write_json(args.ai_out, ai_context)
    print(f"Prepared summary: {metrics['total']} rows, {metrics['issues']} issues")


def aggregate_finalize(args):
    packet = read_json(args.packet)
    overview = read_json(args.overview)
    if set(overview) != {"overview"} or not text(overview["overview"]):
        raise ValueError("Overview must contain a nonempty overview string")
    wb = Workbook()
    metrics_ws = wb.active
    metrics_ws.title = "metrics"
    metrics_ws.append(("metric", "key", "count"))
    metrics = packet["metrics"]
    metrics_ws.append(("total", "", metrics["total"]))
    metrics_ws.append(("issues", "", metrics["issues"]))
    for group in ("by_kind", "by_code"):
        for key, count in metrics[group].items():
            metrics_ws.append((group, key, count))
    findings_ws = wb.create_sheet("findings")
    findings_ws.append(CHECK_HEADERS)
    for row in packet["rows"]:
        findings_ws.append(tuple(row[name] for name in CHECK_HEADERS))
    overview_ws = wb.create_sheet("overview")
    overview_ws.append(("AI overview",))
    overview_ws.append((overview["overview"],))
    target = Path(args.out)
    target.parent.mkdir(parents=True, exist_ok=True)
    wb.save(target)
    print(f"Wrote aggregate workbook to {target}")


def verify(args):
    expected = read_json(args.expected)
    rows = read_checks(args.checks)
    actual = {row["row_key"]: row["verdict"] for row in rows}
    if actual != expected:
        raise ValueError(f"Quality mismatch: expected={expected}, actual={actual}")
    print(f"Quality check passed for {len(actual)} rows")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--input", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--ai-out", required=True)
    p.set_defaults(func=prepare)
    p = sub.add_parser("merge")
    for flag in ("packet", "review", "out"):
        p.add_argument("--" + flag, required=True)
    p.set_defaults(func=merge)
    p = sub.add_parser("aggregate-prepare")
    p.add_argument("--checks", nargs="+", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--ai-out", required=True)
    p.set_defaults(func=aggregate_prepare)
    p = sub.add_parser("aggregate-finalize")
    for flag in ("packet", "overview", "out"):
        p.add_argument("--" + flag, required=True)
    p.set_defaults(func=aggregate_finalize)
    p = sub.add_parser("verify")
    p.add_argument("--expected", required=True)
    p.add_argument("--checks", nargs="+", required=True)
    p.set_defaults(func=verify)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
