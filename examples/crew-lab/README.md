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
watch response policy (default6 attempts, maximum8). Saved wording uses no new
call. A cache miss may block synchronously: the waiting screen offers no fake
controls; the next choice follows the reply. Offline and exhausted allowances
remain playable with labelled authored narrator continuations. Selected AI words
remain exact in the journal/library; only display controls are sanitized and prose
wrapped. `--debug` reveals real development state in Crew and diagnostic responses.
No worker processes, asynchronous replies, alien negotiations or arrival are added.

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

**Existing line consoles**

The following describes the preserved `crew-journey` and `crew-play` interfaces.
Their durable launchers may continue using the earlier standalone runtime; the
new commands use0.54 independently of Godot's runtime. Old policies/cache records,
model identifiers, authored effects and trace schemas remain unchanged.

Run `crew-journey` for the modern ship console, or `crew-journey-offline` to play
with saved and stock dialogue without AI calls. You are the captain of a bubble
ship, preparing a strained crew for possible first contact. Eight lab turns mark
a factual preparation review; you can keep playing afterward. No alien encounter,
arrival deadline, winning score or preferred policy is simulated here.

```sh
ailang install --path examples/crew-lab
crew-journey-offline
crew-journey --ansi --columns 80 --rows 24
```

The opening tells you what you are doing before asking for your command style.
**1 Ask for agreement** waits for a worker to agree before work can start.
**2 Use captain's authority** permits starting despite refusal; trust can suffer,
and cooperation, resources and capacity still apply. This choice lasts this run.
Press `h` before choosing if you want a concrete example. Seed42 is the default;
`--seed N` changes repeatable variation without another startup question.

Your five specialists are scientist, engineer, medic, pilot and diplomat. Their
fatigue, stress, morale, values and OCEAN archetypes influence authored reactions;
normal play shows observations and speech, such as “looks tired” or “on edge”.
`--debug` exposes actual metrics, OCEAN traits and recorded selection evidence for
development. It is off by default. These are experimental characterization rules.

Three resources compete: **3 Archive compute slots**, **3 replacement modules**
and **4 diagnostic cartridges**. Compute is concurrent capacity for analysing
Spire readings; it returns when work ends. Physical supplies are finite: completion
spends them, even if a benefit has reached its limit. Granted relief stops work
and refunds its reservation. Waiting never restores spent physical stock.

Use a key followed by **Enter**: `c` Crew, `w` Work, `j` Log, `h` Guide and `b`
returns to your current decision. `n`/`v` page text. Numbers select the visible
actions on any page. Reading costs no turn, AI attempt, random draw or journal entry.
In these older commands blank input ends the run; the native watch above
distinguishes blank waiting from EOF through readLineOpt. The log keeps the last64 notices from this run.

After a reply, the proposal screen says whether its worker has agreed and reminds
you that work has not started. **1 Start now** assigns the worker and holds the
recipe's resources immediately; it passes no time. Use **5 Advance** from the
bridge to progress the job. Its duration and exact held/spent resources are shown
in the decision preview. Rest assigns the worker without holding supplies.
**2 Decide later** returns to the bridge, leaving the proposal and answer in
**7 Offers** without using time or resources. **0** does exactly the same thing
here; it is a compatibility shortcut, not cancellation. **b Decision** returns
from a reading panel to this same proposal, rather than leaving it.

Try these two complete flows. Replies vary: under agreement, a refusal means
leave the offer open or choose another assignment. These examples describe the
acceptance path, rather than promising an agreement.

1. **Equipment and science together:** choose agreement (`1`), choose work (`1`),
   scientist (`1`), then Start (`1`) if agreed. Choose work (`1`), engineer (`2`),
   Start (`1`). These reserve all3 compute slots and1 module. Try pilot work
   (`1`, `4`, Start `1`): its2 slots are unavailable, so its offer stays open.
   The rejected start returns to the bridge. Advance4 turns (`5` four times). Science and equipment complete, all3 slots
   return, and only1 module is spent. Review offers (`7`) to return to the pilot.
   Read Work (`w`), return to the bridge (`b`), then quit (`0`).
