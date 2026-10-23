# Live-loop input ownership and microphone checks

Status: implemented after merged PR 158; the user reports the microphone workflow
working. Per-scenario device evidence and physical latency measurements remain open. This follows the successful Firefox synthetic host soak, before extending
L1 with quantized Audio windows, overdub/undo and local save.

The previous input-open path used the shared held flag to validate asynchronous
permission replies. A cancelled old request could resolve while a new hold had set
that flag again. The application now owns each pending request, source and stream
by its capture identity; late grants are stopped and old errors/device callbacks
cannot cancel a newer take. Only one browser permission request is outstanding.

An explicit Enable microphone preflight releases its probe stream without recording,
then the user holds to capture through the existing private worklet. It emits silence
and now honors ID-scoped stop/cancel messages. Input resources close immediately on
release/cancel/device loss; only the matching buffer reaches preparation. Focus loss
and device-change callbacks cancel active input. Permission prompts remain under
browser/user control; app cancellation only invalidates its intent.

A local guide and bounded lifecycle report support user/device testing. The report
contains metadata/aggregate peaks only, no sample arrays or device identity, and no
automatic physical/privacy pass. Existing pure AILANG planning, audio package byte
identity and the program renderer are unchanged. No new core update is needed.

[Evidence](../../examples/live-loop/evidence/capture-lifecycle/README.md): 34 Node
checks pass, including a full app-flow regression with fake browser/audio/media APIs
and the real strict planner. App quality remains 4 files compiled; 3/6 arithmetic/
transport contracts proved, 3 skipped, 0 errors, 1 uncontracted generator; 10 package
tests and smoke pass, no gates. Browser microphone/device execution and physical
loopback remain open; the synthetic soak is baseline evidence for the earlier host.

Next: [musical feature roadmap](live-loop-musical-roadmap.md), beginning with explicit
level planning and recoverable takes, then local hum-to-bass notes and instrument/FX
choices. General user feedback is recorded separately from automated and physical
acceptance evidence.
