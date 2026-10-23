# Loop Lab

A local L0 feasibility prototype for the [live-loop instrument](../../design_docs/planned/live-loop-instrument.md).
Four original parts share a browser audio clock. Capture stays private until an
explicit commit, and a pure AILANG planner authorizes the revision and loop boundary.
**L0 acceptance is still open:** automated kernel/transport checks pass, but the
browser, physical loopback, device lifecycle and soak checks have not been run here.

## Run locally

Requires AILANG >=0.54.17, Python 3 (tested 3.13.7), and a browser with AudioWorklet.
Node (tested 26.12.1) is needed only for host-kernel tests and the optional WASM probe.
No npm install, model service, microphone access or cloud deployment is required.

```sh
cd examples/live-loop
ailang lock
python3 server.py
```

Open **http://127.0.0.1:8976** on the machine running the server. First startup renders
four 8-second mono WAV fixtures at 16 kHz through `sunholo/audio@0.2.0`. The generator
uses the evaluator to retain its `FS @limit=4, IO @limit=1` budget; this toolchain
explicitly refuses that effect frame in strict bytecode. Fixture generation has a
180-second timeout and is offline. Delete `static/audio/*.wav` after changing
`assets.ail` to regenerate. Browser decoding explicitly resamples to the actual
AudioContext rate. No generated WAVs or runtimes are committed.

1. Play the four parts. Select a part; adjust its level, pan or mute.
2. Leave **Test tone** selected to try private capture without a microphone.
3. Hold the capture button (pointer, Space or Enter); release to prepare privately.
4. Commit the ready take. The part changes at a planned four-bar loop boundary.
5. Stop & reset clears active takes, pending changes and private browser buffers.

Microphone is an explicit input selection and uses the browser's permission prompt.
No cue/monitor route exists. Capture is mono (first input channel), capped at 16 seconds;
focus loss during capture, hidden page, cancellation and device-ended events discard
it. A take binds to the selected part at capture start. Preparation trims/pads to
8 seconds, applies 10 ms edge fades and limits peaks to -6 dBFS without boosting.
This simple Audio replacement is a feasibility fixture, before quantized record
windows, overdub, undo, persistence or Notes/humming mode.

The phrase lanes are schematic, not measured waveforms. The private ready take has
its own waveform. The master meter is sample peak after final hard clamping, not
perceptual loudness. Level is linear; live gain/pan smoothing is later work.

## Ownership and protocol

| Component | Responsibility |
|---|---|
| `planner.ail` | Pure bounded state machine; integer absolute boundaries; epoch, expected session revision, track revision and pending ID checks; recent-command idempotence |
| `assets.ail` | Four original reference phrases using package PCM/WAV checking; fixed file-write budget |
| `server.py` | One authoritative in-memory planner session; fixed strict-bytecode entry, no planner capabilities; subprocess timeout, 64 KiB JSON metadata requests |
| `program-worklet.mjs` | Four active mono buffers, at most one pending replacement each; equal-power pan; audio-frame activation and acknowledgements; sample-peak/clamp counts |
| `capture-worklet.mjs` | Fixed-capacity private buffer, always-zero output, bounded-rate meters and one buffer transfer at stop |
| `prepare-worker.mjs` | Bounded take preparation and SHA-256 of the resulting f32 samples; no audio callback work |
| `app.mjs` | Serial bounded command queue, lifecycle and UI; transfers committed buffers to the program worklet |

The reference host is fixed at 120 BPM, four bars in 4/4, 8-second phrases. The
planner's arithmetic supports 40–240 BPM, but the host does not yet expose variable
phrase duration or tempo changes. It plans from an absolute origin, avoiding repeated
rounded-beat drift. `960` in the frame conversion is **16 beats × 60 seconds**, not
the pattern model's separate 960 ticks per quarter-note resolution.

