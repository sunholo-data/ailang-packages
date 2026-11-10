# [pkg/sunholo/gcp_auth] GOOGLE_APPLICATION_CREDENTIALS is never consulted

**Source:** user feedback via `mcp.ailang.sunholo.com/submit_feedback`
**Reporter:** `mcp-public`
**ailang_version:** v0.57.3 (gcp_auth 0.8.1)
**Category:** bug (no `auto:` prefix — internal issue only, no auto-action)
**Status:** verified by code inspection

## User's report

`getCredentialsPath()` in token.ail hardcodes `$HOME/.config/gcloud/application_default_credentials.json`.
`GOOGLE_APPLICATION_CREDENTIALS` is never consulted, although it's the standard ADC override that
Google client libraries and `gcloud auth application-default print-access-token` both honour.

Impact: a process can't choose its own credentials without changing the machine-wide default file.
On 10 Nov 2026 the default ADC was re-logged as a different account for unrelated work. The speak
Gemini Live demo (demos/streaming/gemini_live, which imports gcp_auth/token) then failed with
`websocket close 1008: Permission 'aiplatform.endpoints.predict' denied on projects/multivac-internal-dev`,
and setting `GOOGLE_APPLICATION_CREDENTIALS` to an authorised user's ADC file changed nothing.

Repro:
1. Default ADC = account A, which lacks `aiplatform.endpoints.predict` on project P.
2. `~/alt.json` = authorized_user ADC for account B, which has the permission (verified with testIamPermissions).
3. `GOOGLE_APPLICATION_CREDENTIALS=~/alt.json speak "hello"` (or any getAccessToken() caller): permission denied as account A.
4. `GOOGLE_ACCESS_TOKEN=$(GOOGLE_APPLICATION_CREDENTIALS=~/alt.json gcloud auth application-default print-access-token) speak "hello"`: works.

Suggested fix: in getCredentialsPath(), use `GOOGLE_APPLICATION_CREDENTIALS` when it's set and non-empty,
and fall back to the default path otherwise. That gives the resolution order
env token → GOOGLE_APPLICATION_CREDENTIALS → default ADC file → metadata server, which matches google-auth.
Also respect `quota_project_id` from whichever file is chosen. Optional: if the file at that path is
`service_account`, either support it (JWT exchange) or return a clear error rather than "Missing refresh_token".

Current workaround: mint `GOOGLE_ACCESS_TOKEN` from gcloud with the alternate credentials file.

## Maintainer verification (code inspection, both modules read in full)

| Claim | Confirmed? |
|---|---|
| `getCredentialsPath()` (token.ail) only uses `getEnvOr("HOME", "/tmp")`; no `GOOGLE_APPLICATION_CREDENTIALS` anywhere in token.ail or project.ail | ✅ |
| `getAccessToken()` resolution order is `env var → ADC file → metadata server` — no ADC-path override consulted | ✅ |
| `tryQuotaProject()` in project.ail also hardcodes the default `home/.config/gcloud/application_default_credentials.json` path | ✅ |
| `parseCredentialsFile` errors `"Missing refresh_token in ADC file"` for a `service_account` ADC file (which has no `refresh_token` field) | ✅ |

Minor discrepancy: the user's snippet shows `home ++ "/.config/..."` (list concat syntax) but the actual
code uses `"${home}/.config/gcloud/application_default_credentials.json"` (string interpolation). Same
behaviour, same bug — the claim stands.

## Suggested fix (for the implementer, not this triage)

- `getCredentialsPath()` in token.ail: `let envPath = getEnvOr("GOOGLE_APPLICATION_CREDENTIALS", "");` then
  `if envPath != "" then envPath else "${home}/.config/gcloud/application_default_credentials.json"`.
- `tryQuotaProject()` in project.ail should read `quota_project_id` from whichever file
  `getCredentialsPath()` (after the fix) returns, not from the hardcoded default path.
- Improve the `service_account` error message: detect the file type (e.g. check for `"type": "service_account"`)
  and return a targeted message like "ADC file is type service_account (needs JWT exchange); this package
  only supports authorized_user ADC files — set GOOGLE_APPLICATION_CREDENTIALS to an authorized_user file
  or use GOOGLE_ACCESS_TOKEN".
- Note: `getEnvOr` has type `(string, string) -> string ! {Env}` — the new code path already sits in a
  function with `! {FS, Env}`, so no effect-row change is needed. Package ceiling `[FS, Net, Env]` is
  unchanged.

## Package tests

`ailang test --package .` reports **no test files** (`0 test files` in `sunholo/gcp_auth`), so there is no
existing test suite to run against this. A pure test for the new `getCredentialsPath()` resolution order
would need a way to inject the env var — `getEnvOr` is `! {Env}` and not injectable, so the fix would
likely need either a contract test or a small refactor to make the path resolution testable.

## Action taken

- Internal issue draft filed here (this file). No code fix, no public PR, no reply to the reporter —
  the `auto:` category prefix was not present on the message.
- No version bump, no publish.
