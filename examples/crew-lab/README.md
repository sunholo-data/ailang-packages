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
