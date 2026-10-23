# sunholo/maintenance_bench

Repeatable real-project maintenance analysis, written in AILANG. Collect facts with Git/`gh`, review labels separately, freeze inputs, and reproduce descriptive reports offline. No Python/pandas/R analysis engine, GitHub connector, or LLM is needed.

This is an **experimental research instrument**, not evidence that AILANG has fewer bugs. The shipped analytical fixture is synthetic. Four source-attributed real repairs are a discovery sample with no mature follow-up, unknown AI authorship, and no validated introducing changes.

## Run from this directory

Requires AILANG >=0.54.17; Git and gh are required only for acquisition. There are no external package dependencies.

```sh
ailang install --path . --bin-dir /tmp/maintenance-bin
/tmp/maintenance-bin/maintenance-bench verify-snapshot \
  assets/fixtures/analytical.snapshot.json \
  assets/fixtures/analytical.annotations.json \
  assets/fixtures/analytical.manifest.json \
  assets/fixtures/analytical.expected.json
/tmp/maintenance-bin/maintenance-bench compare \
  assets/fixtures/analytical.snapshot.json \
  assets/fixtures/analytical.annotations.json \
  assets/fixtures/analytical.manifest.json ailang python /tmp/new-comparison.json
/tmp/maintenance-bin/maintenance-bench report \
  assets/fixtures/real_cases.snapshot.json \
  assets/fixtures/real_cases.annotations.json \
  assets/fixtures/real_cases.manifest.json /tmp/new-real-cases.md
/tmp/maintenance-bin/maintenance-scale 1000 /tmp/new-timing.json
```

Output paths must be new: the CLI refuses to overwrite evidence. Supply absolute input paths when running from another directory. The installed commands resolve package modules independently of the working directory.

## Acquisition is explicit

```sh
maintenance-collect git /path/to/repo owner/repo ailang HEAD CUTOFF_MS 100 /tmp/new-git.json
maintenance-collect github owner/repo python CUTOFF_MS 5 2 /tmp/new-gh.json
```

Bounds are explicit; hitting a page/row cap marks the snapshot incomplete. `gh` uses GET endpoints only, capturing PR files, reviews, inline comments and issue discussion. No purpose or AI authorship is inferred. Languages are declared metadata; canonical source is filtered by supported language extension. Other-language bridges and ordinary docs remain unclassified rather than being called generated mirrors.

**Git committer time is not acceptance time.** Git snapshots have `timeBasis: commit`; accepted-change cohorts refuse them until every row has a reviewed `acceptedMs` annotation supported by acceptance evidence. GitHub snapshots use PR `merged_at`. Do not promote old branch commits to mature accepted changes. A full Git log still does not prove that all relevant defects or local repair attempts were observed.

`maintenance-bench` uses IO/FS/Env only; `maintenance-collect` additionally requires Process; `maintenance-scale` adds Clock but no Process/Net/AI. The package ceiling does not grant runtime authority. Direct runs can use `--process-allowlist git,gh` and bounded process timeout/output flags.

## Measures and interpretation

- Purpose, root cause, detection stage, authorship and evidence level are reviewed, versioned fields. Confirmed application repairs found after acceptance are separate from compiler/CI interceptions and toolchain defects.
- A repair link names the introducing episode, defect and visible round. Unknown introductions stay unknown. One five-file correction is one defect, not five.
- Exposure is fixed at 30 or 90 days. Recent changes are censored. Observed linked-repair incidence is a lower-bound observation, not true bug prevalence; unlabelled counts remain visible.
- Structured file changes preserve renames, copies and deletions. Reports include within-snapshot artifact identity, observed paths, total touches and confirmed repair touches. Path reuse after deletion creates a new artifact. Ordering is acceptedMs then episode id; unresolved ties are a limitation, not proof of original creation history.
- Cross-language task comparisons require explicit semantic pair/model/harness/trial identities. Missing mappings, mismatched contexts and unknown outcomes remain visible. No population confidence intervals or p-values in v0.1.
- Counts are checked from raw JSON lexemes before float conversion, then bounded to exact integers <=2^53-1. Fractions/exponents and duplicate object keys are refused. IDs/hashes remain strings. Reports state known-value counts, unavailable ratios, overflow, and unknown costs/outcomes. Reported micro-costs are not claimed to be metered billing.
- Report identity binds input digests, package/metric versions, declared compiler identity and comparison direction. Runtime identity must be externally attested; the package does not claim to inspect the running compiler automatically.

See [SCHEMA.md](SCHEMA.md), [fixtures](assets/fixtures/README.md), [DATA_SCIENCE_GAPS.md](DATA_SCIENCE_GAPS.md), [VALIDATION.md](VALIDATION.md), and [AGENT.md](AGENT.md). The real-world survey and held-out maintenance campaign remain separate work.

## Validate

```sh
make verify
make integration
make scale
```

`make quality` runs the package quality report; `make quality-strict` deliberately reports strict badges as failures. Version 0.1 carries an explicit experimental PUB011 contract-coverage limitation: meaningful contracts are not universal proofs. Native tests, properties and mutation controls are the main evidence for complex codecs/joins. No vacuous contracts are added to make a badge green.

Source availability on a PR/branch is distinct from a main-branch merge and a registry release. Registry upload is not part of this sprint's authorisation.
