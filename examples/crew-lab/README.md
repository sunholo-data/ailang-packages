# Captain's preparation watch

Start with **`crew-watch-offline`**: this is a small game about being captain of a
bubble ship, preparing five specialists and equipment for possible first contact.
Offer work to hear a person, decide whether to commit their time and resources,
and advance everyone together. There is no preferred command style or winning
score. Eight turns mark a preparation review; you may continue afterward.

```sh
# From the package repository; standalone AILANG0.54.0 or newer is required.
ailang install --path examples/crew-lab
crew-watch-offline
crew-watch                  # Existing GLM setup; new replies may wait for AI.
```

The app is pure AILANG. Auto mode uses native arrows and Enter when both input and
output are terminals with raw-mode support. `--mode native` requires that support;
`--mode line` uses typed commands with ANSI; `--mode plain` uses typed commands
without escapes. Use `--ascii` for simple box/bar characters. Native mode reads
actual terminal size and resizes without losing a decision. Under40x16 it offers
only resize/quit; it cannot start an invisible assignment. The larger ship diagram
is a Bridge/Commons schematic, not a map of anyone's physical location.

**First watch: science before hello**

1. Read the opening. Leave **Ask for agreement** selected and press Enter.
2. Leave **Choose work** selected and press Enter. Choose the **scientist**.
3. Read their reply. Work has not started. The proposal defaults to **Decide
   later**; Up highlights **Start now** and shows its costs. Enter starts only if
   agreement, worker capacity and the two Archive slots are available.
4. Press `5` four times. Everyone working advances each time. The bar counts
   elapsed turns; science benefits apply when the fourth turn completes, and its
   two slots return. `w` shows assignments and supplies; `c` shows crew observations.
5. `b` returns from reading to your decision. `q` asks before ending; **Keep
   playing** is the safe default. Down then Enter ends the watch and keeps its journal.

**Second watch: authority, objections and relief**

Start a fresh run, highlight **Captain's authority** and press Enter. Offer the
engineer a readiness check. A refusal leaves the proposal open; authority permits
Start despite it, with a possible loss of cooperation. Read the preview before
committing. Choose **Check in with working crew** (`6`) and their job to hear how
it is going. If they request relief, choose **Resolve a relief request** (`8`),
select it, then read **Grant relief** versus **Deny relief** before choosing.
Grant stops that work and releases its held compute/module; deny leaves them
working and can strain cooperation. Replies vary, so a default seed does not
promise an objection or relief request. The deterministic fixture below exercises
both, and the installed tests exercise both grant and deny.

Every proposal displays **Start now**, **Decide later** and **0 Return to bridge**.
The latter two keep the offer/agreement in **7 Offers**, use no time/resources and
never cancel it. `b`/Escape leaves a decision submenu for the bridge; from a reading
view it returns to the pending decision. Main Escape or `q` asks before quitting.
Reading uses arrows or PgUp/PgDn; menus use arrows and Enter. The bottom tally tells
you which choice is highlighted when a menu is windowed. Numbers execute their
shown actions immediately in native mode. In line/plain mode type a number or
`up`, `down`, `enter`, `pgup`, `pgdn`, `b`, `h` or `q` and press Enter. Blank input
waits without a redraw or decision; actual EOF ends. To run the first flow by pipe:

```sh
printf '1\n1\n1\n1\n5\n5\n5\n5\n' | crew-watch-offline --mode plain --seed 42
```

Try competition: start scientist work and engineer work, then offer pilot work.
Together the first two hold all3 compute slots; the pilot needs2. Highlight Start
to see the named shortage beside it. Attempting it retains this same proposal
with an explanation. Decide later, advance the existing work four turns, return
through Offers, and start the pilot. Physical supplies spent on completion never
replenish by waiting; rest uses no supplies. Starting passes no time.