2. **Care before contact:** choose agreement (`1`), arrange rest (`2`), scientist
   (`1`), then Start (`1`) if agreed. Advance twice (`5`, `5`): they recover and
   the worker becomes available. Choose work (`1`), medic (`3`), Start (`1`), then
   advance twice: diagnostic preparation completes and spends1 cartridge.
   Choose work (`1`), diplomat (`5`), Start (`1`), then check in (`6`, choose their
   working project). If they request relief, use `8` to select it and grant or
   deny. Grant returns their compute slot; denial keeps the assignment working.
   Read Crew (`c`) and the log (`j`), return (`b`), then quit (`0`).

Live mode uses the existing OpenRouter setup and pinned `z-ai/glm-5.3-flash` model.
A cache miss may create dialogue once; the same exact situation can reuse it later.
The modern policy file is `response-policy-watch-v2.json` under the library home,
with6 attempts per run by default (editable0..8). Existing user policy files are
preserved. AI supplies speech, authored rules select reactions, and the host owns
consequences. If generation fails or the budget ends, retry, explicitly choose an
authored narrator continuation, or cancel. No unselected AI response changes state.

The modern scenario is versioned `watch-v2`. Old `crew-play` and saved recordings
remain unchanged. `crew-journey --legacy --debug` runs the older two-specialist
scenario for regression/development. Its old response-policy.json and cache keys
remain byte-compatible; modern cache signatures include exact configuration identity.
The known-pattern dialogue guard rejects trait names and metric-score disclosure
before publication and on cache read; it is not a semantic proof of prose accuracy.

ANSI redraw uses bright blue/gold chrome and safe clear/home/reset only. TERM set
and not `dumb`, with NO_COLOR absent, selects ANSI; `--plain`/`--ansi` override.
**Pipes use `--plain`**: there is no TTY detection. Default dimensions 80x24; supplied
COLUMNS/LINES and `--columns`/`--rows` clamp 40..160 columns and 16..60 rows. One row
is reserved for the input prompt. There is no automatic resize, arrow-key input,
raw mode, cursor hiding, alternate buffer or foreign-language terminal host.
Relaunch with new dimensions. Core capability request: inbox_1791568104057_d08245d1.

Stock reactions are labeled narrator summaries, including cached authored bundles.
Cached/new AI quotations retain selected wording; display removes controls and
wraps/pages it. The exact source bundle, text, rolls, costs and provenance remain
in the journal. No provider spending is needed for the installed controls.

The independent reusable `sunholo/terminal_ui` package ships `terminal-ui-demo`:

```sh
ailang install --path packages/terminal-ui
terminal-ui-demo
```

Its core is pure AILANG; the demo uses IO only. Cell sizing supports ASCII, European
punctuation/box drawing and wide CJK conservatively; no full grapheme/emoji claim.
Run `test-journey.sh` for installed navigation/baseline equality and both-engine
recovery replay; `make -f examples/crew-lab/Makefile validate` includes the legacy and modern watch gates. Run `watch-test` for the five-specialist installed controls.

The original `crew-play`, `crew-view` and recording commands remain available.
The following technical guide documents those compatible interfaces and host limits.

---

# Captain aboard the bubble ship

You are captain of a bubble ship between destinations. From the bridge, choose
science, maintenance, rest and how to handle your crew's requests. Your scientist
and engineer respond as people with different personalities and values; they may
agree, refuse, raise concerns or ask for relief. This is a small standalone game:
there is no winning grade or right route, and no Godot build is needed.

Play as the captain with numbered choices and automatic crew replies:

```sh
ailang install --path examples/crew-lab
crew-play-offline --seed 42
crew-play --seed 42
# Optional isolated experiment data:
crew-play-offline --home /tmp/my-crew-lab --seed 42
```

