# Supporting Release Scope and Safety

## Included

This public release includes the selected prediction freeze and hash sidecar; the primary analysis, independent oracle/scoring audit, calibration-only comparator and sensitivity scripts; dependency list; aggregate predictive, calibration, component and bootstrap result tables; integrity metadata; and documentation required to interpret the package.

## Intentionally excluded

- The `C.R.A._raw_analysis` workbook, at the researcher's explicit direction. It contains prompt text, raw model responses, oracle data and task-bank designs.
- The alternate historical prediction freeze, which was superseded and not used for primary scoring.
- Raw-response failure inventories and detailed filter-node audits that repeat response excerpts or reveal task-bank values.
- Archived machine-specific run logs with environment-specific paths or detailed failure examples.
- Research-paper PDF/DOCX, PDF README duplicate, ZIP archives, intermediate workbooks, and temporary validation files.
- Any credential, private account information, or unrelated project artifacts.

## Completeness statement

The checksum manifest at repository root covers the selected public release files (excluding the manifest itself). It does not imply that the local working folder is byte-for-byte mirrored. The workbook is not part of the public release; consequently the scripts require a researcher-held matching workbook for full execution.

## Limits

The source-data integrity record summarizes checks performed locally on the analyzed workbook before its explicit exclusion. SHA-256 validates byte identity, not data provenance or chronology. A manifest is only as useful as the correspondence between listed paths and committed files; the repository manifest is intended to be checked against the exact file bytes.
