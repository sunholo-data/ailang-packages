#!/bin/bash
# Mutation check for every 0.2 control (design §Testing Strategy: "revert it
# in a scratch copy and confirm a named test fails"). Each mutant is applied
# to a FRESH COPY of the package in a temp dir (the checkout is never
# touched), and must make the named case fail while the rest of its suite
# still runs (so a mutant that merely breaks compilation does not count).
#   bash tests/mutation_check.sh            # all mutants
#   bash tests/mutation_check.sh M07 M12    # some
set -uo pipefail
PKG="$(cd "$(dirname "$0")/.." && pwd)"
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT
ONLY=" $* "
total=0; killed=0; rc=0

# mutant ID FILE FROM TO KIND ARG CASE [WHY]
#   KIND suite  ARG = suite name; CASE must not PASS, another case must PASS
#   KIND test   ARG = -;  `ailang test --package .`: CASE must fail, others pass
#   KIND verify ARG = file; `ailang verify ARG`: CASE must be a VIOLATION
mutant() {
  local id="$1" file="$2" from="$3" to="$4" kind="$5" arg="$6" case="$7" why="${8:-}"
  [ "$ONLY" != "  " ] && [[ "$ONLY" != *" $id "* ]] && return 0
  total=$((total + 1))
  local dir="$WORK/$id"
  rm -rf "$dir"; cp -R "$PKG" "$dir"
  if ! FROM="$from" TO="$to" perl -0777 -i -pe 'BEGIN{$c=0} $c += s/\Q$ENV{FROM}\E/$ENV{TO}/g; END{exit($c==1?0:3)}' "$dir/$file"; then
    echo "BROKEN $id: mutation site not found exactly once in $file (update the harness)"; rc=1; return
  fi
  local out alive=0 dead=0
  case "$kind" in
    suite)
      out=$(cd "$dir" && AILANG_RELAX_MODULES=1 ailang run --caps IO,SharedMem,Rand,Clock,Env --entry main tests/client_models.ail -- "$arg" 2>&1)
      grep -q '^PASS ' <<<"$out" && grep -vqxF "PASS $case" <<<"$(grep '^PASS ' <<<"$out")" && alive=1
      grep -qxF "PASS $case" <<<"$out" || dead=1 ;;
    test)
      out=$(cd "$dir" && ailang test --package . 2>&1)
      grep -q "✓" <<<"$out" && alive=1
      grep -F "✗" <<<"$out" | grep -qF "$case" && dead=1 ;;
    verify)
      out=$(cd "$dir" && AILANG_RELAX_MODULES=1 ailang verify "$arg" 2>&1)
      grep -q "VERIFIED" <<<"$out" && alive=1
      grep -E "VIOLATION" <<<"$out" | grep -qw "$case" && dead=1 ;;
  esac
  if [ $alive -eq 1 ] && [ $dead -eq 1 ]; then killed=$((killed + 1)); echo "killed   $id  $case  ($why)"
  else echo "SURVIVED $id  $case  ($why) alive=$alive dead=$dead"; grep -E '^(FAIL|RUN)|rror' <<<"$out" | head -5; rc=1; fi
}

F=flow.ail; C=clients.ail; K=core.ail; D=cimd.ail
# ---- M1a: client authentication (T11, T16), legacy guard, kinds, redirects
mutant M01 $F $'      if r.method != presented then Err(invalidClient("this client authenticates with ${r.method}"))\n      else if presented == "none"' \
              $'      if presented == "none"' suite confidential "TestConfidentialWithoutSecret" "record-method check dropped (T16)"
mutant M02 $F $'      if r.method != presented then Err(invalidClient("this client authenticates with ${r.method}"))\n      else if presented == "none"' \
              $'      if presented == "none"' suite refresh_policy "TestStableRefreshNeedsClientAuth" "record-method check dropped: stable token alone"
mutant M03 $F '  storedDigest != "" && constantTimeEqual(digestOf(presented), storedDigest)' '  storedDigest != ""' \
              suite confidential "TestWrongSecretInvalidClient" "secret comparison dropped"