Prepare reserves a boundary at least 200 ms after the later of current/ready frame.
The host stages the buffer first and sends a historical audio-frame acknowledgement;
Schedule records that acknowledgement. Activate follows the actual render-frame
message and requires exact equality with the planned frame. A late/rejected stage
retains the old part. A failed schedule/activation acknowledgement stops/resets the
session; L0 has no speculative rollback or scheduled-revision cancellation.
The last 64 command IDs are remembered within the epoch. Stop advances the epoch;
late UI results are discarded. Reloading a page closes its audio but leaves the
bridge's session until Stop & reset; the UI offers that reset before a new start.

## Inspect and test

Open **Timing & feasibility notes** for render-clock messages and bridge timings.
[The muted synthetic host check](http://127.0.0.1:8976/host-check.html) exercises the
real browser AudioWorklets, a nonzero private tone and an acknowledged boundary
replacement. It closes its context afterwards and displays a JSON report. It has
not been executed in this development session: the computer-use service exposed no
accessible browser windows. Run it on the reference laptop before accepting L0.

```sh
ailang check --package .
ailang test --strict-bytecode --package .
ailang verify --package . --json
ailang pkg quality .
node --test test/*.test.mjs
python3 -m unittest discover -s test -p '*_test.py' -v
python3 tools/benchmark.py
```

The Node tests use a fake AudioWorklet environment to test the actual render kernel;
100 exact-frame handoffs in that environment are not 100 hardware handoffs. The
Python suite executes the real strict VM and HTTP boundary. See [recorded evidence](evidence/2026-10-23/README.md)
for counts, proof skips and performance scope. No change to `packages/audio` is part
of this example and nothing here is a registry release.

## Optional WASM experiment

A resident WASM call avoids CLI launch/compilation overhead, but it is not automatically
the bytecode engine and has no hard realtime guarantee. Supply a known local binary
and the Go shim matching its compiler version:

```sh
python3 tools/install-wasm.py /path/to/ailang.wasm /path/to/go/lib/wasm/wasm_exec.js
node tools/benchmark-wasm.mjs
```

Then the UI's **Measure optional WASM worker** loads the same planner source in a
worker and reports cold initialization, loaded runtime version and warm init calls.
The application continues to use the strict local bridge; the worker is a measurement
path, not a second authority for live revisions. Missing/incompatible runtimes fail
explicitly. The measured current binary was built from a clean archive of CLI commit
`8f58117f265471584176e2aeb45996c2c9822577` with Go 1.26.10, never the core agent's dirty
checkout. Reproduce without modifying that checkout:

```sh
# From an AILANG core checkout; choose your own temporary directory.
mkdir -p /tmp/loop-core
git archive 8f58117 go.mod go.sum cmd internal std third_party | tar -x -C /tmp/loop-core
cd /tmp/loop-core
GOOS=js GOARCH=wasm go build \
  -ldflags '-X main.Version=v0.54.17-8f58117 -X main.BuildTime=2026-10-23' \
  -o /tmp/loop-ailang.wasm ./cmd/wasm
```

## Privacy, hosting and remaining acceptance

The local server serves only `static/`, the fixed planner source, three optional
runtime files and declared metadata APIs; it denies directory listings and repository
traversal. JSON commands reject sample/upload fields. Raw takes are not logged,
saved, exported, uploaded, or sent to the planner. Static original demo WAVs are
ordinary served assets. API access is limited by exact Host/Origin and a custom
same-origin JSON header. This is a single-session development server, not a
multi-user production service.

Loopback is the default bind. A laptop on another machine needs an explicitly
approved private HTTPS proxy, with its exact origin passed as `--public-origin`.
A Tailscale Serve route is persistent and exposes the metadata controls/static demo
to authorized devices on that tailnet; setting it up is separate from running this
local server. No public route has been created for this prototype.

Before L0 acceptance, run the browser check and real capture/playback on the reference
hardware, listen to four parts/replacements, measure physical loopback and deadline
misses, test permissions/device loss/focus/suspend/reset, run at least 100 actual
handoffs, and a 30-minute soak. Then use the measured render/worker/transfer costs to
prioritize `sunholo/audio` 0.3.0 block processing and the minimum `music_patterns`
time/revision API. Notes extraction, controllers and AI remain later milestones.
