# Resource-family qualification evidence

Observed 2026-10-23 using AILANG v0.54.18, full commit `cd33d050b2276633c82624453309ebf7fcea9e2f`, teaching prompt v0.16.7, and Python 3.13. The actual binary SHA-256 is in [qualification.json](validation/qualification.json). This is offline fixture qualification, not model performance or a language-quality estimate.

| Check | Actual result |
|---|---|
| Native starter/reference compile | All four AILANG packages and four Python programs compiled; candidate copies use isolated per-run directories |
| Native named tests | 3/3 passed, 0 failed, 0 skipped in each AILANG package: 12 total; no generated properties claimed |
| Native examples | All four `examples/qualify_f1.ail` wrappers ran the shared public fixture successfully under IO/FS/Env |
| Smoke | Passed in all four AILANG packages |
| Positive semantic runs | 16/16 passed across both languages, all four checkpoints and both document orders; 1,136 independent assertions in the recorded run |
| Negative controls | 14/14 expected semantic rejections after successful compilation and exit-zero execution: 6 previous-version no-ops plus 8 specific mutants |
| Visible-green negatives | 12/14 negative executions pass the unchanged public single-document round-trip check and still fail the independent oracle |
| Host oracle tests | 4/4 passed, including actual full taskpack execution with the oracle replaced by always-pass; expected-failure accounting rejects the weakened oracle |
| SMT | `withinCap`: 1 verified, 0 counterexamples, 0 skipped, 0 errors in each package. The effectful `run` and `main` exports have no contracts and are not proved |
| Regular package quality | Passed in all four packages, with compile/interface/effects/release/docs/test/smoke sections recorded in `validation/*-quality.json` |
| Strict package quality | Does **not** pass: PUB011 for 2 uncontracted effectful exports per package; no additional gate is waived. `validation/*-quality-strict.json` retains exact reports |
| Formatting/locks | All native sources pass fmt --check; dependency-free package locks generated and checked |
| Registry/model work | None; these are unpublished native task fixtures |

The protocol, stage requests, shared inputs, independent oracle and oracle tests were written before native implementations. The initial full qualifier failed because the starter did not exist; that is recorded as an implementation-red result, **not** a semantic oracle kill. Later previous-version no-op controls supply real compiled semantic reds for each new stage. Expected negative failures are actual assertion failures, not parse/type errors or process exits.

Qualification records preserve exact source/base digests, mutation before/after text, protocol/fixture/oracle digests, public-check outcomes and the actual semantic failure message. Compilation, public check, candidate execution and oracle timings are separate; wall time includes surrounding qualification work. Peak per-process memory is explicitly uncollected rather than fabricated from cumulative child RSS. No memory/speed comparison is asserted.

The independent stages are stored as full native checkpoints to ensure the starter does not contain later implementations behind a stage switch. Consequently the source footprint is larger than the original small-component LOC estimate; these are separate qualification assets rather than a new application framework. There is no claim that a live agent has carried its own program across stages; that belongs to the next executor-integration sprint.

Replay from this directory:

```sh
sh qualify.sh --output /tmp/f1-qualification-replay.json
python3 -m unittest -v oracle_test.py
```

Every regenerated qualification must pass its positive and expected-negative controls before setting `qualified=true`. Writing a receipt is not permission to run a model campaign or promote these known public assets into sealed confirmation evidence.

## Amendment 2026-11-10: `cap` reads numbers with `getNumber` (std/json `JInt`)

AILANG's `std/json` gained `JInt(int)` (sunholo-data/ailang#2223, merged to AILANG `dev` and not yet released). On that compiler `decode` returns `JInt(16)` for an integer literal such as the fixtures' `"cap": 16`. Only fractional and exponent literals remain `JNumber`. Every checkpoint's private `cap` function matched `Some(JNumber(n))`, so on that compiler every integer cap took the `expected cap` arm. The S2 and S3 references then answered `byte_cap` / `invalid batch` where the frozen expected outputs say otherwise. The starter and S1 define `cap` but never call it.

What changed, in all four AILANG checkpoints (starter and references S1–S3): `cap` now reads `getNumber(j, "cap")`. `getNumber` exists on the pinned compiler, where it accepts `JNumber`, and on the new one, where it accepts `JInt` and `JNumber`. `JNumber` is dropped from the imports where nothing else uses it (starter and S1). Python arms, protocol, fixtures, stage requests, oracle, public check, qualifier and mutations are unchanged.

Behaviour on the pinned compiler is unchanged:
- Old and new `cap` were evaluated side by side on 22 decoded inputs. Those inputs cover a missing key, null, bool, string, array and object; 0, -0, 16, `16.0`, `1e3` and `1.6777216e7`; and -1, 1.5, 16777217, `2e7`, -16777216 and values above 2^53. The results and error strings (`expected cap` / `invalid cap`) are identical on v0.54.18 and v0.59.0.
- Each checkpoint's `examples/qualify_f1.ail` was run on all nine pack fixtures and 19 cap edge-case documents (4 × 28 runs). Before and after, on v0.54.18, stdout, exit code and the files written are byte-identical.
- On the new compiler, the amended checkpoints give exactly the v0.54.18 outputs. The previous sources differed in 62 of the 224 output and file records.

Re-frozen with the pack's own tooling, toolchain unchanged (v0.54.18 evidence and binary digest as recorded in `execution/development.ailang-toolchain.json`):
- `execution/write_development_manifest.py` was run with the checked-in toolchain evidence. As a null control, run on the unamended sources it reproduces the previous `development.plan.json` and `development.example.json` byte for byte. Changed:
  - starter `engine.ail` SHA-256: `55843394…7bf4` → `a9c8d18f…f485`
  - resource-ownership AILANG `starterDigest`: `ea0f6a0d…d1e3` → `816f90e9…c27b`
  - plan digest: `28b7fed2…625b` → `8a7b2b3c…9d04`
- `qualify.sh --output` regenerated the integration receipt `packages/maintenance-bench/validation/v0.2.0/resource-qualification.json` on AILANG v0.54.18 (commit `cd33d05`). It records:
  - 16/16 positive runs and 14/14 negative controls killed
  - checkpoint source digests `d94b9157…`, `309054fb…`, `265ef5a0…`, `fad1a2bb…` (previously `0a126cdd…`, `2faf799d…`, `9a6e51dc…`, `195ba048…`)
  - the release build's binary SHA-256 for macOS arm64, `f52b7176…`. The earlier receipt was produced by a different build of the same commit.
- `sh ../qualify.sh` (both families and both host-oracle suites) passes on v0.54.18 and on the new compiler.

The worker-stage files under `validation/` are historical evidence. They still bind the earlier sources and are not rewritten.

No model campaign has been scored against the previous freeze. The pack, execution README and maintenance-bench records describe only development qualification and scripted instrument controls. AILANG's adapter documentation states that live admission is closed, so no measurement is invalidated. This amendment is development maintenance, not a new confirmation freeze.
