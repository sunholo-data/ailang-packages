# Loop Lab

A local L0 feasibility prototype for the [live-loop instrument](../../design_docs/planned/live-loop-instrument.md).
Four original parts share a browser audio clock. Capture stays private until an
explicit commit, and a pure AILANG planner authorizes the revision and loop boundary.
**Earlier software host baseline passed:** user-run Firefox 158 at 44.1 kHz completed
100 exact-frame handoffs and 30 audio minutes, with zero clamping and 260.413
seconds in background tabs. Automated kernel/transport checks pass. Physical
loopback and broader platform acceptance remain open. The level/undo/export candidate
has separate automated evidence below; it does not inherit a new browser soak pass.

## Run locally

Requires AILANG >=0.54.17, Python 3 (tested 3.13.7), and a browser with AudioWorklet.
Node (tested 26.12.1) is needed only for host-kernel tests and the optional WASM probe.
No npm install, model service, microphone access or cloud deployment is required.
The current planner/quality checks also pass on the released v0.54.18 CLI.

```sh
cd examples/live-loop
ailang lock
python3 server.py
```

Open **http://127.0.0.1:8976** on the machine running the server. First startup renders
four 8-second mono WAV fixtures at 16 kHz through the local `sunholo/audio@0.3.0`
candidate (unchanged synthesis/PCM byte behavior). The generator
uses the evaluator to retain its `FS @limit=4, IO @limit=1` budget; this toolchain
explicitly refuses that effect frame in strict bytecode. Fixture generation has a
180-second timeout and is offline. Delete `static/audio/*.wav` after changing
`assets.ail` to regenerate. Browser decoding explicitly resamples to the actual
AudioContext rate. No generated WAVs or runtimes are committed.

1. Play the four parts. Select a part; adjust its level, pan or mute.
2. Leave **Test tone** selected to try private capture without a microphone.
3. Hold the capture button (pointer, Space or Enter); release to prepare privately.
4. Choose **Peak-safe**, **Matched** or **Off** and inspect the private gain/level
   report. Changing the mode re-prepares from the unlevelled shaped original.
5. Commit the ready take. The part changes at a planned four-bar loop boundary.
6. **Undo take** restores the previous committed part at the next boundary;
   **Redo take** swaps it back. Capture a new part to replace that one-step history.
7. **Download WAV** saves the active committed part, including its prepared gain but
   before track level/pan/mute. Import the file into Live at 120 BPM / four bars.
8. Stop & reset clears active takes, pending changes, history and private buffers.

Microphone is an explicit input selection. Choose **Enable microphone** first and
respond to the browser prompt before holding to capture. The permission probe stops
its stream immediately and records no take; the capture hold then opens its own
input. Only one permission request can be outstanding on this page. A cancelled
request cannot attach its eventual stream to a later hold.
No cue/monitor route exists. Capture is mono (first input channel), capped at 16 seconds;
focus loss during capture, hidden page, cancellation and device-ended events discard
it. A take binds to the selected part at capture start. Preparation trims/pads to
8 seconds and applies 10 ms edge fades once. Peak-safe only reduces peaks to about
-6 dBFS; Matched uses the audio 0.3 active-window RMS policy with bounded boost and
peak protection; Off retains the shaped input level. Quantized recording windows,
overdub, project save/load and Notes/humming mode remain future work.

The phrase lanes are schematic, not measured waveforms. The private ready take has
its own waveform. The master meter is sample peak after final hard clamping, not
perceptual loudness. Level is linear; live gain/pan smoothing is later work.

## Level decisions, recovery and Live handoff

Matched targets linear active-window RMS 0.125 (about -18.1 dBFS), permits at most
4x gain (about +12 dB), requires 1024 active frames and keeps sample peak <=0.501187
(about -6 dBFS). Activity uses 1024-frame windows with RMS >=0.001 (-60 dBFS).
Silence/below-floor takes are not boosted; noise above that floor can still qualify.
This is a preparation preset, not LUFS, true peak, noise removal or compression.
The worker checks actual Float32 stored-sample peaks and may reserve a little extra
headroom after rounding. The AILANG proofs do not apply to its JavaScript adapter;
18 cross-language fixtures compare measurements/decisions against the package.

