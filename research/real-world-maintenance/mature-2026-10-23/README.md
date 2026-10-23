# Mature real-project results — 2026-10-23

**We now have measured maintenance usage, a reproduced AI-maintainer regression in AILANG, and a real cross-project touch comparison. These results do not support a claim that AILANG programs have fewer bugs.** They also do not establish that AILANG is worse: project/task mix and coverage differ, and only three mature AILANG PR changes qualify.

This extends the earlier availability pilot without changing it. It uses real application/library histories, not the language-development evals. No new model trial was launched. This attended coding agent selected and interpreted evidence; its research effort is outside the historical task counters below.

## 1. Real maintenance tokens

The repo-filtered chain query returned no rows, but task-ID lookups recovered the actual execution records. Each public PR identifies the coordinator task/branch; the chain contains one completed execution stage. We verified that input+output equals its recorded total and did not add parent and stage totals together.

| Accepted AILANG Parse work | Recorded input tokens | Recorded output tokens | Total | Recorded turns |
|---|---:|---:|---:|---:|
| [#44](https://github.com/sunholo-data/ailang-parse/pull/44): replace quadratic Markdown string accumulation | 172,053 | 1,746 | 173,799 | 14 |
| [#45](https://github.com/sunholo-data/ailang-parse/pull/45): reduce worksheet memory retention | 443,436 | 10,432 | 453,868 | 49 |
| [#46](https://github.com/sunholo-data/ailang-parse/pull/46): move retained image bytes into files, add resource cap | 474,442 | 11,933 | 486,375 | 75 |
| **Recorded total** | **1,089,931** | **24,111** | **1,114,042** | **138** |

These are task execution counters, not complete program-lifetime consumption, unique uncached input, provider-reconciled billing, or human labour. Model/cache provenance is not established in the retrieved summaries. Reported cost scalars are retained in [evidence/real-task-usage.json](evidence/real-task-usage.json), explicitly unverified for billing; there is no cost-per-success claim. The chains still say pending_approval despite public merged PRs, so we do not use that stale chain state to infer delivery or calendar completion time. No approval state was changed.

We have no equivalent Go/Rust task telemetry, and the later image repair's tokens are unknown. Thus **there is a real AILANG maintenance-effort baseline, but no honest token-saving delta yet**. In particular, the 486,375 recorded tokens for #46 do not include the subsequent #77 repair.

## 2. Mature changes and repeated touches

[protocol.json](protocol.json) was committed before outcome inspection. Index changes merged from January 1 through September 22, 2026 have at least 30 days before the fixed October 23 cutoff. We fetched all merged-PR search pages through October 22 and their structured file lists for projects with eligible indices. Search returned no incomplete_results and fetched counts matched totals. That is an exhausted **PR search frame**, not complete repository maintenance ascertainment.

Eligibility uses production target-language paths, excluding tests, examples, docs and derived copies. The AILANG frame is a census; larger frames use the first 12 by SHA256(`mature-2026-10-23-v1|repo#number`). Selection does not use fix labels or follow-up outcomes. The native AILANG analysis recomputes the selection and checks the published IDs/order against it. A source touch includes direct path overlap and a directly recorded rename from the original path, not arbitrary transitive function lineage.

| Project | Eligible mature PR frame | Selected | Selected changes whose source was touched by another merged PR within 30 days | Observed fraction |
|---|---:|---:|---:|---:|
| AILANG Parse | 3 | 3 | 3 | 100.0% |
| Docparse | 0 | 0 | unavailable | unavailable |
| Excelize / Go | 76 | 12 | 9 | 75.0% |
| Calamine / Rust | 46 | 12 | 8 | 66.7% |
| python-docx / Python | 0 | 0 | unavailable | unavailable |

The descriptive **touch-proxy** differences are AILANG Parse minus Excelize **+25.0 percentage points**, and minus Calamine **+33.3 points**. They provide no signal of fewer AILANG touches in this small panel. They are **not defect-rate or causal language-effect estimates**. All three AILANG indices came from one resource/performance audit; comparator indices span different kinds of work and calendar periods. Shared large modules are more likely to be touched. A repeated touch can be a feature, migration, refactor, duplicate integration or unrelated defect repair.

For example, #45's XLSX source has five later PR touches, #44's Markdown source three, and #46's image/parser source ten. These are 18 index-to-follow-up edges across 14 distinct follow-up PRs, not 18 defects. #51 adds colour support; #60 integrates other branches; #100 combines features and type repairs; #97/#98 address the same reported comment defect. We do not turn every overlap or every corrective PR into a new introduced bug. Later Go/Rust overlaps remain candidate evidence with uncertain causal labels rather than being counted as clean changes.

The PR-only AILANG sample is especially incomplete: local main history contains many direct source commits before September 23. We inspected this to explain the frame limitation, not to assign unverified acceptance dates to commits. Public merged-file lists also describe the API's current PR comparison; exact accepted source trees were independently pinned for the causal reproductions below. Collection happened after the cutoff, so current PR text can include later edits. These issues prevent a population defect-rate denominator.

Native results: [reports/mature-touches.json](reports/mature-touches.json). The released package separately reports three mature AILANG indices, 28 recent/censored canonical changes, and the one confirmed link below in [reports/parse-linked-repair.json](reports/parse-linked-repair.json). Its observed linked-repair value is 1/3 for this tiny PR panel. That is one verified positive observation, not proof the other two changes are bug-free or a comparable 33% language bug rate. Comparator causal introductions have not been fully adjudicated; they are not zero.

## 3. Reproduced AILANG regression: image ownership

**Introduced:** accepted [#46](https://github.com/sunholo-data/ailang-parse/pull/46), September 17, merge `d8c04a66993d8abbe97a286be40ac975d1858557`. Its agent task is the third telemetry row above. The [introducing patch](https://github.com/sunholo-data/ailang-parse/commit/38b09748426d7b194ca3cb8e88187f87673513f7) adds extractMediaToFiles and names each file `docparse-img-<counter>` with a counter starting at zero per document.

**Corrected:** accepted [#77](https://github.com/sunholo-data/ailang-parse/pull/77), September 29, merge `583e7d57cc53455af2268cd9fdb140507463941e`. It names images by content hash. The public PR reports the earlier document's image path being overwritten by a later document. The correction arrived about 12 days after acceptance, within the fixed window. We use PR opening time as an observed public report timestamp/latest-known detection bound, not an invented first-discovery time.

We downloaded the exact accepted zip_extract and document modules, independently of local branch history. A requirement-derived AILANG probe calls the real production extractMediaToFiles twice on two minimal ZIPs containing different valid PNGs under the same entry name. It then checks that the first result still resolves to the first PNG's bytes. Both historical sources and the probe pass type/effect checking on the pinned modern AILANG runtime.

| Source | Type/effect check | Paths equal across the two documents | First image still belongs to its document | Oracle exit |
|---|---|---|---|---:|
| Introducing source | Pass | true | **false** | 1 |
| Repaired source | Pass | false | **true** | 0 |

This establishes a concrete causal regression introduced by an automated AILANG maintainer change and repaired later. The source addition, path collision and correction are inspectable, rather than inferred from a fix title or same-file overlap. It tests a production component through a small harness, not the entire hosted application, historical renderer or deployment. It uses AILANG v0.54.17 rather than claiming a recreation of the historical compiler environment. Authorship identifies the automated maintenance episode, not every original line in the application.

The type and effect signatures were valid; the missing obligation was **cross-document ownership of an external resource**. This points to scoped/content-addressed resource helpers and an ownership regression oracle. It does not justify abandoning type checking or claiming all similar defects escape a properly specified contract.

## 4. Reproduced Rust regression: internal whitespace

[Calamine #671](https://github.com/tafia/calamine/pull/671) changed whitespace handling on July 2. [#673](https://github.com/tafia/calamine/pull/673) explicitly identifies and corrects its introduced regression on July 6. This is an additional source-known case, **outside the hash-selected index**, not an extra event in a convenient denominator. In particular, #673 touching the same module as sampled #621 does not establish that #621 caused it.

We built the true pre-fix parent `058cb507c8d74541f96d6439b6abd80e52f0c058` and repaired `bec70ca56621a6aab429d676a14ee8db5b1a3c1c` with identical Cargo manifests and the captured dependency lock, Rust 1.98.0. The same requirement-derived tests and updated upstream input fixture run against both production sources. `<t>&#26085;&#26399; &#26102;&#38388;</t>` must retain its internal space.

- Original focused whitespace tests on pre-fix production: **2 pass**.
- New inline/shared-string checks on pre-fix production: **2 fail**, returning `日期时间` instead of `日期 时间`.
- Identical new checks on repaired production: **2 pass**.

We did not run or claim the whole project suite. The fixture/new oracle is added to the pre-fix test harness; production source is unchanged. Each revision uses a fresh separate target directory. An initial shared-target attempt misleadingly reused a build artifact, and using PR.base.sha initially selected a different dependency manifest; neither is accepted as final evidence. The reproducible script uses the actual parent, identical lock and isolated builds. This is another real typed-language semantic regression that needed a requirement-specific oracle, not proof of either language's relative defect prevalence. Rust authorship remains unknown.

## Implications and next evidence

1. **Current hypothesis verdict:** no demonstrated AILANG advantage on bugs or total tokens. We have a confirmed escaped AILANG regression, concrete maintenance effort and a touch proxy pointing upward in this selected panel; causal cross-language inference remains unsupported.
2. **Checks that help:** [Parse #100](https://github.com/sunholo-data/ailang-parse/pull/100) describes missing-record-field mistakes intercepted during feature integration. This remains source-supported rather than locally reproduced here. Shape checks and semantic/resource oracles address different failures. Do not equate type-check success, test count or unrelated proof count with application correctness.
3. **Roadmap evidence:** reusable safe image-resource ownership and byte-preservation oracles; diagnostics for repeated quadratic string accumulation and evaluator frame retention; trace linkage from accepted PR/commit to agent task, model/cache/billing metadata and later repair. These findings warrant scoped designs, not automatic compiler changes.
4. **Get a representative comparison:** extend beyond PR-only first-party history using reviewed mainline/release acceptance evidence; calibrate source-role and repair labels independently; match functional task families and actual agent configurations. Do not promote commit dates to acceptance timestamps. Freeze and price any new paired model campaign separately.

These cases are now exposed development evidence. They may guide the roadmap or demonstrate a benchmark runner, but must not silently become sealed confirmation tasks for a future improvement claim.

## Reproduce and audit

The study consumer pins sunholo/maintenance_bench@0.1.0. Native AILANG performs final hash selection, temporal joins, denominators, token aggregation, median and proxy deltas. Host preparation only normalises API records, applies production-path eligibility and attaches explicitly sourced task metadata; native selection independently checks the prepared index. Source links/hashes are published; full API bodies and internal telemetry are retained in the core workspace's ignored `.ailang/state/maintenance-mature-2026-10-23/` bank, not copied into the public dataset. No private chat or credentials are included. Public readers can rerun the component reproductions; internal token records are first-party attestations, not independently public provider billing data.

- Study report replay: set AILANG_BIN and BENCH_BIN, then `sh reproduce.sh /absolute/new-output`. All six reports must match byte for byte.
- Historical source probes: `sh reproductions/reproduce_cases.sh /absolute/new-case-output`, with AILANG_BIN set. Requires gh, Python standard library for fixture ZIP generation, Rust/cargo, jq and network for immutable public source/dependency downloads. It checks expected failure codes, not merely nonzero exits.
- Analysis validation: native check and fmt pass; **10 native checks (nine examples plus one generated contract property with 100 cases), zero failures/skips; 1 SMT contract verified, zero counterexamples/skips/errors**. Two exported study functions are uncontracted. This is analysis validation, not proof of the studied applications.
- The released library's experimental contract-coverage limitations remain unchanged; no registry version or compiler/stdlib semantics changed in this study.

A supplemental [single-reviewer intent ledger](evidence/reviewed-ailang-followups.tsv) records all 14 distinct AILANG follow-up PRs, including duplicate/integration cautions and a supported repair-of-repair case. Only #77 has been independently executed as a causal oracle here; the other intent proposals are not silently promoted into confirmed native defect counts. Comparator overlap labels remain unadjudicated.