Live uses the existing pinned OpenRouter `z-ai/glm-5.3-flash` setup and separate
watch response policy (default12 attempts, maximum64). Saved wording uses no new
call. A cache miss never blocks: see "Background replies" below. Offline and exhausted allowances
remain playable with labelled authored narrator continuations. Selected AI words
remain exact in the journal/library; only display controls are sanitized and prose
wrapped. `--debug` reveals real development state in Crew and diagnostic responses.
No alien negotiations or arrival are added.

**Background replies (0.6.0)**

A crew member's decision always shows at once. Their reaction, rolls and seed come
from the authored policy, never from the model, so the watch commits the decision
with an authored line and fetches their own words in the background. The status
row reads `Replies: 1 preparing, 0 new (r)`; keep playing (read Crew, offer more
work, advance) and press `r` to read the words when they arrive. Arrivals never move
the menu, cursor, page or a half-typed reply; in line/plain modes they appear after
your next input. Each fetch runs in a separate `crew-reply-worker` process (installed
with the watch; up to three at once) that fills the same dialogue library, so the
words are saved for next time. Quitting stops any still running.

Prefetch: on the bridge the watch also fetches the words for offering up to two idle
crew their work (`--prefetch 0..5`, default 2), so that offer shows the crew member's
own words immediately. It is an exact prediction (the session is pure), never a
guess about the outcome, and it only spends attempts above a reserve of three kept for
replies you asked for. Prefetches are not shown as replies; if you make the offer
while one is still running, it becomes that reply.

The journal records each fetch as a `wording` record (job, request, source, calls,
tokens, text or error). These are transport only: the host commands, traces and seeds
are identical to a run whose words were already saved (`make ... async-test` checks
this).

**What a live dialogue call sends and receives**

The simulation first draws a reaction from the authored personality policy and
seed. AI writes its wording. A new watch request sends that fixed reaction, the
proposal and its purpose, and nested actor-local context: OCEAN, current state,
values, relationships, received evidence, known briefing, conversation issue and
exact captain speech. It receives `generated_dialogue/1` JSON with exactly two
different variants of the selected reaction, each with an id, text of at most240
characters and weight1. The player sees one selected speech. The model cannot
start work, change resources, choose probabilities or invent a fulfilled promise.

This reduces the previous request for alternatives covering every legal reaction.
Other reactions remain possible under different simulation conditions or seeds.
Cache identity still binds the full original context, policy/configuration, model,
chosen reaction and new generation profile. Existing complete library entries are
preferred unchanged; new selected-reaction entries occupy separate keys. Repeat
hits spend no AI allowance. Invalid output spends one attempt, retains the same
pending request and seed, and offers authored continuation.

In one paired GLM-5.3-Flash sample, the old request took83.7 seconds and6,502 output
tokens for12 variants; the selected-reaction request took10.9 seconds and967
tokens for two. Provider latency varies; since 0.6.0 that latency is hidden by
background replies and prefetch.

For a repeatable developer objection/relief experiment, create an isolated home
and strongly weight those legal labels through its authored policy. This never changes your
usual library or policy and makes zero provider calls:

```sh
lab_home=$(mktemp -d)
printf '1\n' | crew-watch-offline --mode plain --home "$lab_home" >/dev/null
jq '.rules |= map(.base=(if .label=="decline" or .label=="request_relief" then 1000 else 0 end)|.influences=[])' \
  "$lab_home/response-policy-watch-v2.json" > "$lab_home/objections.json"
mv "$lab_home/objections.json" "$lab_home/response-policy-watch-v2.json"
printf '2\n1\n2\n1\n6\n1\n8\n1\n2\n5\n5\n5\n' | \
  crew-watch-offline --mode plain --home "$lab_home" --seed 10001
# Choose1 instead of2 at the relief decision to grant it.
```

## Tune the crew: scenario files and crew-sim

This example is **local only** and is never published. The captain/crew host it
runs is the published package [`sunholo/crew_core`](../../packages/crew-core):
crew-lab adds the terminal watch, AI dialogue wording, journals and `crew-sim`.

