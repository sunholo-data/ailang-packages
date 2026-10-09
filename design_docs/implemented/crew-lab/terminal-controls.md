# Terminal graphics and friendly captain controls

| Pillar | Score | Reason |
|---|---:|---|
| Choices Are Final | +1 | Uses the existing atomic host and retained decision bank |
| The Game Doesn't Judge | +1 | Separate gauges, no preferred score or red/green verdict |
| Time Has Emotional Weight | +1 | Explicit advance; no wall time |
| The Ship Is Home | +1 | Crew state visible in an immediate interior dashboard |
| Grounded Strangeness | 0 | UI only |
| We Are Not Built For This | +1 | Trust and fatigue stay distinct |

Mark requested terminal graphics and an easy way to work with the CLI (attended
2026-10-09). Initial crew-lab PR108 is merged after CI/independent100PASS. This
small follow-up adds ASCII gauges and friendly aliases for the exact existing
host commands. It changes no kernel, actor policy, scenario or public wire schema.

M1: Pure translator plus native controls (estimate180LOC). M2: IO-only viewer,
installed interactive/recorded controls, docs and independent review (estimate120LOC).
Reuse std/string.words, codec numeric checks, std/json safe encoders and existing
session authority/state machinery. No new dependency. User request authorizes UI
execution; no provider calls, game edits or publishing.

Friendly 'reply' creates an explicitly synthetic:manual one-hot fixture for a
stored pending request; it is an authored test response, never a calibrated NPC.
Full JSON saved distributions remain available. Confidence/roll can be specified;
all validation and actor mapping still happen in the existing pure host.

Friendly interactive mistakes retain state and allow another command; JSON-recorded
mode preserves fail-fast invalid-input behaviour. Blank/EOF and quit end input.
Bound10,000commands including help/status. Gauge clamps visual extent to10cells
and retains the exact number. No ANSI clear-screen assumptions or extra effects.

Acceptance: native translator tests evaluator/strictVM; all five legacy recordings
and installed wrappers pass; friendly care/order sessions produce the same expected
fatigue/trust/materials; cancel and errors do not fabricate crew responses; independent
review and scoped CI pass. No source changes to already-reviewed social mechanisms.

Implementation and independent local evaluation completed:100/100. Native68/68
on interpreter/strictVM; five full JSON traces replay and match, installed terminal
controls pass. Source properties are separate: scenario7pass; session3pass9skip
because Session has no automatic generator. No zero-skip claim for those properties.
Remote scoped CI remains the mandatory landing gate; read PR checks for its result.
