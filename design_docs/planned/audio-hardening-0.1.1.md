# Audio hardening 0.1.1

**Status:** Implemented and validated on `fix/audio-0.1.1`, 2026-10-23. Release candidate; not published. Core changes and Stapledon's migration are owned separately.
**Roadmap:** [First class audio support](first-class-audio-roadmap.md), first milestone.

## Result

The package now has checked recipe parsing/rendering, bounded sample allocations, typed errors and checked PCM/WAV boundaries. Silent drive returns silence; one-shot starts no longer depend on input order. The WAV reader validates all declared chunks, and first-channel decoding uses direct byte access after metadata revalidation. Existing record shapes and function signatures remain compatible.

New public functions carry meaningful contracts. Static proofs increased from 2/12 to 7/25; the 33 legacy uncontracted exports did not increase. Ordinary guards enforce checked API failures without `--verify-contracts`. The supported domains, default limits and stricter rejection behavior are documented in [AGENT.md](../../packages/audio/AGENT.md).

## Quality report

Final report: [quality.json](../implemented/audio-hardening-0.1.1/quality.json), run with registry access on AILANG v0.54.17-dirty, commit 8f58117. This is local publisher-mode evidence, not a remote validator result.

| Section | Result |
|---|---|
| Compile | 16 files pass |
| Contracts | 7/25 verified; 0 counterexamples; 18 skipped; 0 errors; 33 uncontracted legacy exports |
| Interface | v2 `1c130bd28a9e2fb9c248c5ad861bd0e14ce85f31bcd06c4b6ea1d8f1bf80b8c8`, 71 signatures |
| Effects | Declared `[IO]` ceiling, rank IO; DSP stays pure; smoke has `IO @limit=1` |
| Release | Version 0.1.1, `fix`, nonempty matching changelog section |
| Documentation | AGENT.md and AI summary present |
| Style | 58/58 exported functions pure, 100% |
| Native package tests | 7 test files, 79 passed, 0 failed, 0 skipped |
| Smoke | Passed, including checked-boundary probes |
| Registry overlap | Ran with network access; no PUB023 skip in final report |
| Gates and warnings | No gates. PUB016: 18 skipped contracts; PUB011: 33 uncontracted exports. Strict quality would block on PUB011 |

The [raw verifier report](../implemented/audio-hardening-0.1.1/verify.json) separates 5 missing-postcondition skips from 13 unsupported-encoding skips. Verified functions are `absF`, `clamp16`, `fitsWork`, `pcm16ByteCount`, `limitsValid`, `defaultLimits`, and `inRange`. Proofs use the verifier's mathematical Int/Real models; floating-point edge behavior is guarded and tested, not certified by those proofs.

## Execution and compatibility evidence

- [Strict bytecode test log](../implemented/audio-hardening-0.1.1/tests-vm.txt): all 74 named-test bodies ran on the VM, with no evaluator fallback; 5 explicit properties ran on the evaluator, 100 cases each. All 79 checks passed.
- [Source inline log](../implemented/audio-hardening-0.1.1/inline-tests.txt): DSP has 6 passing inline examples and 5 passing generated properties (100 cases each). One auto-generated `onePole` property remains skipped for an invalid generated precondition. A separate explicit positive-domain `onePole` property passes 100 cases in the package suite.
- `checkedProbe(0)` returned `true true true true` on the interpreter and strict VM, both with `--verify-contracts`. It checks reference rendering, a resource-limit failure, a non-finite parameter failure, and forged decoder metadata.
- Historical compatibility used the 19 recipes from [Stapledon's commit 8bb63f13](https://github.com/sunholo-data/stapledons-godot/blob/8bb63f13/data/audio/recipes.json). Isolated old (`e95368f`) and candidate package copies rendered each recipe on strict bytecode; every PCM hash matched. [Recorded hashes](../implemented/audio-hardening-0.1.1/historical-pcm-hashes.txt). No game checkout was changed and the game's full integration suite was not run.
- [Publish dry run](../implemented/audio-hardening-0.1.1/publish-dry-run.txt) passed the local quality/packaging checks without uploading a release or contacting the remote validator.

## Scope and remaining work

This completes the package hardening milestone. Stereo clips, block processing, resampling, effects, richer analysis and device adapters remain on the roadmap. No core files were edited. The package retains its WAV/PCM helpers until the other agent's stdlib work defines a compatible replacement.

Checked limits bound frame/list sizes and layer passes, not exact heap use or execution time. The default frame limit is 30 seconds at 48 kHz, so the historical 32-second cue requires caller-supplied limits when opting into checked rendering. Raw render/encode functions remain compatibility primitives. The reader deliberately rejects malformed WAVs and supports integer PCM metadata only; PCM16 decode returns the first channel.

Release 0.1.1 is prepared for review. Publication and merging this implementation are separate from the earlier 0.1.0 merge.