mutant M04 $F $'    else if presented != "none" then Err(invalidClient("a client metadata document client authenticates with none and sends no client secret"))\n' '' \
              suite confidential "TestCimdWithSecretRefused" "CIMD client may present a secret"
mutant M05 $F 'if clientKind(clientId) != "cimd" then Err(invalidClient("exchangeCode serves' 'if false then Err(invalidClient("exchangeCode serves' \
              suite confidential "TestLegacyExchangeRefusesRegisteredId" "legacy exchangeCode guard dropped"
mutant M06 $F 'if clientKind(clientId) != "cimd" then Err(invalidClient("refreshTokens serves' 'if false then Err(invalidClient("refreshTokens serves' \
              suite confidential "TestLegacyRefreshRefusesRegisteredId" "legacy refreshTokens guard dropped"
mutant M07 $F $'        else if kindOf(rec) != auth.kind then Err(invalidGrant("the client kind does not match the code"))\n' '' \
              suite confidential "TestKindMismatchRefused" "code kind check dropped (T16)"
mutant M08 $F 'Some(r) => authorizeChecked(h, loginUrl, clientId, "registered", r.origin, r.redirectUris,' 'Some(r) => authorizeChecked(h, loginUrl, clientId, "registered", r.origin, [redirectUri],' \
              suite confidential "TestRegisteredRedirectExact" "registered redirect allowlist bypassed"
mutant M09 $F '    let digest = if isSecretMethod(method) then digestOf(secret) else "";' '    let digest = if isSecretMethod(method) then secret else "";' \
              suite confidential "TestSecretNeverStored" "secret stored instead of its digest"
mutant M10 $C '  ((r.origin == "operator" && cfg.confidential) || (r.origin == "dcr" && cfg.dcr))
    && (isSecretMethod' '  ((r.origin == "operator") || (r.origin == "dcr" && cfg.dcr))
    && (isSecretMethod' suite confidential "registered clients need cfg.confidential" "cfg.confidential gate dropped"
mutant M11 $F $'        else if pkceOk(verifier, getStringOr(rec, "challenge")) == false then Err(invalidGrant("PKCE verification failed"))\n' '' \
              suite confidential "confidential client still needs PKCE" "PKCE dropped (D4)"
mutant M12 $K 'if startsWith(id, "mco_") && strContains(id, "://") == false && lowerHex32(substring(id, 4, length(id))) then "registered"' \
              'if startsWith(id, "mco_") && strContains(id, "://") == false && length(id) == 36 then "registered"' \
              test - "client kind rejects near misses" "registered id hex check dropped (T14)"
mutant M13 $K '  else if startsWith(id, "https://") then "cimd"' '  else if startsWith(id, "mco_") || startsWith(id, "https://") then "cimd"' \
              verify core.ail clientKind "namespaces overlap: mco_ id read as CIMD (T14)"
# ---- M1b: DCR (T12, T15)
mutant M14 $C '  dcrRedirectOk(uri, dcrHostAllowed(httpsHost(uri), hosts), stripLoopbackPort(uri) != "")' '  dcrRedirectOk(uri, httpsHost(uri) != "", stripLoopbackPort(uri) != "")' \
              suite dcr "TestDcrRedirectAllowlist" "dcrRedirectHosts ignored"
mutant M15 $K 'firstStop(rest, ["/", "?", "#", "\\"])' 'firstStop(rest, ["/"])' \
              test - "host ends at the query" "host parser ignores ?/#/\\ (one parser: CIMD and DCR)"
mutant M16 $C '    && (loopback || (startsWith(uri, "https://") && strContains(uri, "@") == false && hostAllowed))
}' '    && (loopback || (startsWith(uri, "https://") && hostAllowed))
}' verify clients.ail dcrRedirectOk "userinfo allowed in a DCR redirect"
mutant M17 $F '      if underLimit(nCaller, cfg.dcrPerCallerPerHour) == false then' '      if false then' \
              suite dcr "TestDcrRateLimitPerCaller" "per-caller limit dropped"
