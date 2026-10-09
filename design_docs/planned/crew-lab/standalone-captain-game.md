# Standalone captain game: introduction and consequences

Status: approved scope, implementation in progress, 2026-10-09.

The guided crew CLI currently assumes a player understands its protocol. A new
player sees raw task IDs, duplicate trust indicators and placeholder dialogue;
an ordinary materials shortage terminates play. The user requests a small game
that explains itself from first launch, with human guidance and terminal graphics.

You are captain of a bubble ship between destinations. The bridge is the decision
surface for life aboard the ship; reuse the established bridge/Commons fiction.
Choose work, rest, timing and how to handle crew requests. Different choices leave
different consequences, without a combined goodness score or a correct route.
This slice is a standalone experiment with two crew members, not the full universe.

## Boundaries and verified premises

Preserve the pure social host, OCEAN response weights, legal choice validation,
recipes, resources, policy semantics, model and complete journal schemas. AI writes
dialogue variants; authored probabilities and the simulation determine actions.
No new KPI, win/loss rule, replenishment, undo, cross-run crew memory or save/resume.
The response library persists; each launch starts a fresh crew session. Journals
record runs but do not implement resumable saves. No fresh provider calls are needed
for this interface update. Keep the existing GLM setup.

Verified from scenario.ail: six initial materials; science reserves and consumes
four over four ticks; maintenance reserves three and consumes two over three ticks;
rest takes two ticks and costs no materials. Science completion leaves only two
materials, so waiting cannot make maintenance affordable. Acceptance is separate
from an explicit captain start and cannot override resources or crew capacity.
Effects are applied at completion in this small fixture; do not imply gradual
fatigue changes or arbitrary scheduler progress.

Quorum trigger audit: no design freeze, shared event override, cost/KPI/banked-schema
change, or new external premise. This is presentation plus recovery using existing
committed rejection semantics. Independent sprint evaluation remains required.

## Player experience

On launch, a concise bridge briefing gives identity, situation, available choices
and a first suggested experiment. Explain consent/orders before selection, seed as
repeatable variation, and explicit ticks as work time. Do not require an additional
blank-line acknowledgement: the current reader treats a blank line as EOF.

Use portable, compact ASCII panels for crew, directed trust, supplies and projects.
Display human project names, worker, duration, reservation/consumption, and actual
work progress read from host state. Avoid displaying the inert actor trust scalar
as if it were the live directed relationship. Label who trusts whom. Explain that
higher fatigue differs from higher readiness. Keep existing numbered actions;
add h/help and contextual guidance without consuming AI calls or changing state.

Show consequences after actions, especially agreement versus actual start, reserved
versus consumed materials, completed work and relief. Project offers show costs
before commitment. Cached/live/authored wording is labelled in ordinary language;
placeholder fallback should be understandable, not protocol jargon.

Ordinary published domain rejection (resources, permission, crew occupancy or a
blocked advance) explains the reason and returns to an appropriate menu. Preserve
the accepted seed and all earlier successful boundaries, including partial advances.
Never hide, roll back or silently retry the failed action. Journal publication and
retention failures remain fatal; do not expose unrecorded state or dialogue.

On quitting, give a factual session recap of the actual current state, including
unfinished projects and elapsed ticks, with journal location and a clear note that
restarting creates a fresh session. Do not assign a winner, grade or moral score.

## Acceptance

1. A newcomer can identify their role and perform offer, answer, start and tick.
2. The pasted science-then-maintenance shortage remains playable, logs its rejected
   start and continues with subsequent actions, without charging resources or RNG.
3. Science completion does not falsely promise maintenance becomes affordable.
4. Consent refusal/crew occupancy and blocked scheduling are recoverable; fatal
   publication injection still leaves the previous journal/state boundary intact.
5. Help/navigation never changes host state, seed, sequence or call budget.
6. Existing recordings, strict VM/evaluator native tests, eight mutation controls,
   storage failure controls and original social regression continue to pass.
7. Independent review includes reading an actual new-player session transcript.
