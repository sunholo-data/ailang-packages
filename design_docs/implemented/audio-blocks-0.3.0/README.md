# Generic stateful block filters, audio 0.3 candidate

Implemented 2026-10-23 on AILANG v0.54.18. Loop Lab has moved to
[its application repository](https://github.com/sunholo-data/ailang-loop-lab);
this increment adds generic audio processing independently of that UI.
Audio 0.3 remains unpublished.

## Public behavior

`sunholo/audio/block` adds four pure checked APIs: `defaultBlockLimits`,
`startFilter`, `processFilter` and `resetFilter`. LowPass/HighPass keep one
history value per mono/stereo channel; FilterBypass preserves exact sample bytes.
Input/output rate, layout and frames are preserved. Empty blocks keep history;
reset flushes history and starts a new logical-stream frame counter. No device,
clock, track count, tempo or AI provider enters the API.

Limits default to 4096 block frames, 8192 block samples and 2147483647 cumulative
frames. Ordinary guards validate limits, state, cutoff, shape, rate/layout,
finite inputs/output and arithmetic overflow. Finite headroom is retained; integer
export remains explicit. High-pass arithmetic can exceed finite float range for
extreme headroom, and returns a typed error. Low-pass scales before adding to
avoid a naive opposite-extreme subtraction overflow. Legacy DSP order is unchanged.

The one-pole recurrence is `a=1-exp(-2*pi*cutoff/rate)`,
`low=(1-a)*previous+a*x`; high-pass is `x-low`. This is not a biquad or an exact
digital -3 dB cutoff claim across all frequencies. Low/high cutoff is 1e-6..rate/2
Hz; bypass allows 0..rate/2. Rates are 1..384000. Caller-selected budgets are not
total-heap/CPU/deadline guarantees, and resetting starts a new logical budget.

State/history is public and structurally validated, not authenticated. Filter tails
remain in state; callers explicitly process silence to render them or reset to
discard them. Parameter smoothing, delay, resampling and general graph/streaming
engines are subsequent work. There is no callback-throughput claim here.

## Generic generation/AI-output examples

[`examples/block_pipeline.ail`](../../../packages/audio/examples/block_pipeline.ail)
is a headless consumer with no effects:

- `recipeDemo`: checked JSON as a model might propose → bounded procedural render
  → Clip → filter → level plan/preparation → measured PCM16 WAV identity.
- `pcmDemo`: fixture s16le as a speech/model adapter might return → checked Clip
  import → the same processing/encoding path.

The inputs are analytic fixtures, not recorded speech or actual neural inference.
An effectful `std/ai`/provider adapter can supply supported audio/recipe data; DSP
stays pure. Model meaning, quality and provider formats remain separate concerns.

[`headless-examples.json`](headless-examples.json) records both entries on both
engines with runtime contracts enabled. Results are identical on this tested host:

| Entry | Frames/rate | Delivered WAV | SHA-256 |
|---|---|---|---|
| PCM fixture | 8 / 24000 Hz | 60 bytes | `f3164973bd7de4e38d4a5f10dac80c8d4a3348dc5fcdd89b4ed7064b53108427` |
| Recipe fixture | 240 / 24000 Hz | 524 bytes | `63a23c667af2a63a147a424cfefcf266341a3d5677f084dea71f38af2cb3a92c` |

Both have measured pre-quantization RMS 0.125 and sample peak <0.5. The metadata
does not claim perceptual loudness, post-quantization RMS identity or model accuracy.

## Validation and proof scope

[`native-tests.txt`](native-tests.txt): **164/164 checks pass**, 0 failed/skipped.
151 named bodies run in strict bytecode with 0 evaluator fallback; 13 properties
run on the evaluator, 100 generated cases each. The new block suite contributes
17 named tests and 2 properties (19 checks):

- Analytical impulse/DC responses and a quarter-rate sine transfer magnitude.
- Independent stereo histories; mono/stereo partition sizes 1,127,128,1024/whole.
- Exact bypass bytes including negative zero; reset and empty-block continuity.
- Per-block/cumulative budgets; forged state, invalid cutoff/rate/layout/dimensions,
  NaN/infinity rejection; finite-extreme update and high-pass overflow errors.
- Bounded-signal low/high complement and small arbitrary partition properties.

Selected `blockProbe` runtime-contract checks pass on both engines, returning
`true true true` for the closed-form response, reset and budget failure. These
selected assertions do not mean every runtime contract/input has been exercised.

[`block-verification.json`](block-verification.json): **2/5 contracts verified**,
3 unsupported-encoding skips, 0 refuted/errors/uncontracted. The proved functions
are `defaultBlockLimits` and private integer budget helper `canAdvance`. Start,
process and reset remain unproved because of higher-order/Result/record encodings.
The model uses mathematical Real/Int, with runtime equivalence not established;
it does not prove IEEE arithmetic or audio/device behavior.

The separately rerun legacy inline DSP suite has 12 total: 11 passed, 1 skipped,
0 failures. The precondition generator still supplies a negative onePole cutoff;
that case is not counted as passed. See [dsp-inline-tests.txt](dsp-inline-tests.txt).

## Quality report, section by section

[`quality.json`](quality.json):

| Section | Observed result |
|---|---|
| Compile | 27 files pass |
| Contracts | 14/62 verified; 48 skipped (5 missing postcondition, 43 unsupported); 0 refuted/errors; 33 uncontracted exports |
| Interface | 141 signatures; v2 `e323556e6a947daaa5af0d4dfd9474b06bc84a041ba381803affb10d587cc730` |
| Effects | Declared max `[IO]`, rank_max IO; processing is pure, IO only for smoke |
| Release | Feature kind; nonempty 0.3.0 changelog section |
| Docs | AGENT.md / ai_summary present; reported exports covered = 7 |
| Style | 93/93 exports pure |
| Tests/smoke | 12 files, 164 package checks pass; smoke passes, attested execution |
| Badges/gates | PUB016: 48 skipped; PUB011: 33 uncontracted; no gates |

The Apache-2.0 license text is now included with the package and license_url points
to that file rather than the source repo's nonexistent root LICENSE.
[`publish-dry-run.txt`](publish-dry-run.txt) records packaging only; no upload or
registry validation/publication is claimed. Strict quality would promote PUB011's
existing warning to a gate; the normal report is not a warning-free/full-proof claim.

## Independent consumer compatibility

[`app-compatibility.txt`](app-compatibility.txt) records the standalone Loop Lab
fresh clone tested against this working package through a temporary explicit
developer path override: compile/native 10, Node 45, Python 6 and quality all pass.
The committed app manifest/lock were restored to their exact remote candidate pin
afterward. This checks backwards compatibility; the application has not yet adopted
the new filter feature in its UI. Hosted app CI did not execute due to runner/account
availability and is not reported as a pass. The working private preview remains
in the application repo, independent of this development checkout.

## Reproduce

```sh
ailang check --package packages/audio
ailang test --strict-bytecode --package packages/audio
ailang test packages/audio/dsp.ail
ailang verify --json packages/audio/block.ail
ailang pkg quality --json packages/audio
ailang run --package-dir packages/audio --strict-bytecode --verify-contracts --entry pcmDemo --args-json 0 packages/audio/examples/block_pipeline.ail
ailang run --package-dir packages/audio --strict-bytecode --verify-contracts --entry recipeDemo --args-json 0 packages/audio/examples/block_pipeline.ail
# Repeat the two demos without --strict-bytecode for interpreter comparison.
# From packages/audio: ailang publish --dry-run
```

Text logs have ANSI styling stripped. These software fixtures do not establish
audible/perceptual quality, cross-architecture byte identity or physical latency.
