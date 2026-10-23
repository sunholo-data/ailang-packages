# Audio consumer check against released AILANG v0.54.18

Tested installed release `v0.54.18`, commit
`cd33d050b2276633c82624453309ebf7fcea9e2f`, built 2026-10-23 11:36:25.
Official release: https://github.com/sunholo-data/ailang/releases/tag/v0.54.18
(published 2026-10-23T11:53:13Z; notes inspected with `gh release view`).
`toolchain.txt` records the installed binary. This is compatibility evidence for
unchanged `sunholo/audio@0.2.0`, not a new package release.

## Package quality, section by section

| Section | Observed result |
|---|---|
| Compile | 22 files pass |
| Contracts | 10/49 proved, 0 refuted, 39 skipped, 0 errors; 33 uncontracted exports |
| Skip reasons | 5 missing postconditions, 34 unsupported encodings; neither group is proved |
| Interface | 104 signatures; v2 `88d860b4797eb822e9087e4f01bcfdd4f5b6ad1d689ab58c3be153b83ce3e678`, unchanged from the published feature group |
| Effects | Explicit `[IO]` ceiling, rank IO; all 82 exported functions pure |
| Release | `feature`, matching 0.2.0 changelog section |
| Docs | AGENT.md and AI summary present; 4 exported-module references recognized by quality |
| Style | 82/82 functions pure, 100% |
| Package tests | 116/116 pass, 0 failed/skipped in 10 files |
| Strict engine run | 107 named test bodies on VM, 0 evaluator fallback; 9 properties on evaluator, 100 cases each |
| Smoke | Present, passed |
| Badges / gates | PUB016: 39 skipped contracts; PUB011: 33 uncontracted exports; no gates |

The original `clip.checkSize` imported-ADT constructor failure is resolved:
`verify.json` now reports **verified** for that function. The previous package
result was 9/49 proved, 39 skipped, 1 verifier error. It is now 10/49 proved,
39 skipped, 0 errors. This confirms the upstream fix on the consumer source.

The numeric model remains mathematical Real/Int, with runtime equivalence not
established. This is not a floating-point/overflow/cross-platform audio proof.
The quality report does not measure runtime contract execution. Separate
`clipProbe` runs with `--verify-contracts`, on evaluator and strict VM, both print
`true true true`: independent expected PCM bytes, stereo WAV import and forged
metadata rejection. Those probe outcomes do not cover every exported contract.

Standalone DSP source tests: **12 total, 11 passed, 0 failed, 1 skipped**. Six
examples and five properties pass (100 cases each). The existing `onePole`
property still skips because a generated negative cutoff violates its requires;
that skip is reproduced on this release, not counted as passing coverage or hidden
behind the 116 package checks. See `dsp-inline-tests.txt` for input and replay seed.

## New stdlib boundary probes

`std_audio_probe.ail` runs seven closed-form checks with no effects or runtime
contract flag. Both evaluator and strict VM return the same JSON, all seven true:

1. The ordinary writer pads one byte of PCM8 to a 46-byte WAV, RIFF size 38,
   and a zero pad byte, preserving unpadded data size.
2. `std/audio.wavInfo` returns the correct one-frame metadata/data extent.
3. `wavHeaderChecked` rejects channel-count overflow.
4. `wavFromPcmChecked` rejects a partial PCM16 frame.
5. Packed PCM16 decode preserves interleaved stereo samples; explicit standard
   quantization encodes the exact independently specified input bytes.
6. Even clipping policy rejects nonfinite samples.
7. `formatFixed` produces nearest-even results for exact halfway values.

The probe outputs and source are preserved here. Reproduce from repository root:

```sh
ailang run --relax-modules --entry probe --args-json 0 \
  design_docs/implemented/audio-core-0.54.18/std_audio_probe.ail
ailang run --relax-modules --strict-bytecode --entry probe --args-json 0 \
  design_docs/implemented/audio-core-0.54.18/std_audio_probe.ail
ailang pkg quality packages/audio
ailang test --strict-bytecode --package packages/audio
ailang test packages/audio/dsp.ail
ailang verify --package packages/audio --json
```

## Consequences for the next feature group

| Upstream facility | Package action |
|---|---|
| Checked WAV writer/reader and ordinary writer validation | The reported odd-padding/field/frame defects now pass consumer probes. For future package internals, map stdlib errors into AudioError while preserving package limits, Mono/Stereo restrictions and supported-depth behavior. |
| Packed PCM16 conversion | Prefer the stdlib primitive in new adapters where its specified convention fits. Enforce package frame/sample budgets before materialization; the stdlib's 100 MiB ceiling is not a replacement for smaller consumer budgets. |
| Nearest-even `x*32768` encoding | **Do not silently replace** audio's pinned `x*32767/round` encoder. At -1 the new convention yields -32768 while the existing package encodes -32767. Preserve recipe/legacy byte identity; introduce any new convention explicitly. |
| Fixed-decimal formatter | Use for new presentation/report strings. Existing centi-dB numeric results and pinned sample arithmetic keep their current meaning. |
| Imported parametric ADT verification | The known constructor error is closed on v0.54.18. Retain explicit skip reasons and numeric/runtime scope; 39 contracts are still unproved. |
| Resampling | Still deferred in the upstream release; keep coordinated resampler work in the roadmap. |

The published 0.2.0 AGENT.md describes the toolchain limitation observed when it
was released. That frozen release description is historical; this newer evidence
supersedes its claim that checkSize still errors on v0.54.18. Update the package's
minimum compiler/docs in the next version that actually adopts new stdlib APIs,
rather than changing the already-published content or its quantization silently.
The original canonical feedback IDs remain recorded in the audio roadmap; no new
core bug report is needed for these now-passing probes.