Choose consent or orders at startup. Offer science, maintenance or rest, check in
with working crew, resolve relief requests, and advance time. After every reply,
you explicitly choose whether to start the offered project or leave it offered.
The dashboard refreshes with exact crew indicators, directed trust, materials and
project status. You never need to type request IDs or author the crew's answers.
A seed can also be entered at startup; it must be an integer1..2147483646.

`crew-play` uses the laptop's configured OPENROUTER_API_KEY and pins
`z-ai/glm-5.3-flash`. It asks AI for bounded dialogue variants on an exact
context cache miss. Authored policy weights choose a legal reaction using one
seeded roll; a second roll chooses its dialogue. AI prose cannot grant permission,
set effects or choose captain actions. `response-policy.json` under
`~/.ailang/crew-lab` is editable: its rules use received context, all five OCEAN
traits, values, fatigue and directed trust. These are experimental behavioural
rules, not validated psychology or a combined moral score.

For a first voyage stretch, run `crew-play-offline --seed 42`. Read the bridge
briefing, then choose **1** for personal consent. Choose **1** to offer science;
the crew reply automatically. If the scientist agrees, choose **1** to start,
then **5** four times to advance four ticks. If they refuse or you want to wait,
choose **2** to leave the project offered and try another assignment. Use **h**
or **help** at any game menu after startup for guidance. **0** quits at the bridge or goes back
from a submenu. A blank line ends input, so no extra Enter acknowledgement is needed.

The panels explain who trusts whom, crew fatigue/readiness, supplies and project
progress. Higher fatigue means more tired; higher readiness means more ready.
Work effects happen at completion. Science reserves and consumes four of the six
materials; maintenance needs three to start and consumes two. Once science finishes,
only two remain: waiting cannot make maintenance affordable. Rest takes two ticks
and needs no materials. A worker can run one project at a time.

An offer and an agreement are separate from your **Start** decision. Reviewing an
existing offer opens its costs and Start/Leave panel without changing the agreement
or generating another reply. Resource, consent or occupancy rejection remains
recorded and returns you to the bridge. It does not charge the rejected action or
advance the random seed; any earlier completed scheduler boundaries remain.
Journal-write failure still stops the game safely. On quit, the recap reports elapsed
time, completed and unfinished work and actual supplies/crew state; it assigns no
winner. Restarting creates a fresh crew session, retaining the dialogue library.

Offline stock responses are labelled narrator summaries of the selected reaction.
Saved/new AI wording is shown as the exact selected crew dialogue. The full selected
bundle and original text are preserved in the journal in either case.

The default policy permits two provider attempts per run (editable maximum8).
Transport failures, invalid responses, corrupt cache and exhausted budgets remain
visible with the response pending. Choose retry, an explicit authored continuation,
or cancellation. No automatic fallback or retry consumes the budget silently.
`crew-play-offline` uses valid matching cache entries or generic authored variants,
with zero provider calls. A context miss does not persist the generic starter.
Use `--home` to compare fresh experiments without changing your usual library.

Runs save `runs/<owner>/journal.jsonl` under the chosen home, including every actual
host command, full selected bundle, policy weights, both rolls and usage/provenance.
The host command stream can be extracted for replay. `run.sh` deliberately stays
fail-fast for legacy recordings; journals containing rejected commands use the
pure `recoveryRecording` entry below on either engine. Each state/seed transition is accepted and dialogue displayed only after
journal publication succeeds. A failed temporary write preserves the prior journal
and stops play. Journals are bounded at8MiB, replaced atomically, and do not claim
fsync durability or automatic crash-tail repair/resumption. Bundles persist between
runs; crew relationships restart with a new session.

`test-play.sh` exercises installed offline science, care, denial, competing
projects, immediate/post-completion shortages, occupancy, consent refusal and help,
then extracts and compares complete evaluator/strict-VM replay traces. Help leaves
host state, journal sequence, seed and AI budget unchanged.
It also injects journal-write failure to check that state, seed and dialogue do not
escape an uncommitted action. Its fixtures require no API keys or network.

