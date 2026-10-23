# Audio 0.3.0 candidate: offline level preparation

Implemented 2026-10-23 on AILANG v0.54.18, commit cd33d05. This is the first
auto-level implementation slice; **not a registry release or a Loop Lab UI change**.
The published audio package remains 0.2.0 until an explicit release. The running
capture preview is unchanged. No AILANG core update was required.

## Behavior and integration boundary

[`levels.ail`](../../../packages/audio/levels.ail) adds checked pure measurement,
block accumulation, gain planning and preparation for mono/stereo clips:

- Whole-signal RMS, active-window RMS, sample peak and full-scale/over-range counts.
  Stereo energy is pooled without downmixing. Windows span successive blocks, and
  the final partial window uses its actual size.
- Off, PeakSafe and MatchRms with explicit linear targets, activity floor/minimum,
  maximum boost, peak ceiling and a decision reason. A below-floor/insufficient
  take is not boosted; required peak attenuation still applies. This threshold is
  not a noise detector, LUFS measure, compressor or continuously varying AGC.
- Scaled energy instead of directly squaring very large/small samples. Public
  accumulators, clips and policies are revalidated; cumulative frame/sample budgets
  apply. Finishing does not mutate state or flush partial windows.
- Preparation remeasures its actual clip, applies one linked channel gain and
  checks finite output/peak headroom. It does not accept a forged plan as authority.
  The host retains the immutable original and owns preview, undo and explicit commit.

Legacy synthesis, gated-RMS analysis, PCM quantization and byte pins remain intact.
This does not add plugin hosting, hum transcription, microphone controls or a WAV
export UI. Consumers can combine the new prepared Clip with the existing checked
PCM/WAV adapter for a deliberate file handoff to a DAW such as Ableton Live.

## Quality report, section by section

Source: [`quality.json`](quality.json), run with registry network access. JSON flag
must precede the package path: `ailang pkg quality --json packages/audio`.

| Section | Observed result |
|---|---|
| Compile | 24 files, pass |
| Contracts | 12/57 verified; 45 skipped (5 missing postcondition, 40 unsupported encoding); 0 refuted, 0 errors; 33 uncontracted exports |
| Interface | 130 signatures; v2 `288857c0489e83ce9f235a0263ef69b7af4ed55fc9dce1224e85b146eb1aa031` |
| Effects | Declared max `[IO]`, rank_max IO; IO is confined to smoke; every exported processor is pure |
| Release | `kind = feature`, nonempty `## 0.3.0` changelog section |
| Docs | AGENT.md and ai_summary present; reported agent_doc_exports_covered = 6 |
| Style | 89/89 exported functions pure (100%) |
| Tests | 11 files, 145 passed, 0 failed/skipped; attested execution |
| Smoke | Present and passed; attested execution |
| Badges/gates | PUB016: 45 unproved contracts; PUB011: 33 uncontracted exports; no gates |

Strict mode promotes the existing PUB011 warning to a gate; a normal passing report
does not mean the package is warning-free or fully verified. The final networked
report has no PUB023 export-overlap availability badge. Packaging-only release
preview is retained in [`publish-dry-run.txt`](publish-dry-run.txt); no upload is
authorized or claimed by a dry-run.

### Proof and runtime-contract scope

[`levels-verification.json`](levels-verification.json): **2/8 contracts verified**,
6 skipped, 0 refuted/errors, 0 uncontracted in this module's contract inventory.
The proved functions are `defaultConfig` and the private `boundedGain` arithmetic
helper. The six exported processing APIs are skipped for unsupported callee
encodings (parametric Result/records or higher-order functions). They are not proofs
of signal processing. The package-wide increase is 10/49 → 12/57 verified, with
the previous 33 uncontracted exports unchanged.

The verifier's float sort is Real and int sort Int; runtime equivalence is
`not_established`. These proofs do not establish IEEE-754 behavior, subnormal handling,
audio quality, all input coverage or physical timing. Public guards execute without
a contract flag. The four closed-form preparation checks in `prepareLevelsProbe`
also ran with `--verify-contracts` on interpreter and strict bytecode; both returned
`true true true true` in the retained runtime-contract logs. That is selected runtime
assertion coverage, not a claim that every contract was executed on every input.

