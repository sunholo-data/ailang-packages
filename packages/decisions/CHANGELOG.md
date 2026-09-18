# Changelog — sunholo/decisions

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
