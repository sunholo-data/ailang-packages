# Initial real-project maintenance pass — 2026-10-23

The published AILANG instrument works on actual project histories and finds repeat touches and supported repairs. **This pass cannot estimate an AILANG language advantage or lifetime token saving.** It is an evidence-availability pilot with a deliberately small convenience sample, not the parent design's random mature cohort or a controlled AI campaign. Existing eval benchmarks are excluded from the eligible corpus.

## Release and execution

[Package PR #156](https://github.com/sunholo-data/ailang-packages/pull/156) merged at `85363126d23b6a1e5b9139dcd186e9d8b618f47a`. `sunholo/maintenance_bench@0.1.0` was published and independently downloaded from the registry into a separate consumer. [Public registry metadata](https://registry.ailang.sunholo.com/api/packages/sunholo/maintenance_bench) is captured in [evidence/registry-metadata.json](evidence/registry-metadata.json): server compilation/effects pass, 1/1 contracts verified, zero skipped. There are 75 uncontracted exports; strict quality remains incomplete. Tarball SHA256 is `11575bf5e1ddc7934f205fa7c660601f9e15a355fb1c2aa7bd392dc08cd04760`.

Collection and analysis used the installed registry commands, with clean AILANG v0.54.17 at source `8f58117f265471584176e2aeb45996c2c9822577`; binary fingerprint is in each manifest. The collector and analytical runtime make no LLM calls, and no benchmark model trials were launched. This attended coding agent supplied the single-reviewer annotations and narrative; that work consumes agent tokens, which are not metered in this dataset. No Python/R statistical engine or GitHub connector was used. `gh` GET requests ran through the AILANG collector. `jq` prepared curated JSON, cluster metadata and explicitly reviewed annotations; native AILANG computes cohorts, lineage and metrics. Querying public metadata cannot measure the tokens used in this attended coding-agent conversation.

## Frozen collection and coverage

[protocol.json](protocol.json) was committed before collection. Five projects × the first ten closed PRs ordered by creation descending, at cutoff **2026-10-23 00:00 UTC**; merged_at determines acceptance. Four development cases were already familiar from package authoring, so this is explicitly exploratory, not sealed confirmation. Collection ran after the cutoff: captured bodies/reviews may contain later edits or discussion; there is no claim to an as-of-cutoff reconstruction of their text.

| Project / language | Closed PRs inspected | Accepted by cutoff | Eligible canonical changes | Mature at 30 days | Observed artifacts |
|---|---:|---:|---:|---:|---:|
| AILANG Parse / AILANG | 10 | 7 | 6 | 0 | 25 |
| Docparse / AILANG | 10 | 9 | 4 | 0 | 5 |
| Excelize / Go | 10 | 10 | 10 | 0 | 11 |
| Calamine / Rust | 10 | 9 | 8 | 0 | 9 |
| python-docx / Python | 10 | 0 | 0 | 0 | 0 |

Native JSON/Markdown reports are in [reports/](reports/). The accepted 35 rows yield 28 eligible and 7 excluded; all 28 eligible rows are censored. All five acquisitions are **incomplete by the page cap**, not complete histories. Both AILANG repositories use `sunholo-document-stack` as their shared cluster. Domain, activity and project-age differences are not controlled. No semantic task pairs exist.

The recent-closed-PR selector misses accepted Python work in this window. It also misses work merged manually without GitHub's merged_at: Calamine #729 has a maintainer comment describing a manual merge but merged_at=null. We leave it unaccepted here rather than manufacture acceptance time. The eligible corpus excludes Parse's shadow smoke, release notes/dependency-only changes, deployment infrastructure and Calamine's example-only line-ending change. Calamine #750 retains production paths while its example path is explicitly removed from the curated canonical file set. Raw GitHub language totals reported HTML/Shell for the AILANG projects; declared target language and reviewed paths govern this corpus.

## Touches, supported repairs and features

`review.tsv` records one reviewer's evidence-linked decisions over all 35 accepted observations, including exclusions. No independent annotation-agreement statistic or local before/after application reproduction is claimed. Every purpose label is **supported**, not confirmed; authorship stays unknown at episode/line level. Explicit AI-assistance disclosures are retained separately, including in Go and Rust: comparator languages are not an unaided-human control group. Missing disclosures are not evidence of human-only authorship.

| Project | Supported repair intent in eligible rows | Mixed | Feature | Migration |
|---|---:|---:|---:|---:|
| AILANG Parse | 3 | 3 | 0 | 0 |
| Docparse | 1 | 3 | 0 | 0 |
| Excelize | 9 | 0 | 1 | 0 |
| Calamine | 5 | 1 | 1 | 1 |

These manually reviewed composition counts describe selected PRs; they are not introduced-defect rates. Mixed releases are not forced into repair or feature. Security-related existing-behavior corrections retain repair intent with security context in notes. No introducing episode, local repair round, metered token, cost, duration or successful delivered outcome has been established for these rows. The native reports' zero **confirmed** repair counters mean unascertained under this review, not zero real bugs. Every group has zero known token/cost rows; known-value sums of zero do not mean zero expenditure.

Examples from the native lineage output and reviewed PRs:

| Artifact | Observed accepted touches | Interpretation |
|---|---:|---|
| Parse `docx_generator.ail` | 2 | Mixed image work #103, then supported list-numbering repair #112; not proof the latter was introduced by #103 |
| Parse `docx_parser.ail` | 2 | Supported correction #99, then mixed feature/type adaptation #100 |
| Docparse `mcp_tools.ail` | 3 | Mixed tool changes #229/#230, then supported ignored-outputPath repair #237 |
| Excelize `calc.go` | 6 | Six distinct accepted repair-intent PRs; not six repairs to the same defect |
| Calamine `src/xlsx/mod.rs` | 3 | Dependency migration #741, workbook-name repair #753, custom-property feature #750 |

Observed artifact identity begins inside this snapshot, not at file creation. None of these counts is an uncommitted edit-attempt count. Tests, derived mirrors and generated product documents do not become extra source defects.

## What this suggests about checks

[Parse #100](https://github.com/sunholo-data/ailang-parse/pull/100) describes missing record fields exposed by type checking during a feature change. The relevant field additions are present in the diff: evidence that checks can intercept integration mistakes, not a measured count of all prevented bugs. [Calamine #741](https://github.com/tafia/calamine/pull/741) similarly records feature-gated compiler errors during a dependency API migration. A type-checking benefit is not automatically unique to AILANG.

[Parse #112](https://github.com/sunholo-data/ailang-parse/pull/112) repairs user-visible Word list numbering; [Docparse #237](https://github.com/sunholo-data/docparse/pull/237) rejects a parameter that was silently ignored. These are domain/behavioral obligations beyond mere successful compilation. [Excelize #2456](https://github.com/qax-os/excelize/pull/2456) and [Calamine #747](https://github.com/tafia/calamine/pull/747) show bounds/domain failures in typed comparators. This pilot motivates real requirement-level oracles and meaningful contracts; it does not prove equivalent failures would or would not survive AILANG verification.

**No language delta is estimable here:** mature denominators are zero, repair introductions are unlinked, ascertainment is incomplete, project clusters are few, tasks are unmatched and usage traces are absent. A supported-repair PR share would mostly reflect selection and work mix.

## Roadmap candidates grounded in this pass

1. Add bounded merged-PR/calendar selection, plus capture of page counts and accepted-change sampling support. Preserve this original selector/protocol and version subsequent cohorts rather than changing the pilot after seeing its outcomes.
2. Trace a mature 30/90-day sample of accepted functional changes and later corrections. Adjudicate introducing links; double-review labels before a primary-outcome report. Calibrate mixed feature/migration handling and domain matching first.
3. In reporting, expose supported versus confirmed repairs and distinguish zero known-value rows from true zero usage. Make canonical-versus-all-acquired metric denominators explicit: v0.1 Parse reports 6 eligible rows but 7 unknown outcomes and 1 mechanical change because those group workload counters include the excluded smoke row. Do not interpret those counters as canonical-only totals. This needs a separately reviewed package fix/clarification, not an unannounced change to immutable 0.1.0.
4. Exercise real DOCX numbering, empty comment anchors, ignored parameters and dependency record/API changes as held-out maintenance tasks. These are candidate task families, not reused confirmation evidence or automatically comparable ports. Retire cases used for roadmap tuning from confirmation.
5. Join actual agent/session traces and metered usage to accepted changes for initial-generation, failed attempts, repair and verification. Count both application and dependency/infrastructure work in lifetime economics; public GitHub metadata alone cannot answer token savings.

No compiler/stdlib behavior changed in this pass. No benchmark model trials were launched. The next primary study requires a frozen mature cohort and reliable provenance; it is not an automatic extension of this convenience sample.

## Evidence handling and reproduction

[inputs/](inputs/) contains small curated snapshots and reviewed annotations sufficient to reproduce reports offline. They deliberately contain no full raw bodies or patches: source URLs and structured paths remain; full original gh snapshots are retained locally in `.ailang/state/maintenance-pilot-2026-10-23/` of the core workspace. [evidence/](evidence/) records original snapshot hashes and every captured endpoint/body digest. Public issue responses can contain copied notification links or personal details, so they are not blindly redistributed. Hashes of unavailable raw bodies alone are not an independent public audit; reviewers can inspect the linked upstream evidence and the local originals where available. Raw bodies and curated inputs are different evidence artifacts.

To reproduce, install the published version into a scratch consumer using the manifest/lock in evidence/, set `BENCH_BIN` to its installed maintenance-bench command, and run:

```sh
export AILANG_CACHE_DIR=/tmp/maintenance-pilot-compile-cache
BENCH_BIN="$HOME/.ailang/bin/maintenance-bench" sh reproduce.sh /tmp/new-maintenance-pilot-output
```

The script requires a fresh output directory and compares all ten regenerated native reports byte for byte with the committed results. Snapshot re-acquisition is a different operation: public API responses change over time. Frame hashes and the pre-collection protocol identify this acquisition. Input/report checksums bind the published artifacts, not their scientific truth. Cache directory override avoids this execution sandbox's read-only home-cache restriction; that restriction is not recorded as a language defect.
