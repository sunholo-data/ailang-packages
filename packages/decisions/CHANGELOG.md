# Changelog — sunholo/decisions

## 0.4.0 — 2026-09-30

**The use-case map release** (docs.typesafe.ai use-case map / patterns / cookbooks): the three wire
primitives were half of what Jev does — this version adds the surface the vendor's patterns are built
from. All new helpers are pure; the only breaking edge is three new `Question` constructors. Design:
`design_docs/planned/v0.4.0-decisions-use-case-map.md`.

- **Breaking: `Question` grows three constructors.** `NoulR(Json, Option[NoulCriteria])`,
  `ChoiceR(Json, [{ key: string, desc: Json }])`, `ScoreR(Json, [Json])` — the same three primitives
  with JSON-structured instructions and criteria (primitives/advanced.md: every EntryType field accepts
  `string | object | array | null`), plus the wire's optional Noul `criteria.true/criteria.false`
  (`NoulCriteria = { yes, no }`; `true`/`false` are AILANG keywords). `Noul`/`Choice`/`Score` are
  unchanged. Answers parse identically — only `buildRequest` output differs. Only exhaustive `match`
  on `Question` breaks; every known consumer constructs questions (lane_shadow.ail matches with a
  wildcard).
- **Distribution analytics (Search / Retrieval / Ranking):** `probabilityOf(a, key)` (a key missing
  from a distribution is a `BadResponse`, never a silent 0.0), `best(a)`, `ranked(a)` (descending,
  ties stable), `topK(a, k)` (requires k >= 1), `margin(a)` (top1−top2 — D6's disagreement signal as
  one number), `entropy(a)` (bits; zero-probability entries contribute 0), `renormalise(a, keys)`
  (project + rescale; zero-sum stays zero — the hierarchical beam step).
- **Detection gating:** `detect(a, presentAt, absentAt)` -> `Present(p) | Absent(p) | Uncertain(p)` —
  the Noul-side twin of `gate` (which stays confidence-only): two caller-supplied cut points,
  three-way, no defaults (D4). `WrongVariant` on Choice/Score answers.
- **Composite scoring:** `compositeScore(d, questions, weights)` — each named dimension's Score answer
  normalized to [0,1] (expectedScore / (levels−1)) and averaged with the caller's weights. Negative
  or zero-sum weights are typed errors, not clamps.
- **ML feature extraction:** `featuresOf(d)` -> `[Feature]` with stable, provider-safe names
  (`<q>_p`, `<q>_probabilities_<key>`, `<q>_confidence`, `<q>_expected`, `<q>_score`), deterministic
  order — feed a classical model alongside structured data. Underscore-joined and built without
  string interpolation in the name field on purpose: the registry's tool-name scan reads
  name-field literals and rejects `$`/`.` (Bedrock/Vertex tool-name rules) — the first publish
  attempt was refused over the original dotted templates and was fixed pre-release (nothing had
  shipped).
- **Self-consistency (D6 made queryable):** `noulSpread(ds, name)` -> `Spread{mean, low, high, k}` and
  `choiceVotes(ds, name)` -> `VoteReport{winner, share, votes, k}` — pure over k banked Decisions;
  the tolerance stays the caller's.
