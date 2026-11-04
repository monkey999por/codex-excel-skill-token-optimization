---
name: demo-summary
description: Check the fictional function, screen, and report Excel workbooks and make one aggregate workbook in the token optimization demo.
---

For `fixture/function.xlsx`, `fixture/screen.xlsx`, and `fixture/report.xlsx`, follow the `demo-check` skill's procedure for each workbook. Each `NAME.check.xlsx` must exist before continuing. Do not substitute the bundled `sample_reviews/` for AI judgments.

Run `python3 pipeline.py aggregate-prepare --checks out/function.check.xlsx out/screen.check.xlsx out/report.check.xlsx --out out/summary.packet.json --ai-out out/summary.ai.json`. Read only `out/summary.ai.json` for the AI overview. Write `out/summary.overview.json` as `{"overview":"..."}`. State broad patterns supported by the metrics and samples; the samples are capped at two per issue code, so do not claim to have inspected every finding. Then run `python3 pipeline.py aggregate-finalize --packet out/summary.packet.json --overview out/summary.overview.json --out out/summary.xlsx`.

Report `out/summary.xlsx` and concise counts. Do not print or reread all findings for the overview.
