# sunholo/live_loop_lab

Local application example, never a registry release. `sunholo/live_loop_lab/planner` owns pure command,
epoch/revision and boundary decisions. `sunholo/live_loop_lab/assets` generates original demo WAVs using
sunholo/audio. The browser owns its audio clock, device lifecycle, private capture,
rendering and sample-level acknowledgements. The Python server is only a bounded local
transport to the fixed AILANG entry point, with no runtime capabilities for the planner.

Run `python3 server.py` from this directory. It generates missing audio fixtures and
serves only the static root plus declared local API/runtime endpoints. The default
binding is loopback. Capture is private until an explicit Audio commit; synthetic
input can test routing without microphone access. Stop/reset releases captures.

`planner.handle(string) -> string` takes schema-versioned JSON and returns JSON.
Frame/rate/bpm/revision bounds execute in ordinary runs. The last 64 command IDs are
idempotent within the epoch; stale epoch/revision, missing asset metadata, busy tracks,
late staging and false activation frames are rejected. No raw samples enter this API.

The reference configuration is four bars of 4/4 at 120 BPM. Boundary frames derive
from absolute cycle position with integer division, not repeated rounded beat lengths.
The browser must stage before the requested frame; missing a deadline keeps the
current part active. Physical audible latency is separate from render-clock metrics.

Effects: planner is pure; asset generation uses at most four FS writes and one IO
verdict. Clip processing, capture capacity, queues, request sizes and CLI runtime have
explicit limits. Runtime contract checks are opt-in; boundary guards are always active.

Validate: `ailang lock`, `ailang test --strict-bytecode --package .`, source inline
tests, `ailang verify --package .`, `ailang pkg quality .`; `node --test test/*.test.mjs`;
`python3 -m unittest discover -s test -p '*_test.py'`. Browser/loopback measurements
must identify the tested runtime/configuration and may not be called physical audio
or microphone evidence when synthetic input was used.

## Capture lifecycle follow-up

`static/private-capture.mjs` owns each input request/source by a distinct take ID.
Only one browser permission request may be outstanding. Cancellation invalidates
ownership; a late stream is stopped and a late error cannot cancel a later take.
The explicit microphone permission probe immediately stops its stream before any
capture starts. The capture worklet accepts ID-scoped stop/cancel controls.

The local microphone guide is `/microphone-check.html`. Its manual/device checks
have not been attested by the automated tests. The inspector's capture report
contains bounded metadata/events and aggregate peaks, not samples, device labels
or IDs; it does not automatically report a physical/privacy pass.

## Level preparation, recovery and WAV handoff (local 0.2.0)

The browser `levels.mjs` adapter implements the audio 0.3 plan semantics. Its
JavaScript code does not inherit AILANG proofs: cross-language fixtures test its
measurements/decisions against the package, and Float32 output has its own stored
peak check. Defaults: 1024-frame pooled activity windows, 0.001 floor; Matched aims
for 0.125 active RMS, at most 4x gain, 0.501187 peak ceiling and 1024 active frames.
These are prototype preparation settings, not LUFS targets or a noise detector.
Switching mode reuses a shaped but unlevelled private original. Commit remains explicit.

`TakeHistory` retains current/previous/pending eight-second mono assets per part,
at most 12 retained buffers across four parts (18,432,000 Float32 samples at the
192 kHz host ceiling). This is a retained-history bound, not total browser heap.
Undo/redo uses the same revision/stage/activation protocol as a new capture; only
acknowledged active audio is exportable. Reset/pagehide clears owned history and
the owned download object URL. No session/project save/load is implemented.

Download WAV explicitly saves a committed part before track level/pan/mute. It is
mono PCM16 with the package's *32767/half-away rounding and an eight-second loop
length. The filename records track, active revision, 120 BPM and four bars. Private
and staged candidates cannot enter this path. A browser download is not an automatic
Live import or continuous DAW connection. No new server upload endpoint is added.
