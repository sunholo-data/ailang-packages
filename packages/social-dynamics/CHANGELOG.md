# Changelog

## 0.4.1

Faster wire framing. `singleObject` (and so `decodeProposal` and every host
that frames its input with it) checks the object's framing in one left fold
over the characters. 0.4.0 walked them with a cons pattern, and on the bytecode
VM each step copies the rest of the list (ailang#1827), so framing cost grew with
the square of the line's length. A crew host's auto-run spends most of its time
here: its answer commands carry the proposal as escaped JSON of a few KB.

- New export `framed(text)`: the framing check alone (no JSON decode).
- Behaviour is unchanged. `framing_test.ail` keeps the 0.4.0 framer as an
  oracle and checks that both agree on 25 framing cases (escapes, quoted
  brackets, mismatched closers, trailing data and whitespace).

## 0.4.0

The host can halt running work. `tasks.halt(config, state, Host, task, reason)`:
- **Who and what:** host only, and only a Working task.
- **Effect:** the task's reservation is released with nothing consumed, as
  for released relief, and the task is Stopped at the current tick.
- **Event:** a new `TaskHalted(task, reason)` event (`task_halted` on the
  wire).

Hosts use it when the world takes away capacity that running work holds; the
crew host uses it when crew argue over lost ship capacity. Everything else is
unchanged.

## 0.3.0

Add a pure personality sidecar with receipt-bound major-event responses. OCEAN
traits move only over simulation time, at most one point per trait per turn,
within individual baseline and world bounds. Ordinary perceived interactions
can influence an active response but cannot initiate one. Exact retries are
idempotent; altered receipts, rewinds and full retention return typed errors.

## 0.2.0

Breaking: Effect adds opt-in BoundedIndicatorDelta. Checked arithmetic and reference/observer ownership gates remain; only a valid configured indicator result saturates at its bounds. Existing IndicatorDelta and wire tags are unchanged.

## 0.1.0

Experimental pure social dynamics kernel: bounded domain indicators, directed
relationships and evidence-gated appraisal, explicit project offers/assignments,
conserved materials and work allocations, individual commitment consent, hysteresis
conditions, deterministic scheduling/continuations, immutable configuration,
atomic proposals and strict canonical recordings. Standalone ship and community
experiments live in `examples/social-dynamics`. No provider calls or game coupling.
