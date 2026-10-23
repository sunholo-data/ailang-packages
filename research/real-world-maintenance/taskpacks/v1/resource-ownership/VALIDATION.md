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
