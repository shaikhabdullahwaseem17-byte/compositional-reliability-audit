# Supporting release scope

## Included

The public repository contains the selected 192-row prediction freeze and hash sidecar; primary analysis pipeline; independent oracle/scoring audit; aggregate result-table builder; calibration-only comparator; post-hoc sensitivity diagnostics; dependencies; aggregate result tables; integrity records; and reproduction documentation.

## Excluded

- The analyzed Excel workbook, including prompts, raw model responses, oracle records, and task-bank details. It remains a separate researcher-held file.
- The alternate historical prediction freeze.
- Raw-response failure inventories, raw response excerpts, and detailed task-specific row-level audit exports.
- Machine-specific run logs and intermediate local workbooks.
- The full research paper PDF/DOCX and temporary ZIP/build artifacts.
- Credentials, tokens, private account data, and unrelated project files.

## Reproduction boundary

The public scripts require a researcher-held workbook with the documented sheets. The workbook is not needed to inspect the selected freeze or aggregate tables, but it is required to rerun scoring and oracle reconstruction. The release-table builder writes aggregate outputs only and does not copy the workbook or raw responses.

## Interpretation limits

The checksum manifest verifies the committed public files. The prediction sidecar verifies the selected freeze's bytes. Neither checksum proves prospective timing. The source workbook lacks row-level run timestamps and exact per-response model-version fields, so those aspects of provenance cannot be independently established from the workbook.
