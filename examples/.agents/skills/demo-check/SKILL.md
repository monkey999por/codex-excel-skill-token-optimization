---
name: demo-check
description: Check one fictional specification Excel workbook in the token optimization demo.
---

For one input workbook under `fixture/`, produce one check workbook under `out/`.

1. Run `python3 pipeline.py prepare --input fixture/NAME.xlsx --out out/NAME.packet.json --ai-out out/NAME.ai.json`.
2. Read only `out/NAME.ai.json` for AI decisions. For each candidate, compare `description` with `expected_result`. Return `issue` only for a clear contradiction; otherwise `ok`. Write `out/NAME.review.json` with exactly `{"results":[{"row_key":"...","verdict":"ok|issue","code":"OK|CONTRADICTION","evidence":"..."}]}`. Include every candidate exactly once. For `ok`, use `OK` and an empty evidence string. For an issue, give a short evidence phrase drawn from the row. Do not use `sample_reviews/` when making judgments.
3. Run `python3 pipeline.py merge --packet out/NAME.packet.json --review out/NAME.review.json --out out/NAME.check.xlsx`.
4. Report the output path and any validation error. Do not paste full workbook contents into the reply.

Keep row IDs and results in files. Do not read the workbook or packet into the model context when the compact AI input suffices.
