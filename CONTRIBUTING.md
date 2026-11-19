# Contributing

This repository is primarily a coursework case study, but corrections and improvements are welcome.

## Ground rules

1. **Every number must be reproducible.** If you change data or a query, re-run
   `python analysis/run_analysis.py --figures` and commit the refreshed `results.json`, charts and
   `index.html` together.
2. **Keep the T-SQL the source of truth.** The Python layer mirrors the SQL; it does not replace it.
   Any logic change must land in `sql/` first.
3. **Quote expected results.** Each query block carries its expected row count in a comment so a
   reviewer can spot a regression.
4. **No real patient data.** The dataset is synthetic; never add identifiable health information.

## Adding a task or query

1. Create or extend the numbered script in `sql/` (`00`–`08` run in order).
2. Add the expected output as a comment.
3. If the query feeds the report, mirror it in `analysis/run_analysis.py` and re-generate outputs.
4. Update `docs/query-catalogue.md` and, where relevant, `docs/findings.md`.

## Commit style

`area: what changed` — e.g. `sql: add RANK() workload tie-breaker to Task 5`.
