# Foundation evidence, 2026-10-23

This is a new metric-v2 replay of the existing real Parse observation frame, not a new sample or model trial. It uses the original immutable mature-study source and explicitly selects the original three index IDs. Analysis is native AILANG via maintenance-ledger; the index JSON projects already reviewed source intent/merge timestamps. The mixed job retains performance plus feature labels.

The [source-pinned scoped report](parse.scoped-v2-source-pinned.json) accounts for 3 mature sampled changes, 14 later artifact-touch changes in their 30-day windows, 1 confirmed repair touch and 13 touch changes with unknown intent. It records one confirmed introduced-defect link; this is an observed lower bound, not a 1/3 language bug-rate estimate. The 53-row workload frame includes 31 canonical rows and 3 known token rows totaling 1,114,042 recorded tokens; 50 rows have unreported tokens. Cache/model billing remains unestablished. Source acquisition is incomplete and local edit coverage is unobserved.

These new named scopes explain the old denominator/workload mismatch without rewriting earlier reports. All six original reports were separately replayed byte for byte using official checksum-verified v0.54.17 and actual v0.1.0 source/lock. The new package never fabricates a 0.1.0 identity to obtain the old bytes.

Replay from repository root with the v0.2 source checkout:

```sh
ailang run --caps IO,FS,Env --entry main packages/maintenance-bench/ledger_cli.ail index \
  research/real-world-maintenance/mature-2026-10-23/inputs/parse.all.snapshot.json \
  research/real-world-maintenance/foundation-2026-10-23/parse.index-v2.json \
  'AILANG v0.54.18 cd33d050b2276633c82624453309ebf7fcea9e2f; maintenance_bench source 40e1e74; externally attested' \
  /tmp/new-parse-scoped.json
cmp research/real-world-maintenance/foundation-2026-10-23/parse.scoped-v2-source-pinned.json /tmp/new-parse-scoped.json
```

Taskpack qualification and artificial 8/24 ledger/economic controls are separate evidence. Their invented dollar/token differences validate accounting only and must not be combined with this observational sample into a language advantage claim.

The original parse.scoped-v2.json is the earlier development replay before external source pinning. The source-pinned replay preserves identical metric values while binding declared analysis identity to tested implementation40e1e74; provenance.json records the full commit, lock and runtime fingerprints. The reportId is not a self-attesting build signature.
