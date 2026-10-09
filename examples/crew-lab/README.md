# Captain and crew CLI lab

An offline experiment combining `sunholo/social_dynamics@0.1.0` with the pure
request, decoder and confidence gate from `sunholo/decisions@0.4.0`. Three people
share six units of project materials: the captain, scientist and engineer.
Saved synthetic decisions choose personal responses. The host applies consent,
captain authority, work, relief and received trust consequences.

From the packages repository:

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
enter request context, with trait-weighted appraisals left for a later experiment.

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
finite command limit. There is no automated live AI or hidden randomness.

Try `crew-view < recordings-care.txt` and `< recordings-order.txt` from this folder.
Change `scenario.ail`, restart the CLI and compare the displayed consequences.
