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
