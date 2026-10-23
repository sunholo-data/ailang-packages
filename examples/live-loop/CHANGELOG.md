# Changelog

## 0.2.0

Feature: audio 0.3 consumer workflow, still a local application (never published).

- Private Off / Peak-safe / Matched take preparation with input/output sample peaks,
  active-window RMS, bounded boost and a reason for the gain. Re-preparation starts
  from an unlevelled shaped original rather than compounding gain or fades.
- One-step undo/redo per part uses the existing prepare/stage/activate protocol;
  history changes only after exact-frame renderer and planner acknowledgement.
- Download the active committed part as an eight-second mono PCM16 WAV for Live.
  Downloads exclude private/pending takes and precede track level/pan. Stop/reset
  clears in-memory history; saving a WAV is an explicit user action.
- Reference tests compare the browser level adapter against the AILANG API and
  pin browser WAV bytes to the package codec. Runner v3 identifies the changed
  preparation worker; the earlier v2 soak remains historical baseline evidence.

## 0.1.0

Feature: local L0 host feasibility lab with four generated parts, private bounded capture,
a pure AILANG revision planner, audio-render-clock acknowledgements, synthetic-input
routing checks, and local/optional WASM bridge measurements. Never published as a package.

Official local Sunholo tokens/Montserrat/AILANG logo; accessible controls and reduced-motion
transport. Added a muted planner/worker/worklet runner for 8-handoff trials or
100 handoffs plus a 30-minute software soak, with cancellation and epoch-scoped cleanup.

Fix: authorize activation from the exact renderer acknowledgement when the main
AudioContext clock trails it. Runner v2 records hidden-tab intervals instead of
cancelling synthetic background checks; microphone capture still cancels on hide.

Fix: bind each asynchronous input request to its own capture identity. Close late
permission grants, ignore obsolete failures, stop input on release/cancel/device loss,
and scope worklet stop/cancel commands to the intended take. Add explicit microphone
permission preflight, focus/device-change cancellation and bounded local lifecycle
reports with a manual microphone/device check guide. The permission probe records
no take and immediately releases its stream.