- **Availability:** `retryable(e)` (HTTP 429/529 per api.md) + `retryAfterMs(attempt)` (1s doubling,
  capped at 30s; the sleep stays in the caller's runtime — the ceiling has no Clock, on purpose) and
  `listModelsDirect()` (GET /v1/models, TYPESAFE_API_KEY — where `jev-latest`/`jev-preview` come from;
  no OpenRouter twin: that listing hides the typesafe ids).
- `x-typesafe-sdk: sunholo-decisions/0.4.0`. 14 new native tests (R-question serialization, schema
  equivalence, probabilityOf/best/ranked/topK/margin/entropy values, renormalise, detect three-way,
  compositeScore values + typed errors, featuresOf names/counts, spread/votes across three banked
  bodies, retry classification); `_smoke.ail` additionally asserts the R-fallback degradation and the
  0.4.0 invariants offline (executed by `ailang pkg quality`).
- **Fix, pre-publish (caught by the first `ailang pkg quality` run — 2/33 tests failed):** `entropy`
  computed `Σ p·log₂p` without the negation — a concentrated distribution scored 0.0 as expected, but
  every real split came out *negative* (the lane fixture: −1.1642 bits). Each term is now negated
  (`−p·log₂p`) and `entropy` gained `ensures Ok(x) => x >= 0.0`. The `choiceVotes` test fixture
  `bodyDeptTechnical` answered only `department` while parsed against the three-question ticket list —
  `parseAnswers` correctly refused with `MissingAnswer`; the fixture now answers all three questions,
  as any banked Decision from one call would.

## 0.3.0 — 2026-09-19

- **TypeSafe direct transport.** `Transport = OpenRouter | TypeSafeDirect`; `decideVia(transport, …)`,
  `decideDirect(model, …)` (TYPESAFE_API_KEY, `https://api.typesafe.ai/v1/systemone`, model names
  `jev-latest` | `jev-preview`), `decideOrFallbackVia(transport, …)`, `defaultModel(transport)`. `decide` and
  `decideOrFallback` are unchanged (OpenRouter). Measured 2026-09-19 through the package: direct 621 ms,
  OpenRouter 565 ms, identical token counts.
- `listPriceUsd(d)`: the wire cost when present, else input tokens × the vendor list price ($0.042/MTok) —
  the direct API reports no cost. Reproduces OpenRouter's billed `usage.cost` exactly on the same call.
- Every call sends `x-typesafe-sdk: sunholo-decisions/0.3.0`.
- Observability note: direct calls produce **no OpenRouter Broadcast trace**; if you rely on Broadcast as the
  provider-side record, stay on OpenRouter.

## 0.2.0 — 2026-09-18

- **Fallback when the System One model is unavailable.** `decideOrFallback(model, fallbackModel, state, questions)`
  returns `Outcome = Calibrated(Decision) | Degraded(Decision, DecideError)`. On `Transport`/`Http`/`BadResponse`/
  `MissingAnswer` from the System One call it asks a chat LLM (OpenRouter slug, e.g. `z-ai/glm-5.3-flash`) the same
  questions via a strict `json_schema` on the same Net transport and deadline. A degraded `ChoiceA`/`ScoreA` has
  **confidence forced to 0.0**, so `gate(a, t)` returns `Escalate(0.0)` for any `t > 0` — acting on a fallback answer
  is an explicit opt-in (`gate(a, 0.0)` or matching `Degraded`). `Decision.model` is `fallback:<chat-model>`.
  `parseFallback`, `decisionOf`, `isDegraded` exported. `MissingKey` does not trigger the fallback (same key).
- `questionsToJsonSchema` now encodes a shared `schemaValue`; no behaviour change.
- Fallback invariants are asserted in `_smoke.ail` (executed by `ailang pkg quality`) rather than a `*_test.ail`:
  `ailang test` mis-resolves calls on this path ("function expects 3 arguments, got 1") that `ailang run` evaluates
  correctly — the same code passes under `run`. Filed against ailang (harness flat-environment injection).

## 0.1.2 — 2026-09-18

- Docs only: AGENT.md gains a migration guide from `std/ai.callJson` classifiers (schema-property →
  Question mapping, what is lost, a complete feedback-gate example, the Go route via `internal/embed`,
  the data-boundary note). No code change.

## 0.1.1 — 2026-09-18

- Fix: `questionsToJsonSchema` emitted `additionalProperties` as the string `"false"`; now a JSON boolean
  (strict structured-output modes reject the string form). Test added.

## 0.1.0 — 2026-09-18

First release. Typed decisions from a System One model (TypeSafe Jev) via
OpenRouter `POST /api/alpha/decisions`, in pure AILANG.

- `Question = Noul | Choice | Score`, `Answer = NoulA | ChoiceA | ScoreA` (distributions always carried),
  `DecideError` (6 variants), `Decision` (wire `model`/`id`, usage, cost), `Gate = Act | Escalate | Ungateable`.
- Pure: `buildRequest`, `parseAnswers` (replayable from a banked body), `questionsToJsonSchema`
  (the only LLM-facing export — a schema, never an answer), `answer`, `gate`, `expectedScore`.
- Effectful: `decide` (OpenRouter, `OPENROUTER_API_KEY`) and `decideWith` (explicit endpoint + bearer), `! {Net, Env}`.
- No default confidence threshold anywhere; `gate` requires one and is three-way so a wrong variant is
  never read as "low confidence".
- 15 native tests over three real banked responses (two OpenRouter, one TypeSafe direct) and three malformed bodies.

Known limitations: the model is non-deterministic (bank the distribution, not argmax); calls are bounded by
`--net-timeout` (30 s default) but are outside the AI effect's budget and `ailang trace` cost totals.
Design: `ailang/design_docs/planned/m-ai-decide-system-one.md`.
