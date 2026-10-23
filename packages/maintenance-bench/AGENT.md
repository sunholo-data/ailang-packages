# sunholo/maintenance_bench

Use for repeatable, descriptive real-project maintenance analysis and for exploring AILANG data handling. Do not use it to certify that a language is bug-free or to infer AI authorship from style.

## Public modules

- `sunholo/maintenance_bench/types`: snapshot, reviewed annotation, manifest, episode and structured file-change boundaries.
- `sunholo/maintenance_bench/codec`, `strict_json`: strict count-only input documents, nullable states, exact count lexemes, schemas and evidence hashes.
- `sunholo/maintenance_bench/observation`: explicit unknown-filled acquisition constructors.
- `sunholo/maintenance_bench/cohort`: apply reviewed annotations, validate links, reject commit-age acceptance claims and partition fixed-window exposure.
- `sunholo/maintenance_bench/lineage`: observed chronological artifact/touch history, renames, copies and deletion/recreation.
- `sunholo/maintenance_bench/metrics`, `compare`: descriptive counts, bounded sums, median, rates, semantic task pairing and deltas.
- `sunholo/maintenance_bench/report`, `report_json`, `verify_snapshot`: pure preparation/analysis, stable JSON/Markdown and independent expectation checks.
- `sunholo/maintenance_bench/snapshot_io`: fallible file input and single-writer new-path output; not a concurrent immutable object store.
- `sunholo/maintenance_bench/collect_git`, `collect_github`, `process_read`: bounded Process adapters using argument arrays and gh GET endpoints.
- `sunholo/maintenance_bench/reference`, `benchmark`: visibly synthetic analytical and scale inputs, never language-quality evidence.
- `sunholo/maintenance_bench/cli`, `collect_cli`: installed command entry points.

## Library use

```ailang
import pkg/sunholo/maintenance_bench/report (analyse)
import std/result (Ok, Err)
-- analyse(snapshotText, reviewedAnnotationText, manifestText, "ailang", "python")
-- returns Result[{json:string,markdown:string},string]; it is pure.
```

Use relative imports inside this package and `pkg/sunholo/maintenance_bench/...` from a consumer. Read README for executable CLI commands and SCHEMA for complete input examples. All analysis functions are pure. FS is limited to snapshot_io, Process to explicit collection, Clock to benchmark timing, and IO/Env to command entry points; there is no Net or AI effect.

Errors are data/collection failures, not empty cohorts. Inspect exitCode and truncation on Process results. Reject malformed fields; never call JSON repair or permissive getters on study inputs. IDs stay strings. Reviewed unknowns remain explicit null. Declared compiler identity needs external attestation, and metric direction is left minus right.

Run native package tests and properties, all source inline test tables if added, offline smoke and independent fixture verification. `pkg quality --strict` exposes experimental contract-coverage warnings; do not call this package fully proved. See VALIDATION for actual results and DATA_SCIENCE_GAPS for reproducible limitations. Source publication, packaging dry-run and registry acceptance are separate outcomes.