Everything about the ship lives in `data/watch-scenario.json` (schema
`crew_scenario/1`): who is aboard, OCEAN traits, priorities, starting fatigue,
stress and morale, the work each specialist can be offered (duration, held and
spent supplies, effects), rest, the overextension rule, trust in the captain and
the supplies. The response policy (which reactions crew may give, and how traits
and state weight them) is `crew_response_policy/1` JSON. Copy either file, edit
it, and pass it in; nothing is recompiled:

```sh
cp examples/crew-lab/data/watch-scenario.json my-ship.json   # edit freely
crew-watch-offline --scenario my-ship.json                   # play it
crew-watch-offline --scenario my-ship.json --policy my-policy.json
```

A malformed file is rejected before the watch opens, naming the field
(`scientist: ocean: openness must be 0..100`). Each journal records the scenario
hash, the policy hash and the canonical scenario, so a run says exactly which
ship it was.

`crew-sim` plays many seeds without AI and prints one JSON line per seed. Use it
to see what a change does before playing it by hand:

```sh
crew-sim --captain consent --seeds 1..20 > consent.ndjson     # ~12 s
crew-sim --captain orders  --seeds 1..20 > orders.ndjson
crew-sim --summary consent.ndjson                              # medians and spreads
crew-sim --scenario my-ship.json --seeds 1..20 > mine.ndjson   # compare a variant
```

Captains: `consent` starts only agreed work and grants relief; `orders` starts
whatever it offered and denies relief; `random` decides by seeded coin. Crew
replies come from the authored policy exactly as in the offline watch. Each line
holds reply counts, offers, starts, refusals with the engine's reason
(`insufficient_resource`, cooperation floor), relief asked/granted/denied,
completed projects, and each specialist's final fatigue, stress, morale,
readiness, observations and trust in the captain. The same inputs always give
byte-identical output on both AILANG engines. The summary compares runs; it never
ranks captains or ships.

What the default ship shows (20 seeds, 12 turns): trust in the captain rises under
consent (median scientist 59, medic 62) and falls under orders (42, 32); supplies,
not opinions, block most work (every refused start is `insufficient_resource`).

### Check what you expect: claims

Write what you expect the crew to do as claims and let `crew-sim` check them over
many seeds. Each claim is about one captain and one measure of a `crew_sim/1` line:

```json
{"schema":"crew_claims/1","claims":[
 {"id":"orders-erode-medic-trust","captain":"orders","metric":"crew.medic.trust","stat":"median","op":"<","value":40},
 {"id":"orders-erode-medic-trust-usually","captain":"orders","metric":"crew.medic.trust","stat":"share","when":{"op":"<","value":45},"op":">=","value":0.75}
]}
```

```sh
crew-sim --check examples/crew-lab/data/watch-claims.json                 # 10 of 10 claims hold
crew-sim --check examples/crew-lab/data/watch-claims.json --scenario my-ship.json
```

Stats: `median`, `mean`, `min`, `max`, or `share` of runs meeting `when`. Metrics:
`tick`, `offers`, `starts`, `refused`, `stockouts`, `errors`, `relief.asked|granted|denied`,
`replies.<reaction>`, `refusal_reasons.<code>`, `completed.<recipe>` and
`crew.<member>.<fatigue|stress|morale|readiness|observations|trust>`. Unknown crew,
recipes or fields are rejected, so a typo cannot pass as zero. Each claim prints
PASS or FAIL with the observed value; any FAIL exits 1. `data/watch-claims.json`
records what the default ship does today: change the ship, re-run, and the named
claims say what moved. Claims describe the simulation; they never score a captain.

### Read the words: crew-sample

`crew-sample` shows what crew members would actually say across varied moments,
fetched exactly as the watch would (same prompts, checks and library):

```sh
crew-sample --max-calls 6 --report words.txt > words.ndjson   # live: at most 6 new calls
crew-sample --offline --report words.txt                     # authored words, no provider
```

