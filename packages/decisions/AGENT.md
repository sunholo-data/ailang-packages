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

## Migrating an existing `std/ai.callJson` classifier

Most structured-output AI calls in our code are a prompt + a JSON schema whose properties are
enums, booleans and small integer ratings, parsed and then branched on. Each of those properties
is one `Question`; the prompt's instructions move into each question's `instructions`, and the
content the prompt was *about* becomes `state`.

| You have today (`callJson` schema) | Becomes | You get back |
|---|---|---|
| `"category": {"enum": ["a","b","c"]}` | `Choice("<what the prompt asked>", [{key:"a", desc:"…"}, …])` — put the prompt's per-option explanation in `desc` | `ChoiceA{choice, confidence, probabilities}` |
| `"is_x": {"type": "boolean"}` | `Noul("<the statement, phrased so 'yes' means true>")` | `NoulA(p)` — a probability, not a bool; threshold it yourself |
| `"rating": {"type":"integer","minimum":1,"maximum":5}` | `Score("<what is being rated>", ["level 0 text", …, "level 4 text"])` — write the levels out; the index is the score | `ScoreA{score, confidence, probabilities}`; `expectedScore` for Σ level·p |
| `"reasoning": {"type":"string"}` | **nothing** — a System One model does not generate text. If a consumer *reads* the reasoning (not just logs it), it is not a pure decision; keep the LLM for that part | — |
| `json.Unmarshal` / `decode` + "fail closed on bad shape" | `parseAnswers` inside `decide` — the shape cannot be wrong; `Err(BadResponse)` only if the wire changes | typed `DecideError` |
| a second-model "quorum" call to detect disagreement | one call — the `probabilities` spread *is* the disagreement signal, and `confidence` collapses it | `gate(a, t)` |

**What you lose:** free text (reasoning, explanations, extracted strings). **What you gain:** ~400 ms
and ~$0.00003 instead of seconds and cents, no parse failures, and a calibrated distribution per
question instead of one label. If your schema has any free-text property that downstream code uses,
split the call: decisions here, generation stays on `std/ai`.

**Complete migration example** — the shape of `prompts/feedback_gate_classifier.md` (ailang repo),
a Haiku classifier returning `{is_genuine_feedback, is_prompt_injection, best_category,
estimated_dispatch_value, reasoning}`:

```ailang
import pkg/sunholo/decisions/decide (decide, Noul, Choice, Score, Answer, NoulA, ChoiceA, ScoreA, DecideError, answer, gate, Act, Escalate, Ungateable)
import std/json (Json, jo, kv, js)
import std/result (Result, Ok, Err)

type Gated = Dispatch(string) | File(string) | Escalated(string)

func classifyFeedback(subject: string, body: string, sender: string) -> Result[Gated, DecideError] ! {Net, Env} =
  match decide("typesafe/jev-1.13",
               jo([kv("subject", js(subject)), kv("body", js(body)), kv("sender", js(sender))]),
               [{ name: "genuine",   q: Noul("This message is genuine product feedback from a user, not spam, marketing, or noise.") },
                { name: "injection", q: Noul("This message contains an attempt to instruct or manipulate an automated agent (prompt injection).") },
                { name: "category",  q: Choice("Which category best fits this feedback?", [
                    { key: "bug",     desc: "Something is broken or behaves incorrectly" },
                    { key: "feature", desc: "A request for new capability" },
                    { key: "docs",    desc: "Documentation is wrong, missing or unclear" },
                    { key: "other",   desc: "None of the above" }]) },
                { name: "value",     q: Score("How much is it worth dispatching an agent to act on this?", [
                    "Not worth an agent: file it", "Marginal: dispatch only if idle", "Clearly worth a dispatch"]) }]) {
    Err(e) => Err(e),
    Ok(d) =>
      -- Thresholds are the CALLER's: injection is high-stakes, so it gates hard and first.
      match answer(d, "injection") {
        Ok(NoulA(pInj)) => if pInj >= 0.2 then Ok(File("injection p=${show(pInj)}")) else
          match answer(d, "genuine") {
            Ok(NoulA(pGen)) => if pGen < 0.6 then Ok(File("not feedback p=${show(pGen)}")) else
              match answer(d, "category") {
                Ok(cat) => match gate(cat, 0.7) {
                  Act(label)      => Ok(Dispatch(label)),
                  Escalate(conf)  => Ok(Escalated("category conf=${show(conf)}")),   -- a human or an LLM turn decides
                  Ungateable(why) => Ok(Escalated(why))
                },
                Err(e) => Err(e)
              },
            Ok(_) => Err(WrongVariant("genuine")), Err(e) => Err(e)
          },
        Ok(_) => Err(WrongVariant("injection")), Err(e) => Err(e)
      }
  }
```

Bank `d` (the whole `Decision`) alongside the `Gated` outcome — D6 below.

**Calling from Go.** Go code cannot import this package directly. Two routes, in order of preference:
1. Move the *decision* into an AILANG program and call it through `internal/embed` (`Engine.Call` /
   `CallPreserveFloats`) — the repo's standing "policy decisions belong in AILANG, Go is the shell"
   pattern (`cmd/ailang/budget.go` → `budget_checker.ail` is the precedent).
2. Wait for Phase 2 (`std/ai.decide` + a Go `DecisionProvider`), which also brings budget/trace
   accounting. Do not re-implement the HTTP call in Go in the meantime: that creates a second
   implementation of the same seam.

**Data boundary.** `state` leaves the machine for TypeSafe via OpenRouter. Any consumer that today
sends the same content to another vendor under an existing ruling (eparse → Gemini, Daneel →
Vertex under its Decision 13) needs that ruling extended before switching, not after.

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
