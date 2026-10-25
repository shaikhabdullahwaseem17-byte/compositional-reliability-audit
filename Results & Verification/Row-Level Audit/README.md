# Row-Level Audit

This folder contains row-identified diagnostics supporting the aggregate results. The files are deliberately curated for readability; they do not replace the complete workbook or claim to reproduce every raw response.

## Files

- `composition_failure_inventory.csv` — one row per composition failure, with run ID, task family, model alias, graph structure, failure category, and first identifiable mismatch. Long raw-response excerpts are omitted to keep this audit index compact and focused.
- `task_family_success_summary.csv` — exact-success counts and rates by task family and model alias, pooled across the four graph structures.
- `filter_node_error_summary.csv` — counts of inexact FILTER_CHAR node values by model alias and structure, derived from the row-level filter-node audit.

## Interpretation cautions

- `Model_A` and `Model_B` are study aliases. Do not infer a uniquely verified provider/model version from them.
- A `STRICT_JSON_FAILURE` means the response did not meet the strict machine-readable response contract; it does not imply that every idea or calculation inside the response was wrong.
- The `FILTER_CHAR` patterns are descriptive observations within this task bank, not evidence that the same error distribution will generalize to other models or tasks.
- The primary outcome remains strict exact task success. Post-hoc embedded-JSON recovery is reported separately and does not replace it.
- The complete analyzed workbook remains the source for trial prompts, raw responses, oracle data, and full row-level scoring fields.
