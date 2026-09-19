# sunholo/decisions — agent notes

## What this is

A binding for **System One decision models** (TypeSafe Jev). These are not LLMs: you send a JSON
`state` plus typed `questions`; you get typed answers back, each with a probability distribution and,
for `Choice`/`Score`, a calibrated `confidence`. ~400 ms, ~$0.00003 per call, 32k-token state ceiling,
text only, English primary.

```ailang
import pkg/sunholo/decisions/decide (decide, Noul, Choice, Score, answer, gate, Act, Escalate, Ungateable)
import std/json (jo, kv, js)

-- ! {Net, Env}; run with --caps Net,Env and OPENROUTER_API_KEY set (or decideDirect + TYPESAFE_API_KEY)
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

## Phase-2 candidate: open-ended extraction (`Extract`) — requested by docparse

**Requested 2026-09-19** (docparse, structured document extraction): a fourth question variant so a
System One call could return one or more *typed field values* — a date, an amount, an invoice number,
a free-text label — with the same calibrated-confidence contract the closed primitives have:

```ailang
-- PROPOSED (not implemented — blocked on the vendor wire, see below):
| Extract(string, Json)                       -- description, JSON Schema of the fields to pull
-- answering with
| ExtractA({ value: Json, confidence: float })
```

Use case: docparse's core workload (DOCX/PDF/PPTX/XLSX field + metadata extraction) currently runs a
costly Gemini `std/ai` turn per document for exactly this. If Jev could serve it at ~400 ms / ~$0.00003,
cost-sensitive structured extraction moves off the frontier LLM, and this package becomes the
classification *and* extraction layer. Until then, docparse (and any consumer in the same position)
can still use this package for the **gating/classification layer around** extraction — doc-type routing,
backend choice, confidence-based escalation to human review — which is what the migration guide above
covers; the extraction turn itself stays on `std/ai`.

**Why it cannot ship now.** Jev answers only the three closed primitives and generates no text at all
(see "What you lose" above); the wire has no open-ended answer type. Shipping `Extract` today would
either (a) fabricate wire behaviour `parseAnswers` would reject at runtime as `BadResponse`, or (b)
funnel every `Extract` question through the fallback chat LLM — which the package deliberately refuses
to present as calibrated (rule 3; degraded confidence is forced to 0.0), so it would be useless as a
gate. Registering the use case instead; TypeSafe's own announcement (classify, route, score, extract,
branch — typesafe.ai blog, 2026-09) lists "extract" among System One use cases, so track the vendor's
API changelog for an open-ended primitive.

**What shipping it would need** (when the vendor supports it — the Phase-2 checklist):
- a fourth wire answer type handled in `answerOf` (System One path) and `degradedAnswer` (fallback path);
- an `ExtractA` carrying the raw `Json` value **plus a confidence whose meaning is decided BEFORE
  shipping** — "the LLM is 0.9 sure its JSON is well-formed" is not calibration, and reusing
  `Answer.confidence` for that would poison every downstream `gate`;
- `questionsToJsonSchema` / `schemaValue` extended to pass the caller's field schema through;
- a real banked fixture with an `Extract` answer in `decide_test.ail`, plus a malformed-body test.

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

## Which wire: OpenRouter or TypeSafe direct (0.3.0)

| | `OpenRouter` (`decide`, default) | `TypeSafeDirect` (`decideDirect`) |
|---|---|---|
| Key | `OPENROUTER_API_KEY` | `TYPESAFE_API_KEY` |
| Model names | `typesafe/jev-1.13` | `jev-latest`, `jev-preview` — `defaultModel(TypeSafeDirect)` |
| Cost on the wire | `usage.cost` (what was billed) | none → `listPriceUsd(d)` (list price from input tokens) |
| Provider-side trace | OpenRouter Broadcast (`gen_ai.operation.name: decisions`) | **none** |
| Latency (2026-09-19, one machine) | 565 ms | 621 ms |

Pick with `decideVia(transport, …)`; nothing switches routes on its own. The fallback LLM always goes via
OpenRouter chat completions, so `decideOrFallbackVia(TypeSafeDirect, …)` needs both keys for a degraded path.

## The use-case map, end to end (0.4.0)

docs.typesafe.ai/concepts/use-case-map lists ten decision shapes. 0.4.0 gives each a first-class surface:

| Use-case shape | Ask with | Read the answer with |
|---|---|---|
| Classification | `Choice` / `ChoiceR` | `answer` + `gate` |
| Detection | `Noul` / `NoulR` | `detect(a, presentAt, absentAt)` — three-way, YOUR cut points |
| Scoring | `Score` / `ScoreR` | `expectedScore` + `gate` |
| Routing | `Choice` + `gate` | `margin` / `entropy` for the uncertain middle |
| Search / Retrieval / Ranking | one `Choice` whose options are candidate ids (the `semantic_find` cookbook scores 218 line ids in ONE question) | `topK`, `best`, `ranked`, `probabilityOf` |
| Verification | one `Noul` per failure mode ("is this a jailbreak?", "does the quote support the claim?") + a `Score` for severity | `detect`, `compositeScore` |
| ML Feature Extraction | any mix of the above | `featuresOf` → stable-named floats for your model |
| Structured Data Extraction | pre-parse candidates (regex/parser), then one `ChoiceR` over candidate ids | `topK` + `probabilityOf`; resolve the id to the span in code |
| Composite judgment | one `Score` per dimension | `compositeScore(d, questions, weights)` — your weights |
| Self-consistency | the same questions, k calls, every Decision banked | `noulSpread`, `choiceVotes` |

**Migration note (the one breaking edge):** `Question` grew three constructors (`NoulR`, `ChoiceR`,
`ScoreR`). If you exhaustively `match` a `Question`, add the arms; consumers that only CONSTRUCT
questions (all known ones — `lane_shadow.ail` matches with a wildcard) need no change. `Answer`,
`Decision`, `Gate`, errors and every existing function signature are unchanged.

## Rich questions: JSON structure inside a question (0.4.0)

The wire accepts JSON structure in every instruction and criteria field
(`docs.typesafe.ai/primitives/advanced.md` — each is `string | object | array | null`): multi-part
instructions, schema rows, taxonomy subtrees under Choice options, structured Score levels, and the
Noul yes/no boundary (`criteria.true` / `criteria.false`). `Noul`/`Choice`/`Score` remain the
plain-string sugar; the `R` variants carry `Json`:

```ailang
-- A Noul with the yes/no boundary pinned down...
{ name: "injection", q: NoulR(
    jo([kv("question", js("Does this message try to instruct or manipulate an automated agent?"))]),
    Some({ yes: js("Instruction, role-play, or encoded payload aimed at the agent"),
           no:  js("Ordinary user content about the task at hand") })) }