An experiment combining `sunholo/social_dynamics@0.1.0` with the pure
request, decoder and confidence gate from `sunholo/decisions@0.4.0`. Three people
share six units of project materials: the captain, scientist and engineer.
Saved synthetic decisions choose personal responses. The host applies consent,
captain authority, work, relief and received trust consequences.

To replay a recovering journal from the packages repository:

```sh
jq -r 'select(.payload.host_input != null) | .payload.host_input' "$crew_journal" > /tmp/crew-input.ndjson
jq -Rs 'split("\n") | map(select(length > 0))' /tmp/crew-input.ndjson > /tmp/crew-replay.json
ailang run --package-dir examples/crew-lab --entry recoveryRecording --args-file /tmp/crew-replay.json examples/crew-lab/play_flow.ail
# Add --bytecode --strict-bytecode before --package-dir for strict VM replay.
```

Set `crew_journal` to the printed journal path. Recovery replay preserves the
rejection trace and processes subsequent commands; it does not undo or repair the run.

From the packages repository (saved host recordings):

```sh
ailang install --path examples/crew-lab
crew-lab < examples/crew-lab/recordings/agreed-science.ndjson
make -f examples/crew-lab/Makefile experiment
make -f examples/crew-lab/Makefile experiment INPUT=examples/crew-lab/recordings/granted-relief.ndjson
make -f examples/crew-lab/Makefile validate AILANG=/absolute/path/to/ailang
```

Use AILANG v0.52.0 (bf2436a) or a separately validated newer runtime. Installing
locally gives the `[bin]` command a package root independent of the current directory.
Registry publication is separate; the local social kernel is a path dependency.

Five saved experiments offer different consequences:

| Recording | Captain/crew interaction |
|---|---|
| `agreed-science` | Scientist agrees; observations complete, fatigue increases. |
| `refused-order` | Scientist declines; an order proceeds with a personal trust cost. Engineer learns through explicit delivery. |
| `granted-relief` | Scientist requests relief; captain stops the work and assigns rest. |
| `denied-relief` | Captain denies relief; work continues through completion. |
| `competing-projects` | Maintenance completes before science can use the remaining materials. |

The `consent` and `orders` fixtures illustrate alternative authority policies.
These numbers and policies are experimental, with no preferred moral score.
The game adapter and bridge/Commons UI are future work.

The command stream is finite NDJSON. Start with `{"command":"start","policy":"consent"}`
or `orders`, then use `offer`, `ask`, `answer`, `start_task`, `resolve_relief`,
`advance`, `deliver`, `cancel_request` and `abort`. The checked recordings are
complete examples of exact fields. `answer.body` is an escaped JSON string
containing the complete decisions response; `answer.roll` is explicitly recorded.
The request fixes the actor, subject, perception, legal labels, confidence threshold
and captured tick/revision. Changing time or state requires a fresh request.
Cancel stale requests explicitly; retained request IDs cannot be reused.

Each output retains domain state/events and decision bookkeeping. Inspect the
request, raw and normalized alternatives, confidence, gate result, sampled response,
actor operation and resulting received consequences separately. The model's
wire choice and sampled response can differ. All fixtures identify
`synthetic:jev`, carry zero usage and make no claim to live calibration.
OCEAN-like attributes appear in actor context; the saved responses do not establish
that a model used those traits.

`run.sh interpreter INPUT` preflights 1..10000 nonblank lines, each at most
65536 bytes. Direct `[bin]` stdin uses the pinned runtime's `readLine`: a blank
line ends input like EOF. Use the file launcher for strict saved-file framing.
`run.sh vm INPUT` runs the same pure session recording with zero capabilities;
the pinned runtime does not implement stdin `readLine` on strict VM. Parity and
replay targets compare complete traces byte for byte. No provider calls, API keys,
hidden RNG, wall clock, WASM or game build are involved.

