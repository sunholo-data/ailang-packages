# Resource ownership: public maintenance task family

This is a **development/calibration adaptation**, not a held-out benchmark, a model result, or an exact replay of a Python historical bug. Its source requirement is document image-resource ownership from [ailang-parse #46](https://github.com/sunholo-data/ailang-parse/pull/46), repaired in [#77](https://github.com/sunholo-data/ailang-parse/pull/77). The merged [historical evidence](../../../mature-2026-10-23/evidence/verified-oracles.json) identifies introducing patch `38b09748426d7b194ca3cb8e88187f87673513f7`, accepted source `d8c04a66993d8abbe97a286be40ac975d1858557`, and repaired source `583e7d57cc53455af2268cd9fdb140507463941e`.

The bounded component receives already extracted image names/bytes; ZIP/PDF parsing is outside its responsibility. Both native arms use the same JSON protocol, byte inputs, operation schedule, cap units and lifetimes. Neither delegates its resource implementation to the other language. Python uses its standard library; AILANG uses its native stdlib. The starter owns inline bytes correctly. References S1–S3 each introduce the corresponding requirement and preserve previous obligations. Future task execution must copy only the selected starter/checkpoint and public checks, keeping reference solutions and external oracles outside the agent workspace. This repository alone does not enforce a hidden-test boundary.

## Run the offline qualification

Requires AILANG v0.54.18+ and Python 3.11+. The recorded run used AILANG v0.54.18 and Python 3.13. Each candidate is copied into an isolated temporary directory, compiled before execution, and receives its own resource directory. No network, provider, model, registry publication, or whole-platform build is involved.

```sh
sh qualify.sh --output /tmp/resource-qualification.json
python3 -m unittest -v oracle_test.py
```

From another directory, invoke this directory's absolute `qualify.sh` path. `AILANG_BIN` selects the actual native binary; the emitted runtime identity records it. Each subprocess has a 30-second timeout. Compilation, launch, timeout or malformed-output failures abort as infrastructure failures; only a successfully compiled, exit-zero candidate's failed semantic assertion counts as an expected negative control.

The qualifier runs 16 positive executions (four checkpoints × two native languages × two document orders) and 14 required negative executions (three prior-version no-ops plus four mutations, per language). All returned operation counts, names, bytes, file references and final file contents/lifetimes are independently checked. Twelve negatives retain a green public single-document check; cross-document ownership and later maintenance requirements need the stronger external oracle. The separate unit suite runs the actual taskpack with the oracle replaced by an always-pass function and requires qualification to fail at an expected-failure control.

## Frozen contract and inputs

[protocol.json](protocol.json) fixes the neutral input/result contract, bounded valid input domain, duplicate-active-ID rule and decoded-byte cap. [stages/](stages/) holds successive requests. [fixtures/](fixtures/) contains baseline and stage schedules frozen before native implementations. Fixtures cover binary bytes including zero/255, zero-byte images, repeated names within/across documents, Unicode document IDs, identical content, reordered documents, exact/over-limit caps, a rejected multi-image document followed by retry, empty documents, one-document release and ID reuse.

Each invocation starts with fresh state; **within that invocation** all operations share the native component's accumulated state. Reads after processing later documents use retained earlier references/files. The harness never resets a document between operations or repairs it from a reference. A future model trajectory will retain its own source across stages; these reference controls merely qualify task assets and do not claim to implement the stage executor.

## Checks, evidence and limits

- `public_check.py` checks single-document extraction/read. The three named native tests in each AILANG package exercise cap predicates. They are intentionally insufficient to prove cross-document semantics.
- `oracle.py` independently models authoritative input bytes and declared document lifetimes, and checks actual outputs/files. It never imports the candidate. Canonical file naming is an implementation choice; the oracle checks uniqueness, containment and exact bytes rather than a preferred hash.
- `qualify.py` records source/base digests, mutation patches, fixture/protocol/oracle digests, actual compiler identity, public-check verdict, semantic failure message, separate compile/public/execution/oracle timing and oracle assertion count. Peak memory is explicitly uncollected. Failed controls cannot be reported as a successful qualification. Timings are descriptive, not a cross-language speed claim.
- Native manifests/locks/effect ceilings and examples are inside each AILANG checkpoint. Pure `withinCap` has a verified contract; effectful `run` and `main` remain uncontracted and rely on the external checks. Verification JSON reports the SMT numeric model separately from runtime equivalence; it does not prove the FS implementation.
- No physical concurrency, RSS threshold, resource deduplication optimization, population bug-rate inference or language superiority is claimed. Known public controls are for development; future confirmation needs new frozen real requirements.

[VALIDATION.md](VALIDATION.md) records the actual qualified counts and tooling outcomes. [validation/](validation/) contains the recorded qualification and package-quality evidence; reruns write a newly chosen output path.
