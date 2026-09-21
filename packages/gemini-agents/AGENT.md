# sunholo/gemini_agents

Google's managed agents through the **Interactions API on Vertex AI**, under Application
Default Credentials. Version 0.1.0 names one agent — **Deep Research**
(`deep-research-preview-04-2026`): a minutes-long, Google-search-grounded research run that
returns a cited report. The agent ids are a proven closed set (`agents.agentOk`); adding one is
a version bump with its own probe.

## Quick start

```ailang
import pkg/sunholo/gemini_agents/request (startBody)
import pkg/sunholo/gemini_agents/interaction (start, get, delete)
import pkg/sunholo/gemini_agents/answer (statusRaw, reportOf, sourcesOf, usageOf, rewriteCitations, sourcesBlock)
import pkg/sunholo/gemini_agents/agents (statusOf)

-- 1. start — background, stored, with a nonce that is the request's identity
match start("my-gcp-project", startBody("What changed in EU AI Act enforcement in 2026?", nonce)) {
  Ok(id) => -- keep id; poll later
  Err(e) => -- auth or HTTP failure, named
}

-- 2. poll (minutes later; most runs finish inside 20)
match get("my-gcp-project", id) {
  Ok(rec) => match statusOf(statusRaw(rec)) {
    "done"    => { let report = rewriteCitations(reportOf(rec)); let sources = sourcesBlock(sourcesOf(rec)); … },
    "running" => -- come back next beat
    _         => -- failed: errorOf(rec); transient(rec) says whether one retry is reasonable
  },
  Err(e) => …
}

-- 3. delete when harvested — Google stores the request and the report until you do
delete("my-gcp-project", id)
```

Run with `--caps Net,FS,Env --net-allow-domains aiplatform.googleapis.com,oauth2.googleapis.com`
and a `--net-timeout` above the default 30 s (a cold project's first POST has been seen to hang
60 s).

## Modules

| Module | What | Kind |
|---|---|---|
| `agents` | `deepResearch()`, `agentOk(id)`, `statusOf(status)` → `running`/`done`/`failed`, `retryOk(attempt, transient)` | **proven** (`ailang verify`; each broken once in the package's CI) |
| `request` | `startBody(question, nonce)`, `noncePart`/`nonceOf`, `interactionsUrl`/`interactionUrl`, `apiRevision()` | pure, tested |
| `answer` | over the raw record: `statusRaw`, `idOf`, `reportOf`, `sourcesOf` (url_citation annotations, first-seen, deduplicated), `recordNonce`, `usageOf` (tokens, searches), `errorOf`, `transient`, `rewriteCitations` (`[cite: n]` → `[n]`), `sourcesBlock` | pure, tested against a captured record |
| `interaction` | `start`, `get`, `list` (ids + `next` page token), `cancel`, `delete` | `{FS, Net, Env}` — ADC via `sunholo/gcp_auth` |

## What the API does (measured 21 Sept 2026, Vertex, `Api-Revision: 2026-05-20`)

- `background:true` and `store:true` are **mandatory** for agent interactions; both other settings are refused.
- A new interaction is **listed immediately** after the POST returns; `list` pages with `next_page_token` (newest first).
- The input's text parts are echoed back verbatim as `user_input` steps — the nonce is how you match a record to a request; there is no client idempotency key.
- `cancel` returns the record with its usage so far; `delete` straight after a cancel is refused *"is not finished yet"* and succeeds seconds later — treat a refused delete as *pending*, not failed.
- One run in six failed with `Internal error encountered.` (`api_error`, code 13); the same request re-sent completed. `transient` names that case.
- Not on Vertex (as of this version): `deep-research-max-preview-04-2026`, `antigravity-preview-09-2026`, environments, a custom agent's `agent_config.model`. The Developer API (`generativelanguage.googleapis.com`, API key) has them; this package does not speak it yet.

## Cost

Google's estimate is $1–3 per Deep Research task (~80 searches, ~250k input tokens); short questions measured here ran 22k–60k tokens with 2–4 searches. `usageOf` is what you record.

## Dependencies

- `sunholo/gcp_auth` — the ADC token (file refresh exchange, or the metadata server).
