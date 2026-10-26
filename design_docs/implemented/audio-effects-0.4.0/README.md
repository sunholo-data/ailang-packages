# Bounded delay and gain automation, audio 0.4.0 candidate

Implemented 2026-10-23 on AILANG v0.54.18 (`cd33d050b2276633c82624453309ebf7fcea9e2f`).
This is the implementation-time candidate snapshot. Audio 0.4.0 was subsequently
merged and published on 2026-10-26; see the [release record](../audio-release-0.4.0/README.md).
Loop Lab's released registry dependency remains 0.3.0. [Next AI/DAW steps](../../planned/audio-0.4-ai-daw.md).

## Behavior and boundaries

`delay` adds defaultDelayLimits/startDelay/processDelay/resetDelay. Integer delays
of at least one frame have separate finite per-channel histories. Recurrence:
`output = dry*x + wet*old`, `stored = x + feedback*old`. Feedback is -0.99..0.99;
dry/wet each 0..1. Finite headroom is retained, including above full scale;
nonfinite output/history returns a typed error. Tail duration is caller-selected
silence, and reset explicitly truncates it and starts a new logical budget.

Default delay caps are 96,000 history frames / 192,000 channel samples. Allocation
is checked before construction. Existing per-block/cumulative limits, rate/layout
and public-state guards apply. Batched ring writes with updateMany avoid copying
the entire history per sample. Full state validation still scans history each call:
O(channels*(blockFrames+delayFrames)) work for a nonempty call. It allocates; it is
an offline/reference processor, not an allocation-free callback implementation.

`automation` adds startGain/setGain/processGain. Finite linear gain 0..64 is linked
across channels. For an N-frame ramp, sample k=1..N uses absolute k/N; sample N
reaches target exactly. Zero frames is immediate on the next input. Retargeting
starts from the last delivered gain and preserves cumulative budgets. Block
partitioning does not change samples or final state. This is gain automation, not
filter/delay-time smoothing, a tempo API or a host scheduler.

No inference, provider credential, browser, track/session or device enters these
types. Existing synthesis, PCM byte pins and legacy filters remain unchanged.
See [AGENT.md](../../../packages/audio/AGENT.md) for complete domains and semantics.

## Executed evidence

| Check / quality section | Observed result |
|---|---|
| Compile | 32 files pass |
| Contracts | 16/71 verified, 55 skipped (5 missing postconditions, 50 unsupported encodings), 0 refuted/errors; 33 uncontracted exports |
| New helper proofs | delay.advanceCursor and automation.rampPosition verified |
| Interface | 154 signatures; v2 `106fa417c34c705e7c7069c8872d9cc76c5f46e2fea170ad0762cd06a205acca` |
| Effects | Declared max [IO], rank IO; 100 processing exports pure, IO used only by smoke |
| Release | Feature kind, nonempty 0.4.0 candidate changelog |
| Docs | AGENT.md and ai_summary present; report heuristic covers 7 exports |
| Style | 100/100 pure exported functions |
| Native tests | 192/192 checks across 14 files, 0 failed/skipped; 177 named tests on strict VM, 0 fallback; 15 properties with 100 cases each on evaluator, seed 0 |
| New checks | 26 named tests + 2 properties: impulse/tail, signed feedback, stereo independence, partitions, reset, retargeting, invalid/forged states, budgets and overflow |
| Inline DSP suite | Unchanged: 11 passed, 1 precondition-generator skip, 0 failed; separate from 192 |
| Smoke | Executed and passed; new effectsProbe returns `true true true` on both engines with runtime contracts |
| Headless reference | Python's independent scalar recurrence and struct/PCM16 writer agree with both AILANG engines; runtime contracts enabled |
| Consumer compatibility | Isolated Loop Lab clone with temporary path dependency: 10 native + 45 Node + 6 Python tests, smoke and quality pass; released consumer/preview unchanged |
| Gates / badges | No gates; PUB016 (55 unproved), PUB011 (33 uncontracted exports) |

[quality.json](quality.json) is the full executed report. Its registry-overlap
lookup was sandbox-blocked (PUB023). [quality-online-no-run.json](quality-online-no-run.json)
reruns structural/proof/registry checks with network access; PUB023 is absent.
Its tests/smoke were explicitly not rerun, so their execution evidence is the full
report and [native-results.json](native-results.json), not the no-run report.
[verification.json](verification.json) gives per-function reasons.
[consumer-compatibility.json](consumer-compatibility.json) records local consumer scope.

The seven new public APIs are not Z3-proved: their contracts contain unsupported
record/Result/higher-order encoding. Helper proofs use mathematical Real/Int, not
IEEE-754 equivalence; tests/runtime guards do not establish perceptual or physical
audio quality. Registry validators do not execute attested tests/smoke.

## Delivered audio fixture

[headless-example.json](headless-example.json) records a synthetic eight-sample
24 kHz speech/model PCM stand-in, an 8-frame fade, 120-frame echo and 720 explicit
silence frames for a truncated tail. Delivered output is 728 mono frames, 1,500 WAV
bytes, SHA-256 `86ab68092f4dbb5342e1200a3ee09b8a2843ad9f13d6ed7eb588849ec15eaad8`.
Decoded quantized output has sample peak 0.21875 and RMS about 0.01254532112.
Byte identity does not validate model meaning or human speech/music quality.

Reproduce from repository root:

```sh
ailang test --strict-bytecode --package packages/audio
ailang pkg quality packages/audio
python3 design_docs/implemented/audio-effects-0.4.0/verify_examples.py
python3 design_docs/implemented/audio-effects-0.4.0/verify_examples.py --timings
```

The audio-specific GitHub workflow runs compile, native/inline tests, independent
reference and full quality without an inference account. Hosted results must be
observed separately; adding a workflow is not a CI pass.

## Performance scope

[timings.json](timings.json): three whole-CLI runs per engine/delay on Darwin arm64;
each processes 49,152 stereo frames at 48 kHz in twelve 4,096-frame blocks. Includes
startup, compilation, input/state validation, allocation and processing. Runtime
contracts off for timing probes; enabled for reference/probe correctness above.

| Delay frames | Interpreter median ms | Strict VM median ms |
|---|---:|---:|
| 1 | 3607.5 | 249.4 |
| 127 | 2468.5 | 135.3 |
| 48000 | 8860.8 | 287.9 |
| 96000 | 15335.7 | 477.8 |

These descriptive results favour the VM for preparation. They do not isolate DSP
kernel time, prove callback deadlines, measure GC tails, or establish performance
for 128-frame callbacks, another host or a native plugin. No new browser soak or
physical input/output latency result is claimed.

## Upstream core feedback

The minimal [record-Eq reproduction](core-record-eq-repro/model_test.ail) passes a
named test on strict VM but fails the property evaluator when an equality helper
compares an imported record: `expected TaggedValue, got *eval.RecordValue`.
Sent to canonical shared AILANG user inbox as `inbox_1792789272676_e056054b`
using the ailang-feedback skill. Explicit field comparisons keep this effect group
portable without waiting for a core fix. Direct record comparison without the
helper did not reproduce; the report preserves that distinction.