mutant M18 $F '      else if underLimit(nGlobal, cfg.dcrGlobalPerDay) == false then' '      else if false then' \
              suite dcr "TestDcrGlobalCap" "global cap dropped"
mutant M19 $F '                  expiresAt: nowSec + dcrUnusedTtlSec() };' '                  expiresAt: 0 };' \
              suite dcr "TestDcrUnusedExpires" "unused-registration TTL dropped"
mutant M20 $F '      Some(r) => storeClient(h, touchClient(r, nowSec), nowSec)' '      Some(r) => true' \
              suite dcr "TestDcrUsedRegistrationSlides" "first-use slide dropped"
mutant M21 $C '  if length(body) > dcrMaxBodyBytes() then badMeta' '  if false then badMeta' \
              suite dcr "TestDcrBodyCap" "body cap dropped"
mutant M22 $C '  else match nth(parts, listLength(parts) - 1 - trustedHops) {' '  else match nth(parts, trustedHops) {' \
              suite dcr "TestTrustedCallerIpIgnoresForgedPrefix" "first X-Forwarded-For entry trusted"
mutant M23 $F '                              ++ (if getStringOr(req, "registered") == "" then [] else' '                              ++ (if true then [] else' \
              suite dcr "TestDescribeRequestOmitsClientName" "unverified (dcr) marker dropped (T15)"
mutant M24 $C '            else if authMethodOk(method, advertisedAuthMethods(cfg)) == false then badMeta' '            else if false then badMeta' \
              suite dcr "dcr secret method needs cfg.confidential" "DCR auth method not intersected with ours"
# ---- M1c: refresh policy (T13), revocation, pruning (T8)
mutant M25 $F 'refreshRecord(fam, account, clientId, kindOf(rec), "stable", false, stableIdleExpiresAt' 'refreshRecord(fam, account, clientId, kindOf(rec), "stable", true, stableIdleExpiresAt' \
              suite refresh_policy "TestStableRefreshNoRotation" "stable token marked used"
mutant M26 $F 'account, fam, live, stable, nowSec) {' 'account, fam, live, false, nowSec) {' \
              suite refresh_policy "TestStableRefreshNoRotation" "stable refresh rotates"
mutant M27 $K '  isExpired(nowSec, idleExpiresAt) == false && isExpired(nowSec, absoluteExpiresAt) == false' '  isExpired(nowSec, idleExpiresAt) == false' \
              verify core.ail stableRefreshLive "absolute lifetime not checked"
mutant M28 $K '  if nowSec + 2592000 < absoluteExpiresAt then nowSec + 2592000 else absoluteExpiresAt' '  nowSec + 2592000' \
              verify core.ail stableIdleExpiresAt "idle deadline not capped at the absolute one"
mutant M29 $K '  isExpired(nowSec, idleExpiresAt) == false && isExpired(nowSec, absoluteExpiresAt) == false' '  isExpired(nowSec, idleExpiresAt) == false' \
              test - "stable refresh dead at either deadline" "absolute lifetime not checked (unit)"
mutant M30 $F 'stableRefreshLive(nowSec, getIntOr(rec, "idle_expires_at"), getIntOr(rec, "absolute_expires_at")) == false' 'stableRefreshLive(nowSec, getIntOr(rec, "absolute_expires_at"), getIntOr(rec, "absolute_expires_at")) == false' \
              suite refresh_policy "TestStableRefreshIdleExpiry" "idle expiry ignored"
mutant M31 $F 'let next = if stable then refreshRecord(fam, account, clientId, kindOf(rec), "stable", false, stableIdleExpiresAt(nowSec, absExp), absExp)' 'let next = if stable then refreshRecord(fam, account, clientId, kindOf(rec), "stable", false, nowSec + 2592000, nowSec + 15552000)' \
              suite refresh_policy "TestStableRefreshAbsoluteExpiry" "absolute deadline slides with each refresh"
mutant M32 $F '  else if refreshPolicyOk(refreshPolicy, method) == false then Err' '  else if false then Err' \
              suite refresh_policy "TestStableRefusedForPublicClient" "stable allowed for a public client (D3)"
