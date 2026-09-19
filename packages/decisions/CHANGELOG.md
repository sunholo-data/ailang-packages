# Changelog — sunholo/decisions

## 0.3.1 — 2026-09-19

- Docs only: AGENT.md registers docparse's requested Phase-2 candidate — an open-ended
  `Extract(description, schema) -> ExtractA{value, confidence}` question for typed field extraction
  (dates, amounts, invoice numbers, free-text labels) with calibrated confidence. Blocked until the
  vendor wire supports it: Jev answers only `noul`/`choice`/`score` and generates no text, and the
  fallback path deliberately never presents an LLM answer as calibrated. The section spells out the
  full shipping checklist (wire answer type, calibrated-confidence semantics, schema passthrough,
  banked fixture). No code change; every existing export is unchanged.
- Header string `x-typesafe-sdk: sunholo-decisions/0.3.1` follows the version.

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