## Test and reference evidence

[`native-tests.txt`](native-tests.txt): **145/145 pass, 0 skipped**. Strict bytecode
ran 134 named-test bodies with **0 evaluator fallback**; 11 properties ran on the
evaluator with 100 generated cases each. The new module adds 27 named checks plus
2 properties (29 total), including:

- Closed-form DC, sine, impulse, partial-window and silence measurements;
  below-floor/insufficient activity, boost versus peak decisions and exact Off bypass.
- Mono/stereo blocks of 1, 127, 128, 1024 and whole-clip frames, including stereo
  polarity cancellation hazards and repeated finish/append without window resets.
- Cumulative budgets, invalid configuration/policies, forged dimensions/state,
  NaN/infinity rejection, huge/tiny finite values and subnormal gain rounding.
- Preparation preserves original samples, channel identity/rate/frames and one
  linked gain; properties check bounded gain/headroom and partition invariance.

Unchanged inline DSP tests were separately reproduced: **12 total, 11 passed,
1 skipped**, 0 failed. `onePole_property_1` generated a negative cutoff violating
its precondition; it is not counted as passed. Six examples plus five properties
(100 cases each) pass. See [`dsp-inline-tests.txt`](dsp-inline-tests.txt).

[`check_reference.py`](check_reference.py) computes direct arbitrary-precision
Decimal sums of squares, independently of the AILANG scaled streaming recurrence.
Twelve deterministic fixtures cover pooled mono/stereo energy, inactive windows,
over-range samples, partial windows and huge/tiny values. Both engines agree on
all **24 fixture runs / 192 field comparisons**: exact counts/peaks, RMS relative
tolerance 1e-12, zero absolute tolerance. This is deterministic numeric evidence,
not an exhaustive corpus or a listening/device test. Raw output:
[`reference-and-timing.json`](reference-and-timing.json).

## Descriptive runtime measurements

Single CLI runs on the host identified in reference-and-timing.json, with runtime
contracts enabled. Includes compiler/startup, fixture/clip allocation, validation,
analysis, gain and output checks; it does not isolate DSP kernel cost or measure
callback deadlines, physical latency or browser-worker transfer costs.

| Engine | Mono duration at 48 kHz | CLI elapsed |
|---|---|---|
| Interpreter | 0.1 s | 797.503 ms |
| Strict bytecode | 0.1 s | 56.014 ms |
| Strict bytecode | 8 s | 1497.989 ms |
| Strict bytecode | 16 s | 2902.373 ms |

This is suitable initial evidence for deferred take preparation, not an audio
callback benchmark, universal latency promise or complete worker turnaround.
No native kernel/core request is justified by these measurements. Test the eventual
worker implementation and transfers before selecting that integration's runtime.

## Reproduction from repository root

```sh
ailang version
ailang lock --help # run `ailang lock` from packages/audio when regenerating
ailang check --package packages/audio
ailang test --strict-bytecode --package packages/audio
ailang test packages/audio/dsp.ail
ailang verify --json packages/audio/levels.ail
ailang pkg quality --json packages/audio
ailang run --quiet --relax-modules --verify-contracts --entry prepareLevelsProbe --args-json 0 packages/audio/_smoke.ail
ailang run --quiet --relax-modules --strict-bytecode --verify-contracts --entry prepareLevelsProbe --args-json 0 packages/audio/_smoke.ail
python3 design_docs/implemented/audio-levels-0.3.0/check_reference.py --benchmark
# From packages/audio: ailang publish --dry-run
```

Text test logs have ANSI styling stripped. The standalone reference probe uses
`--package-dir packages/audio` to resolve the package under development and
`--relax-modules` for its documentation-directory module name. It is not exported
package source. The benchmark probe refuses frame counts outside 0..768000.

Next consumer work: expose gain decisions on a private Loop Lab candidate and keep
an original/one-step undo; add committed WAV export for Live. Those are separate
host changes after this package foundation, with actual worker/UI evidence.