mutant M33 $F '  filter(\p. match p { (_, e) => e < 0 || isExpired(nowSec, e) == false }, zip(tokens, exps))' '  zip(tokens, exps)' \
              suite refresh_policy "TestFamilyDigestsPruned" "family digests never pruned (T8)"
mutant M34 $F 'then revokeFamily(h, getStringOr(rec, "family"), nowSec) else false,' 'then false else false,' \
              suite revoke "TestRevokeEndpointKillsFamily" "revocation does not kill the family"
mutant M35 $F 'Ok(rec) => if getStringOr(rec, "client_id") == auth.clientId then revokeFamily' 'Ok(rec) => if true then revokeFamily' \
              suite revoke "TestRevokeAlways200" "a client can revoke another client's tokens"
# ---- M1d: auth-method intersection (E16, E17)
mutant M36 $D '  match get(doc, "token_endpoint_auth_methods_supported") {' '  match get(doc, "token_endpoint_auth_method") {' \
              test - "cimd accepts chatgpt live doc" "singular token_endpoint_auth_method treated as binding"
mutant M37 $D 'Some(ms) => cimdAuthMethodsOk(ms, true) }' 'Some(ms) => true }' \
              test - "cimd refuses plural without none" "plural without none accepted"
# ---- M1e: metadata
mutant M38 $K '  ] ++ (if cfg.dcr then [kv("registration_endpoint"' '  ] ++ (if true then [kv("registration_endpoint"' \
              test - "metadata golden: asMetadata is byte-identical to 0.1.2" "registration_endpoint always advertised"

# ---- the one host parser (core.httpsHost) and the CIMD/DCR URL gates
mutant M39 $K '    && startsWith(h, ".") == false && endsWith(h, ".") == false && strContains(h, "..") == false' '    && startsWith(h, ".") == false && strContains(h, "..") == false' \
              test - "host refuses a trailing dot" "trailing-dot host accepted by the parser"
mutant M40 $K $'    && endsWith(host, ".") == false && isInternalHost(host) == false)' $'    && isInternalHost(host) == false)' \
              verify core.ail cimdUrlGate "CIMD gate accepts a trailing-dot host"
mutant M41 $K '    let host = toLower(if colon < 0 then authority else substring(authority, 0, colon));' '    let host = (if colon < 0 then authority else substring(authority, 0, colon));' \
              test - "host is lowercased" "host not lowercased (LOCALHOST passes the internal check)"
mutant M42 $K '  match last(split(host, ".")) { Some(l) => digitsOnly(l), None => false }' '  false' \
              test - "host refuses numeric addresses" "numeric (IP) hosts accepted"
mutant M43 $K '  h != "" && not any(\c. find("abcdefghijklmnopqrstuvwxyz0123456789.-", c) < 0, chars(h))' '  h != ""' \
              test - "host refuses percent-encoding" "host charset not checked (%, [, @, space)"
mutant M44 $K $'    && strContains(url, "@") == false && strContains(url, "#") == false && strContains(url, "\\\\") == false\n    && endsWith' $'    && strContains(url, "@") == false && strContains(url, "#") == false\n    && endsWith' \
              verify core.ail cimdUrlGate "CIMD gate accepts a backslash"
mutant M45 $K '    let portOk = colon < 0 || digitsOnly(substring(authority, colon + 1, length(authority)));' '    let portOk = true;' \
              test - "host port must be digits" "non-numeric port accepted"
mutant M46 $K '  cimdUrlGate(url, host, strContains(host, ".") && ipLike(host) == false)' '  cimdUrlGate(url, host, ipLike(host) == false)' \
              test - "host refuses single labels and empty labels" "single-label (intranet) CIMD host accepted"
mutant M47 $C '  length(uri) <= 512 && strContains(uri, "#") == false && strContains(uri, "\\") == false' '  length(uri) <= 512 && strContains(uri, "#") == false' \
              verify clients.ail dcrRedirectOk "DCR gate accepts a backslash"

echo "mutants: $killed/$total killed"
[ $killed -eq $total ] && [ $rc -eq 0 ] && echo "ok: every mutant killed"
exit $rc