It plays the consent captain without AI, picks moments that differ by crew member,
reaction and fatigue/stress/morale, and prints one `crew_sample/1` line each (crew
member, project, reaction, state, the words, source, calls, and whether the words
leak mechanics). Saved words are free; new words cost one call each, up to
`--max-calls`. Samples go into the watch's library, so the watch reuses them.
Samples use the watch-v2 prompts (crew-sim does not play conversations).

Limits worth knowing:

- Sessions keep their last 64 answers and drop answers that can no longer be
  retried, so runs can be long; finished work is not archived, so they slow down
  (one seed: 60 turns about 8 s, 120 about 40 s).
- AI attempts per watch are the response policy's `callLimit` (default 12 for new homes, at most
  64); prefetch only uses attempts above a reserve of three.
- Journals stop safely at 8 MiB; this is a watch-sized lab, not a whole voyage.

## The host protocol: crew-host

`crew-host` reads NDJSON commands on stdin and writes one JSON trace per line:
the protocol a Godot simulation would drive. The saved recordings replay it:

```sh
crew-host < examples/crew-lab/recordings/agreed-science.ndjson
make -f examples/crew-lab/Makefile experiment INPUT=examples/crew-lab/recordings/granted-relief.ndjson
```

The first line is `{"command":"start","policy":"consent","scenario":"watch-v2"}`
(`watch-v3` adds personality and conversation sidecars). Then `offer`, `ask`,
`answer`, `start_task`, `resolve_relief`, `deliver`, `advance`, `abort` and
`cancel`. `run.sh interpreter|vm FILE` runs a recording on either engine;
`make ... parity` asserts the traces are byte-identical.

## Validate

```sh
make -f examples/crew-lab/Makefile validate AILANG=/absolute/path/to/ailang
make -f examples/crew-lab/Makefile mutations
```

`validate` covers crew_core (both engines, contracts, the example drift check),
the app's tests on both engines, host recordings (replay and engine parity),
the store, the installed native watch (plain and PTY), short replies,
conversations, `crew-sim` and scenario-file errors. `mutations` compiles eight
behavioural mutants of the host and requires the tests to kill each one.

## Talk through a crew concern

For a reproducible first example, run:

```sh
crew-watch-offline --seed 34500
```

Choose **1 Ask for agreement**, **1 Choose work**, then **3 medic**. The medic
asks who you intend to prepare for. Their concern leaves the same proposal open.
Read known facts, their condition, the project costs, and what remains unknown.
Choose one of three starting replies to edit, or **4 Write my own reply**.

Type your captain's words. Left/Right and Backspace/Delete edit them; Enter opens
review. Tab opens context help and Escape returns to the draft. Review shows exact
words and the declared approach. **2 Keep editing** is the default; **3 Change
approach** cycles the five discussion stances. **1 Send these exact words** commits
speech and asks the medic to reconsider this same proposal. They may still decline.
No time passes, supplies are not spent, and work is not started by dialogue.

A suggestion is a discussion, not an implemented resource change or fulfilled
promise. Free text uses the approach you explicitly confirm; the host does not
pretend to infer an enforceable command from your words. Your exact words become
evidence available to the recipient's next AI/cache context and the run journal.

Use **4 Introduce a voyage event (lab)** on the bridge to deliver a major scenario
report. It is an experiment fixture; the terminal does not simulate an actual
arrival or alien encounter. Receiving it does not instantly change personality.
Advance turns, talk to crew, and inspect **c Crew** with `--debug` to see baseline,
current OCEAN, response targets and received triggers. Ordinary exchanges can
change mood/trust immediately and influence an active response; they do not start
OCEAN drift. The normal view stays descriptive.

For redirected input, `--mode plain` uses one complete line of draft text at a
time, then a blank line to review; `/context` opens help and `/cancel` sends nothing.
EOF during editing/review sends nothing. `--legacy` runs the previous watch-v2
for archived parity experiments. Live words arrive in the background (0.6.0).
