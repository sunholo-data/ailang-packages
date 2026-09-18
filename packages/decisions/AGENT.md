# sunholo/decisions — agent notes

## What this is

A binding for **System One decision models** (TypeSafe Jev). These are not LLMs: you send a JSON
`state` plus typed `questions`; you get typed answers back, each with a probability distribution and,
for `Choice`/`Score`, a calibrated `confidence`. ~400 ms, ~$0.00003 per call, 32k-token state ceiling,
text only, English primary.

```ailang
import pkg/sunholo/decisions/decide (decide, Noul, Choice, Score, answer, gate, Act, Escalate, Ungateable)
import std/json (jo, kv, js)

-- ! {Net, Env}; run with --caps Net,Env and OPENROUTER_API_KEY set
match decide("typesafe/jev-1.13", jo([kv("ticket", js("My card was charged twice"))]),
             [{ name: "dept", q: Choice("Which team", [{ key: "billing", desc: "Payments" }, { key: "tech", desc: "Bugs" }]) },
              { name: "urgent", q: Noul("The message conveys urgency") }]) {
  Err(e) => …,                                   -- MissingKey | Http | Transport | BadResponse | MissingAnswer | WrongVariant
  Ok(d)  => match answer(d, "dept") {
    Err(e) => …,
    Ok(a)  => match gate(a, 0.8) {               -- YOU pick the threshold; it scales with the stakes
      Act(label)      => …,                      -- confidence >= 0.8
      Escalate(conf)  => …,                      -- confidence <  0.8: a human or a frontier LLM decides
      Ungateable(why) => …                       -- NoulA: threshold the probability yourself
    }
  }
}
```

## Rules for consumers (from the design doc, ratified 2026-09-18)

1. **No default threshold.** This package ships none; `gate` requires `minConfidence`. The vendor's own
   guidance and AILANG's no-silent-fallbacks rule agree: the caller encodes the risk tolerance.
2. **The model is non-deterministic.** Identical calls move the distribution by ±0.04 (argmax usually
   stable). **Bank the whole `Decision`** — `model`, `id`, every answer with its distribution, usage —
   never argmax alone. A bare label is unreproducible and un-auditable.
3. **`Answer.confidence` is calibrated only when `Decision.model` is a System One model.** `parseAnswers`
   is exported so banked bodies can be replayed; it makes no claim about what you feed it. There is
   deliberately no helper that turns a chat-LLM response into an `Answer`; `questionsToJsonSchema` is
   the only LLM-facing export and it yields a schema, not an answer.
4. **Bounded waits:** calls run under the Net effect's deadline (`--net-timeout`, 30 s default). A
   deadline surfaces as `Transport(...)`, a typed `Err`.

## Limitations of v0.1

- **Not in the AI effect's budget or `ailang trace` cost totals.** Calls go through `std/net`, which has
  no cost/span accounting. OpenRouter Broadcast traces are the independent record
  (`gen_ai.operation.name: decisions`). Promotion to `std/ai` (Phase 2) is gated on the shadow
  measurement — see the design doc.
- OpenRouter's Decisions endpoint is **alpha**. `parseAnswers` is fixture-pinned, so a shape change fails
  loudly in this package's tests, not silently in your consumer. `decideWith` takes any endpoint + bearer
  (TypeSafe direct `https://api.typesafe.ai/v1/systemone` accepts the same body).
- The model id is hidden from OpenRouter's `/api/v1/models` listing (beta); do not discover it from there.

## Not to be confused with

`sunholo/motoko_ext_decision_framework` — a keyword-gated *prompt patch* for motoko with no model call.
Different thing; the names are close, the mechanisms are not.

## Testing

```bash
ailang test --package          # 15 offline tests, three real fixtures + three malformed bodies
AILANG_RELAX_MODULES=1 ailang run --caps IO --entry main _smoke.ail   # boot probe, prints OK:
ailang pkg quality .           # the registry's publish report
```

Design + measurements: `ailang/design_docs/planned/m-ai-decide-system-one.md`.