Ready takes and their unlevelled shaped originals remain private in memory. No
audible cue/monitor is added. Discard also invalidates an outstanding worker reply.
Undo/redo stages the previous **committed** buffer through the existing planner;
the export/history pointer changes only after exact-frame activation is acknowledged.
Exporting during private preparation or a scheduled change still downloads the old
active part. Current/previous/pending slots are bounded to three buffers per part;
copies in workers, transfers and the renderer add temporary/browser memory.

WAV is mono PCM16 at the AudioContext rate with the package's legacy *32767,
half-away-from-zero quantization. The filename records part, active revision,
120 BPM and four bars; no tempo/warp marker is embedded. In Live, check import/warp
settings so the eight-second file spans four bars at 120 BPM. This is an explicit
file handoff, not a plugin host or an automatic/continuous Live connection. Only
this explicit download saves a recording. Project save/load is not implemented.

See [workflow evidence](../../design_docs/implemented/audio-v3-workflow/README.md)
for adapter parity, history/export isolation, actual-app fake-browser flow and
package quality. Real browser download/audible acceptance of these new controls
remains distinct from the earlier microphone feedback and runner-v2 soak.

## Real microphone and device checks

Open `/microphone-check.html` for the step-by-step guide before recording. This
follow-up hardens input ownership after the passed synthetic soak. The user reports
the microphone workflow working; detailed per-scenario device/physical evidence
remains separate from that functional feedback.

- Enable microphone access, verify its permission-probe stream is released, then
  mute all four parts before checking private input against a silent program bus.
- Hold/release a take and discard it. Capture again, explicitly commit, then unmute
  its part to listen after the acknowledged boundary.
- Check keyboard focus loss, tab/application changes, external-device disconnect,
  Stop/reset during opening/recording/preparation, and permission denial when a
  prompt is available. Record only scenarios actually exercised.
- In Timing & feasibility notes, choose **Show capture lifecycle report** after each
  scenario. The JSON stays on the page. It includes current owned-track count,
  permission/capture states, track revisions, a last-attempt meter summary and up
  to 64 recent metadata events (with a dropped-event count). No samples, microphone
  labels or device IDs are included. No automatic pass verdict is inferred.

A late browser permission grant is stopped even after cancel/Stop; an obsolete
failure cannot cancel a newer take. Pending permission prompts cannot be aborted
by this app: resolve or dismiss the prompt before requesting microphone access
again. ID-scoped worklet controls prevent old stop/cancel messages from terminating
a later take. Normal capture releases its input immediately on release, then
awaits the private buffer; a missing finish reply cancels after two seconds.

The new controller has deferred-permission/device fakes plus an application-flow
regression using the actual app module, real strict AILANG planner and fake
DOM/audio/media APIs. Those tests are software evidence, not physical browser,
microphone or speaker tests. See [follow-up evidence](evidence/capture-lifecycle/README.md).

## Sunholo / AILANG branding

The interface follows https://www.sunholo.com/assets.html, token revision
`aa420f4c1ebd`: white/slate surfaces, Montserrat and restrained action orange.
The original AILANG SVG, official CSS/JSON tokens and Montserrat Regular/Bold
are served locally from `static/brand/`. The font licence and downloaded-file
hashes are included. The logo is not redrawn/recoloured and no runtime requests
go to third-party asset/font servers. See `DESIGN.md` for the instrument layout.

## Repeated handoffs and soak

Open `/soak-check.html` through the same local or approved private HTTPS origin.
User-run Firefox trials reached three exact-frame handoffs before the original
visibility rule cancelled the soak, and exposed a main-thread/render-clock mismatch
in a later short run. Runner version 2 fixes that clock path and records visibility
instead of cancelling merely because a tab is hidden. The user then completed
its 8-handoff profile successfully in Firefox at 44.1 kHz, with zero frame errors
and clamping. The first acknowledgement confirmed a 67-frame main-clock lag.
The user then passed the full 100-handoff/30-minute profile, including 16
visibility transitions and about 4 minutes 20 seconds hidden. Each track changed
25 times with zero frame error or clamping. See the [full report](evidence/2026-10-23/browser-firefox158-runner-v2-soak.json).
This validates the reference software path; physical microphone/device checks and
other browsers/rates remain open.

- Stop & reset Loop Lab first. The runner refuses to take over a running planner
  session. Background tabs are allowed; keep the machine awake.
- **Short:** 8 replacements across all four tracks, about one minute. Use this to
  check the runner before spending 30 minutes on a soak.
- **Soak:** 100 replacements, then continued rendering until 30 audio minutes have
  elapsed from the transport origin. Only the full profile can pass that soak.