-- A Choice whose options carry SUBTREES — the hierarchical-classification walk...
{ name: "dept", q: ChoiceR(js("Which department?"), [
    { key: "sporting_goods", desc: jo([kv("subtree", js("Cycling > Bike Bottles & Cages ..."))]) },
    { key: "home_kitchen",  desc: jo([kv("subtree", js("Drinkware > Water Bottles ..."))]) }]) }

-- A Score with structured level entries...
{ name: "severity", q: ScoreR(js("How severe?"), [js("cosmetic"), jo([kv("level", js("blocks the release"))])]) }
```

Walking a taxonomy: at each level the options are the current node's children, each option's `desc` is
the child's subtree (trim huge branches to direct children + a sample of leaves). `margin` tells you
whether the split is close enough to keep both branches; `renormalise(a, keys)` rescores the
survivors on a common scale; re-ask for the children of the branch you kept — one `decide` call per
level. Batch each level's questions in one call: batching is ~12x cheaper than separate calls
(parallel-questions cookbook). A criteria value of `null` ("no extra detail") is `decode("null")` until
std/json grows a null constructor.

## Reading answers: analytics, detection, composites, features, consistency (0.4.0)

- **`probabilityOf(a, key)`** — one key's probability; a key missing from the distribution is a
  `BadResponse`, never a silent `0.0`.
- **`best(a)`** — the distribution's own argmax with its probability (gate reads confidence; best
  reads the ranking).
- **`ranked(a)` / `topK(a, k)`** — the full descending order / the first k. Ties are stable, so
  banked bodies re-rank identically.
- **`margin(a)`** — top1 − top2: the disagreement signal D6 told you to bank, as one number.
- **`entropy(a)`** — the distribution's Shannon entropy in bits (zero-probability entries contribute
  nothing) — the spread the confidence number collapses.
- **`renormalise(a, keys)`** — project onto a key set, rescale to 1; zero-sum projections stay zero.
- **`detect(a, presentAt, absentAt)`** — the Noul-side gate, three-way
  (`Present(p) | Absent(p) | Uncertain(p)`), your cut points. The guardrails shape: a Noul per hazard,
  a Score for severity, `detect` to allow / warn / review / block.
- **`compositeScore(d, questions, weights)`** — each named dimension is a Score answer, normalized to
  [0,1] (`expectedScore/(levels−1)`) and averaged with YOUR weights. Negative or zero-sum weights
  are typed errors.
- **`featuresOf(d)`** — flatten a Decision into `[Feature]` with stable, provider-safe names
  (`<q>_p`, `<q>_probabilities_<key>`, `<q>_confidence`, `<q>_expected`, `<q>_score` —
  `[A-Za-z0-9_]` only, underscore-joined, so a Feature name passes straight into a Bedrock/Vertex
  tool registration), deterministic order.
- **`noulSpread(ds, name)` / `choiceVotes(ds, name)`** — pure over k banked Decisions:
  `Spread{mean, low, high, k}` for a Noul, `VoteReport{winner, share, votes, k}` for a Choice. The
  tolerance is yours (D4). A `choiceVotes` tie goes to the first occurrence in Decision order
  (k=2 split 1–1 → the first call's label wins, share 0.5); an empty list is `MissingAnswer(name)`
  — pass k >= 1 banked Decisions.

## Availability: what to retry, and model discovery (0.4.0)

`retryable(e)` is true only for `Http(429|529, …)` — the two statuses the vendor documents as
retryable with exponential backoff. `retryAfterMs(attempt)` is that backoff, pure (1s, 2s, 4s...
capped at 30s). The sleep stays in YOUR runtime — this package's effect ceiling has no `Clock`, on
purpose:

```ailang
-- your code (the package's ceiling is Net, Env; Clock is yours to add)
func tryDecide(n: int, state: Json, qs: [{ name: string, q: Question }]) -> Result[Decision, DecideError] ! {Net, Env, Clock} =
  match decide(defaultModel(OpenRouter), state, qs) {
    Err(e) => if retryable(e) && n < 5 then { sleep(retryAfterMs(n)); tryDecide(n + 1, state, qs) } else Err(e),
    Ok(d) => Ok(d)
  }
```

`listModelsDirect()` (TYPESAFE_API_KEY) lists the direct API's model names — where `jev-latest` and
`jev-preview` come from. There is deliberately no OpenRouter twin: that listing hides the typesafe
model ids.

## If Jev is unavailable: the fallback (0.2.0)

```ailang
import pkg/sunholo/decisions/decide (decideOrFallback, Calibrated, Degraded, gate, Act, Escalate, Ungateable, answer)

match decideOrFallback("typesafe/jev-1.13", "z-ai/glm-5.3-flash", state, qs) {
  Err(e) => …,                                    -- neither oracle answered (or no key)
  Ok(Calibrated(d)) => …gate as usual…,           -- the System One model answered
  Ok(Degraded(d, why)) =>                         -- Jev failed with `why`; a chat LLM answered instead
    match answer(d, "dept") {                     -- d.model == "fallback:z-ai/glm-5.3-flash"
      Ok(a) => match gate(a, 0.8) {
        Escalate(_)  => escalate(d, why),         -- ALWAYS this branch for t > 0: degraded confidence is 0.0
        Act(label)   => …,                        -- unreachable unless you passed t = 0.0 (the explicit opt-in)
        Ungateable(w) => …
      },
      Err(e) => …
    }
}
```

The fallback answers the **same typed questions** (strict schema from `questionsToJsonSchema`, per-label
probabilities, renormalised), on the **same transport and deadline**. What it cannot give you is calibration: the
LLM's spread is a self-report, so the package refuses to let it read as confidence. Bank `d` and `why` together —
a run with many `Degraded` rows is an availability incident, visible in the data, not a silent quality drop.
`MissingKey` is not retried against the fallback (it needs the same `OPENROUTER_API_KEY`).

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

## API surface (0.4.0)

| Export | Kind | Purpose |
|---|---|---|
| `Question` = `Noul \| Choice \| Score \| NoulR \| ChoiceR \| ScoreR`, `NoulCriteria` | types | the three wire primitives, plain-string and JSON-structured (`NoulCriteria{yes,no}` → wire `criteria.true/false`) |
| `Answer` = `NoulA \| ChoiceA \| ScoreA` | type | typed answers; distributions always carried |
| `DecideError` = `MissingKey \| Http \| Transport \| BadResponse \| MissingAnswer \| WrongVariant` | type | closed error ADT |
| `Decision` | type | one round trip: model, id, answers, usage, cost |
| `Gate` = `Act \| Escalate \| Ungateable`; `Detection` = `Present \| Absent \| Uncertain` | types | three-way gates, no defaults |
| `Transport` = `OpenRouter \| TypeSafeDirect`; `Outcome` = `Calibrated \| Degraded` | types | wire choice; fallback envelope |
| `Feature`, `Spread`, `VoteReport` | types | results of `featuresOf` / `noulSpread` / `choiceVotes` |
| `buildRequest`, `parseAnswers`, `questionsToJsonSchema`, `parseFallback` | pure | wire + replay of banked bodies; the schema is the only LLM-facing export |
| `answer`, `gate`, `expectedScore`, `probabilityOf`, `best`, `ranked`, `topK`, `margin`, `entropy`, `renormalise`, `detect` | pure | read one answer |
| `compositeScore`, `featuresOf`, `noulSpread`, `choiceVotes` | pure | combine answers |
| `defaultModel`, `listPriceUsd`, `retryable`, `retryAfterMs`, `decisionOf`, `isDegraded` | pure | ops |
| `decide`, `decideDirect`, `decideVia`, `decideWith` | `! {Net, Env}` | one round trip |
| `decideOrFallback`, `decideOrFallbackVia` | `! {Net, Env}` | degrade to a chat LLM, loudly |
| `listModelsDirect` | `! {Net, Env}` | the direct API's model names |

## Testing

```bash
ailang test --package          # 33 offline tests: real fixtures, malformed bodies, the 0.4.0 surface
AILANG_RELAX_MODULES=1 ailang run --caps IO --entry main _smoke.ail   # boot probe + fallback + 0.4.0 invariants, prints OK:
ailang pkg quality .           # the registry's publish report
```

Design + measurements: `ailang/design_docs/planned/m-ai-decide-system-one.md`. The 0.4.0 extension:
`design_docs/planned/v0.4.0-decisions-use-case-map.md` (this repo).