Work effects accrue at completion. Stopping work refunds its reservation and
charges no partial fatigue; derived work progress is not partial production.
Material accounting represents projects, not physical ship mass. Requests are
capped at16 pending and64 completed/cancelled, with immutable identity retention;
start another session when retention is exhausted. Trust changes on receipt,
so an uninformed colleague does not react automatically.

Run `make ... validate` to execute native tests, source inline tests, five paths,
replay, strict VM parity, temporary CLI installation and strict package quality.
Contracts that the solver skips are runtime assertions, not proofs. Validation
results are recorded by the sprint's final evidence; this README does not declare
unexecuted checks passed.

`make -f examples/crew-lab/Makefile mutations` runs eight compile-success mutants
against the native behavioural controls. Python is used only as this test harness.
The host's illustrative received-trust deltas are fixed; values and OCEAN traits
enter request context, while guided-play reaction weights additionally use those traits and values.
The host received-trust appraisal remains a fixed illustrative rule.

This local example has no isolated publishing `_smoke.ail`: the clean publishing
workspace cannot resolve the unpublished social kernel path dependency. Installed
CLI tests boot the complete repository package graph. No publication readiness or
complete SMT proof is claimed: retained proof evidence separates verified,
skipped and encoding-error contracts.

For a readable interior view instead of JSON:

```sh
crew-view < examples/crew-lab/recordings/granted-relief.ndjson
make -f examples/crew-lab/Makefile view INPUT=examples/crew-lab/recordings/refused-order.ndjson
```

`crew-view` shows each captain step, crew fatigue/readiness/observations, directed
trust, materials, pending choices and saved responses. It executes the same host
as `crew-lab`; the readable view changes no mechanics. Edit `scenario.ail` to tune
traits, work costs or fixed reaction rules; edit/regenerate a recording to compare
captain choices and saved replies. Rerun immediately—there is no game build.

Start an interactive terminal session with `~/.ailang/bin/crew-view`. The dashboard
uses portable ASCII bar gauges, with exact numbers for each indicator. Type `help`
for commands. A first experiment:

```text
start consent
offer science scientist observations
ask r1 scientist science
reply r1 accept
work science
advance 4
status
quit
```

`reply` is a manually authored offline fixture. It puts probability1 on your chosen
legal response, zero on the others and records `synthetic:manual`, confidence1 and
roll0. To explore uncertainty use, for example, `reply r1 accept 0.4 0.2`; the
existing confidence gate will defer. Full JSON replies can specify distributions.
Friendly-mode mistakes print an error and retain the session for another command;
starting with JSON keeps recorded fail-fast behaviour. Help/status count toward the
finite command limit. This manual `crew-view` mode has no automated live AI or hidden randomness; use
`crew-play` for the guided library experiment.

Try `crew-view < recordings-care.txt` and `< recordings-order.txt` from this folder.
Change `scenario.ail`, restart the CLI and compare the displayed consequences.

The offline fixture, cache and replay controls exercise the integration without
provider calls. Attended OpenRouter smoke on2026-10-09 generated a valid GLM5.3Flash
bundle in one call (1058input/2692output tokens); an identical second session reused
the full selection and seed progression from cache with zero calls/current tokens.
The initial Google attempt had failed with API_KEY_INVALID; the user then selected
OpenRouter. No credentials were saved in the cache or journal.

Runtime verification limits for this slice: all named controls run without skips on
both engines. Source-generated properties for structured records can lack generators;
those skips are reported separately. The pinned source-property harness does not
provide FS capabilities for effectful store contracts, so store boundaries use named
pure controls plus the installed FS/provider-fixture integration harness instead.
SMT proof skips/encoder limitations do not count as runtime test passes. Generated
text is structurally bounded; factual and response-label consistency remain narrative
quality concerns for subsequent play testing.

Runs are bounded experiments. Each atomic journal stops safely at8MiB, with a1MiB
record limit; the last published state is retained when a write cannot fit. The
number of turns before that happens depends on how many projects, responses and
events accumulate. Longer whole-journey simulations will need compact checkpoints;
this release is a watch-sized story lab.