- **Stop check:** cancels and releases its graph/worker. It resets only its own
  planner epoch. Hiding records bounded visibility intervals; audio suspension,
  missed deadlines, a closed page or Stop still interrupts the run. Refresh Loop
  Lab after the check finishes.

Runner version 2 records main-thread and render-frame observations for each
activation. A render acknowledgement supplies a lower bound on the known audio
clock when `AudioContext.currentTime` trails it; planned/applied equality remains
mandatory in both the client and planner. Visibility is metadata only and does not
relax deadline or completion requirements. The microphone capture UI still discards
a take when focus/page visibility is lost.

The muted graph uses a private synthetic capture and the real `prepare-worker`,
including SHA-256, then the real AILANG Prepare→Schedule→Activate bridge. It rotates
tracks, records each planned/applied frame and staging lead, and reports worker,
worker round-trip and CLI bridge timings. Report arrays are bounded (100 handoffs,
100 worker samples, up to 512 bridge samples); waits cap at 8 outstanding. A short,
interrupted or incomplete run is never presented as a passed 30-minute run.

The report contains metadata only and stays on the page. No microphone permission
is requested. This tests the software path; physical loopback, audible quality and
the microphone/device lifecycle matrix remain separate acceptance requirements.

## Ownership and protocol

| Component | Responsibility |
|---|---|
| `planner.ail` | Pure bounded state machine; integer absolute boundaries; epoch, expected session revision, track revision and pending ID checks; recent-command idempotence |
| `assets.ail` | Four original reference phrases using package PCM/WAV checking; fixed file-write budget |
| `server.py` | One authoritative in-memory planner session; fixed strict-bytecode entry, no planner capabilities; subprocess timeout, 64 KiB JSON metadata requests |
| `program-worklet.mjs` | Four active mono buffers, at most one pending replacement each; equal-power pan; audio-frame activation and acknowledgements; sample-peak/clamp counts |
| `capture-worklet.mjs` | Fixed-capacity private buffer, always-zero output, bounded-rate meters and one buffer transfer at stop |
| `prepare-worker.mjs` | Bounded take preparation and SHA-256 of the resulting f32 samples; no audio callback work |
| `levels.mjs` | Browser adapter for audio 0.3 measurement/plan semantics; independent Float32 output checks |
| `take-workflow.mjs` | Bounded committed history/restore slots, sample-view hashing and strict PCM16 WAV encoding |
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
replacement. It closes its context afterwards and displays a JSON report. The user
ran it successfully in Firefox 158 at 44.1 kHz: program peak 0 before commit,
nonzero afterwards, and 0-frame activation error. The [user-supplied report](evidence/2026-10-23/browser-firefox158-user-run.json)
is preserved with its scope in the evidence notes. Browser coverage and physical
device acceptance remain open.

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
traversal. JSON commands reject sample/upload fields. Raw/uncommitted takes are not
logged, saved, exported, uploaded, or sent to the planner. Only an explicit active
committed WAV download writes a recording outside session memory. Static original demo WAVs are
ordinary served assets. API access is limited by exact Host/Origin and a custom
same-origin JSON header. This is a single-session development server, not a
multi-user production service.

Loopback is the default bind. A laptop on another machine needs an explicitly
approved private HTTPS proxy, with its exact origin passed as `--public-origin`.
A Tailscale Serve route is persistent and exposes the metadata controls/static demo
to authorized devices on that tailnet; setting it up is separate from running this
local server. The user approved a private Serve preview on port 8449 during this
review session; its page, worklet and planner probe responded successfully over
HTTPS. No public route has been created for this prototype.

Before L0 acceptance, broaden browser coverage and run real capture/playback on the
reference hardware, listen to four parts/replacements, measure physical loopback and deadline
misses, and test microphone permissions/device loss/focus/suspend/reset. The
reference Firefox 100-handoff/30-minute synthetic soak has passed; extend it to
other supported environments as needed. Then use the measured render/worker/transfer costs to
prioritize `sunholo/audio` 0.3.0 block processing and the minimum `music_patterns`
time/revision API. Notes extraction, controllers and AI remain later milestones.

The [musical feature roadmap](../../design_docs/planned/live-loop-musical-roadmap.md)
now has the first level/recovery/WAV candidate implemented. Project persistence,
local hum-to-bass note capture, instrument choices and stateful effects are next.
