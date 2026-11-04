#!/usr/bin/env python3
"""Summarize actual Codex `exec --json` usage from one or more JSONL traces."""

import argparse
import json
from pathlib import Path


FIELDS = ("input_tokens", "cached_input_tokens", "cache_write_input_tokens",
          "output_tokens", "reasoning_output_tokens")


def summarize(path):
    totals = {key: 0 for key in FIELDS}
    turns = 0
    failed = False
    for lineno, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{lineno}: invalid JSONL") from exc
        if event.get("type") == "turn.completed":
            usage = event.get("usage")
            if not isinstance(usage, dict):
                raise ValueError(f"{path}:{lineno}: completed turn has no usage")
            turns += 1
            for key in FIELDS:
                totals[key] += int(usage.get(key, 0))
        elif event.get("type") in ("turn.failed", "error"):
            failed = True
    if turns == 0:
        return {"trace": str(path), "status": "no_completed_turn", "usage": None}
    totals["total_tokens"] = totals["input_tokens"] + totals["output_tokens"]
    totals["uncached_input_tokens"] = totals["input_tokens"] - totals["cached_input_tokens"]
    if totals["uncached_input_tokens"] < 0:
        raise ValueError(f"{path}: cached input exceeds input")
    return {"trace": str(path), "status": "partial_or_failed" if failed else "completed",
            "completed_turns": turns, "usage": totals}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("traces", nargs="+", type=Path)
    parser.add_argument("--json", action="store_true", help="Print machine-readable results")
    args = parser.parse_args()
    results = [summarize(path) for path in args.traces]
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return
    print("trace\tstatus\tinput\tcached_input\toutput\ttotal")
    for row in results:
        usage = row["usage"]
        values = (usage["input_tokens"], usage["cached_input_tokens"],
                  usage["output_tokens"], usage["total_tokens"]) if usage else ("NA",) * 4
        print("\t".join(map(str, (row["trace"], row["status"], *values))))


if __name__ == "__main__":
    main()
