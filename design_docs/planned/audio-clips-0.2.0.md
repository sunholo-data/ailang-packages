# Audio clips and editing 0.2.0

Status: second roadmap milestone implemented and validated, 2026-10-23. Merge and publication were authorized in session on 2026-10-23. PR #155 groups the unpublished 0.1.1 hardening work into 0.2.0; the known core verifier limitation remains explicitly recorded.

Scope: validated planar mono/stereo clips backed by existing Array[float], explicit channel conversion/interleaving, checked editing/mixing, and channel-preserving PCM16/WAV adapters. Core updates remain with the other agent. Existing recipe records and mono render samples stay unchanged.

Policies: internal samples allow finite headroom; mono duplicates at unity; stereo downmix uses 0.5L+0.5R; mono panning uses equal-power gains with exact hard-pan endpoints; edits preserve rate/layout; PCM16 output has explicit Reject/Saturate policies and preserves legacy quantization for in-range samples. Rate/layout mismatch returns an error. There is no implicit resampling.

Clip records are public and can be forged, so every public operation validates its input. Limits bound input and output frames and total samples before allocation. Empty clips are valid. Temporary lists used by current array constructors/validation are bounded by the same dimensions; these are not exact host-memory or realtime guarantees.

Acceptance: independent stereo byte fixtures retain both channels; interleave/deinterleave and bounded PCM round trips have native properties; edits have known expected samples; malformed clips, non-finite values, format mismatch and allocation overflow are rejected; all new exports have meaningful contracts; package quality, source tests, smoke, strict VM and runtime-contract probes are recorded separately. Merge and publication are authorized in session.


## Delivered feature group

The 0.2.0 release includes the hardening work from 0.1.1 and three new modules:

- `clip`: planar Mono/Stereo Clip, ClipLimits, checked construction, channel selection, interleaving and explicit channel conversion.
- `edit`: gain, end-exclusive trim, padding, reverse, append, endpoint-defined fades, complementary crossfades, bounded mixing/placement and equal-power mono panning.
- `clip_pcm`: channel-preserving raw PCM16 and WAV adapters, with explicit Reject/Saturate clipping policy and legacy-compatible in-range quantization.

All 24 new function exports carry contracts. Inputs and outputs are revalidated because Clip records are public. Internal finite headroom is retained; output limits are checked before constructing sample arrays. Operations use existing array and byte primitives; no core files, dependencies, device access or effect privileges were added.

The working branch retains its earlier name `fix/audio-0.1.1`; PR #155 now describes the complete 0.2.0 group. The grouped version supersedes the unpublished hardening-only candidate. Merge and publication are authorized in session.

## Quality and execution evidence

Toolchain: AILANG v0.54.17-dirty, commit 8f58117, on the local arm64 host. [Quality JSON](../implemented/audio-clips-0.2.0/quality.json) is local publisher-mode evidence, not a remote validator result.

| Section | Result |
|---|---|
| Compile | 22 files pass |
| Contracts | 9/49 verified, 0 counterexamples, 39 skipped, **1 verifier error**, 33 unchanged uncontracted legacy exports |
| Interface | v2 `88d860b4797eb822e9087e4f01bcfdd4f5b6ad1d689ab58c3be153b83ce3e678`, 104 signatures |
| Effects | Declared `[IO]` ceiling, rank IO; DSP pure, smoke verdict limited to one IO operation |
| Release | Version 0.2.0, `feature`, matching nonempty changelog section |
| Documentation | AGENT.md and AI summary present; new API signatures and policies documented |
| Style | 82/82 exported functions pure, 100% |
| Package tests | 10 test files, 116 passed, 0 failed, 0 skipped |
| Smoke | Passed; includes stereo clip/PCM/WAV and forged-record checks |
| Registry overlap | Ran with network access; no PUB023 skip |
| Gates and warnings | No CLI gates. PUB016 reports 39 skipped contracts; PUB011 reports 33 legacy uncontracted exports. Strict quality would block on PUB011 |

The raw [verifier report](../implemented/audio-clips-0.2.0/verify.json) preserves every outcome. The quality summary's lack of a gate does **not** resolve the verifier error or establish full formal verification. Five skips have no postcondition; the other 34 are unsupported encoding. Proofs use mathematical Int/Real models, not IEEE-754 or machine-overflow proofs.

[Strict VM execution](../implemented/audio-clips-0.2.0/tests-vm.txt): all 107 named-test bodies ran on the bytecode VM with no fallback. Nine explicit properties ran on the evaluator, 100 cases each. Tests cover independent stereo bytes, channel identity, finite headroom and overflow, clipping extremes, forged records, partial frames, dimension limits, rate/layout mismatch, sample-level edit policies and empty clips.

[Runtime contract probe](../implemented/audio-clips-0.2.0/runtime-contract-probe.txt): `clipProbe(0)` prints `true true true` on interpreter and strict VM with `--verify-contracts`. It checks the full mono-clip → gain → equal-power pan → independent PCM bytes → stereo WAV import path and forged-record rejection. Guards also execute in ordinary runs without the flag.

[Source DSP checks](../implemented/audio-clips-0.2.0/inline-tests.txt): 6 inline examples and 5 generated properties pass; one auto-generated onePole property remains skipped for an invalid precondition. The explicit positive-domain onePole property passes in the package suite. Skips are not counted as test coverage or proofs.

[Publish dry run](../implemented/audio-clips-0.2.0/publish-dry-run.txt) passed local quality and archive construction. No version was uploaded; the remote validator was not contacted. The original recipe/DSP/noise/mono PCM/mix source bodies are unchanged from the hardening commit, whose [19 historical recipe hashes](../implemented/audio-hardening-0.1.1/historical-pcm-hashes.txt) matched 0.1.0. No game checkout was modified.

## Upstream verifier issue and release readiness

`checkSize` has a success contract for the validated sample count and bounds. Z3 verification fails because the generated declarations omit the imported `ResourceLimit(string)` constructor from `safety.AudioError`. A [minimal source](../implemented/audio-clips-0.2.0/verifier-repro.ail) and its [raw output](../implemented/audio-clips-0.2.0/verifier-repro.json) reproduce the failure on the installed binary. The contract remains in the code.

Filed through canonical AILANG messages as `inbox_1792745981583_2823c9cc`, correlated with the earlier verification-scope request. Delivery and the unread shared-store entry were confirmed. The core agent owns this update. Re-run raw verification when the core fix is available; retain the known verifier error, legacy skips and warnings explicitly. The user authorized release with the current evidence, without claiming complete verification.

To reproduce the minimal failure from the repository root, copy the evidence probe into `packages/audio/_verify_probe.ail`, run `ailang verify --json packages/audio/_verify_probe.ail`, then remove the temporary copy before package quality/packaging. The evidence file is not package source.

This is a cohesive offline feature group for the next release. Block processing, resampling, richer effects/analysis and devices remain later milestones; their absence does not imply any change to existing mono recipe output.


## Authorized release check

On 2026-10-23 the user instructed merging PR #155 and publishing 0.2.0 after the verifier limitation was explained. The [final release quality report](../implemented/audio-clips-0.2.0/release-quality.json) repeats the full checks after the release-note wording update: 22 files compile, 116 package checks pass, smoke passes, 9/49 contracts are verified, 39 are skipped, one verifier error remains and there are zero counterexamples. The 33 legacy uncontracted exports and mathematical proof scope remain explicit. No package code or contract was changed to bypass the core issue.
