# Live-loop L0: host prototype and measurement plan

Status: reference software host checks passed on 2026-10-23: user-run Firefox 158
at 44.1 kHz, 100 exact-frame handoffs and 30 audio minutes including background
intervals. Microphone/device, physical loopback and broader-platform acceptance
remain open.
This implements the first experiment in the [long-term instrument plan](live-loop-instrument.md),
not a new registry audio release. [Loop Lab](../../examples/live-loop/README.md) is a
buildless local application with its own package root and a path dependency on the
published `sunholo/audio@0.2.0` source.

Four original 8-second parts are generated with the audio package. A pure AILANG
planner owns transport epochs, recent command IDs, session/track revisions and
future boundaries. A browser AudioWorklet owns its sample clock, mixes four mono
buffers to stereo and acknowledges replacements at the applied sample frame.
A separate capture worklet outputs silence, with a fixed private buffer. A worker
prepares a take; explicit commit is the only route to program playback. The Python
bridge accepts flat typed command metadata, never sample arrays.

The initial host is deliberately fixed at 120 BPM/four bars and Audio replacement.
It includes track selection, mute/level/pan, bounded capture, trim/pad/edge fade,
prepare/commit/discard, scheduled/active acknowledgement and stop/reset. It does not
yet implement Notes extraction, tempo changes, overdub/undo/save, MIDI, AI,
physical device negotiation or AILANG callback DSP. Those stay in L1 and later.

## Runtime decision

Recorded local control-sequence p95: evaluator CLI 30.65 ms, strict VM CLI 35.01 ms,
resident WASM in Node/V8 14.00 ms, with equal final states across all three. CLI
numbers include launch and compilation; resident WASM numbers exclude startup.
The full WASM runtime/load/probe session took 3.78 seconds. These are control tests,
not audio DSP throughput or browser/device latency. No native Go code-generation
comparison was made.

The supported prototype uses the strict local bridge, with no evaluator fallback
for its pure planner. The offline generator retains bounded FS/IO effects and runs
on the evaluator because the VM explicitly refuses its budget frame. An optional
WASM worker probe loads the exact same planner source; a clean version-matched WASM
binary works in Node. The actual preparation-worker/hash/transfer and CLI path
now has the full Firefox soak measurements below; the optional browser WASM
measurement path still needs its own run.
No core modification is needed to run this prototype. Keep the core team's WAV,
resampler and verifier work independent; the reported bounded-effect VM limitation
is not a prerequisite for live host playback.

## Evidence and acceptance boundary

[Full evidence](../../examples/live-loop/evidence/2026-10-23/README.md): 4 files compile;
10 AILANG tests (9 VM named tests + 1 evaluator property/100 cases), 19 host-kernel/
orchestration/clock-regression checks and 6 CLI/HTTP integration checks pass on
clean v0.54.18. Quality: 3/6 contracts proved, 3 skipped, 0 refuted/errors,
1 uncontracted effectful generator, smoke passed, no gates.
Only three integer-arithmetic helpers are proved. The lifecycle relies on executable
guards and tests; raw sample arithmetic, audible quality and device timing are not
formally proved.

The kernel simulated 100 exact-frame handoffs and zero private signal in program
output. The user then ran the real muted browser harness in Firefox 158 at
44.1 kHz: private input peak 1, program peak 0 before commit and nonzero after,
planned/applied frame 382530, activation error 0 frames, preparation 4 ms. The
[user-supplied report](../../examples/live-loop/evidence/2026-10-23/browser-firefox158-user-run.json)
is one actual browser handoff, not physical loopback or the 100-handoff acceptance
run. The 4 ms times the harness's inline preparation, excluding worker/hash/transfer
costs; reported output latency 28.798 ms is a browser estimate. The user also
reported the Loop Lab working. The agent did not independently rerun browser tests.

A branded `/soak-check.html` runner now exercises the real planner, preparation
worker/hash and AudioWorklets with 8-handoff or 100-handoff/30-minute profiles. It
has user-run Firefox evidence for three exact-frame handoffs before a visibility
cancellation, plus a short-run activation rejection. Runner v2 fixes a reproduced
main-thread/render-clock mismatch and records visibility instead of cancelling on
hide. A subsequent user-run v2 short profile passed 8/8 handoffs across all four
tracks, zero frame error and zero clamping. Its first activation recorded a 67-frame
main-clock lag and used the confirmed render frame successfully. The run stayed
foreground and was followed by the full user-run soak below. A short profile
alone cannot pass the soak. The UI follows the user-supplied Sunholo guide with original local AILANG/Montserrat
assets. The preview serves those assets successfully; visual review is still open.

The user then supplied a [successful full runner-v2 soak](../../examples/live-loop/evidence/2026-10-23/browser-firefox158-runner-v2-soak.json):
100/100 exact-frame handoffs (25 per track), 1800.34 audio seconds, zero clamping,
16 visibility changes and 260.413 seconds hidden. Worker preparation/hash p95 was
8 ms, worker round-trip p95 9 ms (first call max 185 ms), and server CLI processing
p95 49.22 ms across 302 observations. The report's arrays/counts/statistics agree.
This clears the reference software/background soak check, not physical/device
acceptance. Its 28.84 ms output-latency value is browser-reported, not measured.

Before accepting L0:

- Extend the passed Firefox synthetic check to other reference browsers/rates and
  confirm four-part playback/replacement listening checks.
- Measure actual browser worker load/call/transfer/preparation costs and physical
  input/output loopback, distinguishing clocks, reported latency and measured latency.
- Exercise microphone permission rejection, focus loss, key/pointer cancellation,
  disconnect, suspend/resume, repeated stop/reset, stale/late handoffs and page reload.
- Completed on the reference Firefox host: 100 real browser handoffs and a
  30-minute software soak. Repeat as needed for additional supported platforms;
  physical/device soak and loopback remain separate.

Then prioritize `sunholo/audio` 0.3.0 block/state APIs from measured needs, with
partition-invariance tests at 1/127/128/1024/full-block sizes. Introduce only the
minimum frame/tick/session/revision model in `music_patterns` before full pattern
algebra. Start L1 with quantized Audio windows, replacement/overdub, undo and local
save; Notes extraction follows after that host workflow is dependable.
