# sunholo/oauth

## When to use this package

Use when an AILANG program needs to act as a **user** against a third-party API —
Google, LinkedIn, GitHub, Slack — rather than as a service account. It covers the
whole OAuth2 installed-app flow: build the consent URL, catch the loopback
redirect, exchange the authorization code for a refresh token, store it, and
exchange that refresh token for access tokens later.

Do **not** use it for inbound auth — validating API keys or bearer tokens on your
own endpoints. That is `sunholo/auth`.

For GCP service-to-service auth from ADC or a Cloud Run metadata server, use
`sunholo/gcp_auth`, which is a narrower and simpler thing.

## Why it exists

Before this package, three consumers each implemented half of OAuth2 and none
implemented the other half:

| Consumer | refresh→access | the initial grant |
|---|---|---|
| `sunholo/gcp_auth` | yes, private | out of scope (ADC comes from `gcloud`) |
| `sunholo/linkedin` | yes, duplicated | outside AILANG — "written by the OAuth dance" by a separate binary |
| Daneel bootstrap (2026-09-08) | — | a Python script |

The loopback half kept escaping the language because `std/net` is an HTTP client
and nothing obviously listens. `ailang serve-api` does, via `@route` + `@raw`, so
the whole dance can be AILANG. That is the gap this package closes.

## Quick start

```ailang
import pkg/sunholo/oauth/flow (googleConfig, consentUrl, exchangeCode, readInstalledClient, codeFromQuery)
import pkg/sunholo/oauth/token (readCreds, writeCreds, exchangeRefresh)
```

### Once: get a refresh token

The `@route` handler must live in the module you serve, so the shim is yours —
about fifteen lines:

```ailang
module my_bootstrap

import std/json (Json)
import std/result (Result, Ok, Err)
import pkg/sunholo/oauth/flow (googleConfig, consentUrl, exchangeCode, readInstalledClient, codeFromQuery)
import pkg/sunholo/oauth/token (writeCreds)

func cfg() -> Result[ClientConfig, string] ! {FS} {
  match readInstalledClient("/path/to/client_secret.json") {
    Ok(c) => Ok(googleConfig(c.id, c.secret, "http://127.0.0.1:8765/",
                             "https://www.googleapis.com/auth/gmail.compose",
                             "someone@example.com")),
    Err(e) => Err(e)
  }
}

@route("GET", "/authurl")
export func authUrl() -> string ! {FS} {
  match cfg() { Ok(c) => consentUrl(c), Err(e) => "ERROR: ${e}" }
}

@raw
@route("GET", "/")
export func callback(
  request: { body: string, headers: Json, method: string, path: string, query: Json }
) -> string ! {FS, Net} {
  match cfg() {
    Ok(c) => match codeFromQuery(request.query) {
      Ok(code) => match exchangeCode(c, code) {
        Ok(creds) => { writeCreds("/path/to/token.json", creds); "Authorised." },
        Err(e) => "Exchange failed: ${e}"
      },
      Err(e) => e
    },
    Err(e) => e
  }
}
```

Then:

```bash
ailang serve-api --port 8765 --caps FS,Net,Env my_bootstrap.ail
curl -s localhost:8765/authurl        # open the URL it returns, in a PRIVATE window
chmod 600 /path/to/token.json         # see "Sharp edges"
```

### Thereafter: get a bearer token

```ailang
match readCreds("/path/to/token.json") {
  Ok(creds) => exchangeRefresh("https://oauth2.googleapis.com/token", creds),
  Err(e) => Err(e)
}
```

## Exported functions

| Function | Module | Signature |
|---|---|---|
| `googleConfig` | flow | `(string, string, string, string, string) -> ClientConfig` |
| `consentUrl` | flow | `(ClientConfig) -> string` |
| `readInstalledClient` | flow | `(string) -> Result[{id, secret}, string] ! {FS}` |
| `exchangeCode` | flow | `(ClientConfig, string) -> Result[OAuthCreds, string] ! {Net}` |
| `codeFromQuery` | flow | `(Json) -> Result[string, string]` |
| `readCreds` | token | `(string) -> Result[OAuthCreds, string] ! {FS}` |
| `writeCreds` | token | `(string, OAuthCreds) -> () ! {FS}` |
| `exchangeRefresh` | token | `(string, OAuthCreds) -> Result[string, string] ! {Net}` |
| `postFormBody` / `postForm` | token | `(string, string) -> Result[string, string] ! {Net}` |

Credentials are stored in Google's ADC `authorized_user` shape — not because the
package is Google-specific, but because it is an existing convention that
`sunholo/gcp_auth` and `gcloud` already read, so files written here interoperate.

## Sharp edges

Every one of these was paid for on 2026-09-08. They are the reason this package
exists rather than the code, which is short.

1. **`writeCreds` cannot chmod.** `std/fs.writeFile` takes no mode, so a live
   refresh token lands at the process umask — usually `0644`. Chmod it yourself.
   There is no way to do this from AILANG today.
2. **`httpRequest` is `(METHOD, URL, headers, body)`.** Both leading parameters
   are `string`, so swapping them type-checks, then fails at runtime in about a
   millisecond with `InvalidMethod("unsupported HTTP method: HTTPS://...")`,
   which reads exactly like a dead network. This package hides it; anyone
   writing their own will meet it.
3. **`NetError` has undocumented variants.** `ailang docs std/net` lists four;
   `InvalidMethod` is real and not among them. An exhaustive match over the
   documented four panics with "no pattern matched" — turning a bad error message
   into a crash. Use `show`.
4. **`access_type=offline` AND `prompt=consent` are both required** to get a
   refresh token. Without them you get an access token that expires in an hour,
   no way to renew, and a flow that otherwise looks like it worked.
5. **A second grant returns no refresh token.** Google issues one per grant; a
   repeat authorisation returns only an access token. Revoke at
   `myaccount.google.com/permissions` and redo, or pass `prompt=consent`.
6. **`login_hint` does not bind the account.** The user can still pick a
   different one, producing a working token authorised as the wrong identity,
   silently. **Always verify who the token belongs to** — for Google, call
   `https://www.googleapis.com/drive/v3/about?fields=user` or the Gmail profile
   endpoint. Do a bootstrap in a private window so there is no account chooser.
7. **A Web client fails at the redirect.** You want an installed/**Desktop app**
   client; only that shape has the `installed` key `readInstalledClient` reads.
8. **`serve-api` JSON-wraps handler returns.** A `string` return arrives as
   `{"result": "...", "module": ..., "func": ...}` with HTML escaped, so a
   browser tab shows JSON rather than a rendered page. Cosmetic for a one-shot
   bootstrap; there is no documented content-type control.
9. **Exported functions become endpoints.** `serve-api` publishes every export,
   not only `@route`-annotated ones, plus an OpenAPI doc at
   `/api/_meta/openapi.json`. Fine on a one-shot loopback. For anything
   long-lived pass `--routes-only`.

## Effects

`FS` to read the client file and read/write credentials, `Net` for the token
endpoint. Serve the bootstrap with `--caps FS,Net,Env`. There is no default
outbound host allowlist; `-net-allow-domains` exists on `ailang run` and is not
accepted by `serve-api`.
