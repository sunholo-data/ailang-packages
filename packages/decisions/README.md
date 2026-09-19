# sunholo/decisions

**Typed, calibrated decisions for AILANG programs**, backed by a System One decision model
([TypeSafe Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev), via
[OpenRouter's Decisions API](https://openrouter.ai/typesafe/jev-1.13)) — with a chat-LLM fallback that
cannot pretend to be calibrated.

```ailang
import pkg/sunholo/decisions/decide (decide, Noul, Choice, Score, answer, gate, Act, Escalate, Ungateable)
import std/json (jo, kv, js)

match decide("typesafe/jev-1.13",
             jo([kv("ticket", js("My card was charged twice, please fix it today"))]),
             [{ name: "dept",   q: Choice("Which team should handle this?", [
                  { key: "billing", desc: "Payments and refunds" }, { key: "tech", desc: "Bugs and integrations" }]) },
              { name: "urgent", q: Noul("The message conveys urgency") }]) {
  Err(e) => …,
  Ok(d)  => match answer(d, "dept") {
    Ok(a)  => match gate(a, 0.8) {          -- you choose the threshold; it scales with the stakes
      Act(team)      => route(team),        -- calibrated confidence ≥ 0.8
      Escalate(conf) => askAHuman(d, conf), -- < 0.8: the model is telling you it isn't sure
      Ungateable(w)  => …                   -- a Noul has a probability, not a confidence
    },
    Err(e) => …
  }
}
```

~400 ms, ~$0.00003 per call, and the answer is a **closed ADT** with the full probability distribution —
not a string to parse.

## Why this fits AILANG

AILANG makes effects explicit, types closed, and non-determinism visible. A System One answer is exactly
that shape: `decide` is `! {Net, Env}`, its result is `Result[Decision, DecideError]`, every answer carries its
distribution, and the one policy-shaped helper (`gate`) is three-way — `Act | Escalate | Ungateable` — so a
wrong variant can never be mistaken for "not confident enough". There is **no default threshold** in the
package; the caller encodes the risk.

## What's here

| | |
|---|---|
| `Question = Noul \| Choice \| Score` | the three TypeSafe primitives: P(yes), categorical, ordinal |
| `Answer = NoulA \| ChoiceA \| ScoreA` | typed answers; distributions always carried |
| `decide` / `decideDirect` / `decideVia` / `decideWith` | one round trip via OpenRouter, via TypeSafe direct, via an explicit `Transport`, or any endpoint + bearer |
| `decideOrFallback` → `Calibrated \| Degraded` | chat-LLM fallback with confidence **forced to 0** — acting on it is an explicit opt-in |
| `gate`, `answer`, `expectedScore`, `parseAnswers`, `questionsToJsonSchema` | pure helpers; `parseAnswers` replays a banked body |

## How we use it

We're the [AILANG](https://ailang.sunholo.com) team. Our agent harness makes many small classification
decisions — route a failure to a lane, gate a feedback message, triage an email — that used to cost a
frontier-LLM turn each. The first measurement (20 hand-labelled design docs) put Jev at the same accuracy
as a cheap reasoning LLM at ~1/30 the latency and ~1/10 the cost, with zero timeouts, and its confidence
separated the one clean miss from the hits. Write-ups: the
[design doc](https://github.com/sunholo-data/ailang/blob/dev/design_docs/implemented/v0_40_1/m-ai-decide-system-one.md)
and the [shadow measurement](https://github.com/sunholo-data/ailang/blob/dev/design_docs/implemented/v0_40_1/m-ai-decide-system-one-shadow-report.md).

## Install

```toml
# ailang.toml
[dependencies]
"sunholo/decisions" = "0.3.0"
```

`ailang lock`, then run with `--caps Net,Env` and `OPENROUTER_API_KEY` set (or `TYPESAFE_API_KEY` for `decideDirect`). Agent-facing notes, the migration
guide from `std/ai.callJson` classifiers, and the consumer rules are in [AGENT.md](AGENT.md)
(`ailang pkg-docs sunholo/decisions`).

## Honest limits

The model is **non-deterministic** (±0.04 on the distribution between identical calls; bank the whole
`Decision`, never argmax). In this version calls go through `std/net`, so they are bounded by `--net-timeout`
(30 s) but sit outside the AI effect's budget and trace-cost accounting. Text only, English primary, 32k-token
state. OpenRouter's Decisions endpoint is alpha.

Apache-2.0 · [sunholo-data/ailang-packages](https://github.com/sunholo-data/ailang-packages/tree/main/packages/decisions)
