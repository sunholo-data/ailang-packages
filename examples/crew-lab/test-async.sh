#!/usr/bin/env bash
# Acceptance harness only: background crew words in the installed live watch,
# with a slow provider-free fixture worker standing in for crew-reply-worker.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
EX="$ROOT/examples/crew-lab"
AILANG=$(command -v "${AILANG:-ailang}")
TMP=$(mktemp -d "${TMPDIR:-/tmp}/crew-async.XXXXXX")
WORKERS="$(basename "$TMP")/.*/replies/job-"
cleanup() { exec 3>&- 2>/dev/null || true; pkill -f "$WORKERS" 2>/dev/null || true; rm -rf "$TMP"; }
trap cleanup EXIT
"$AILANG" install --path "$EX" --bin-dir "$TMP/bin" >/dev/null
mkdir -p "$TMP/fake"
cat > "$TMP/fake/crew-reply-worker" <<SHIM
#!/bin/sh
# $TMP/fake: provider-free stand-in
exec "$AILANG" run --quiet --package-dir "$EX" --caps FS,Env,Clock --entry main "$EX/reply_fixture.ail" -- "\$@"
SHIM
chmod +x "$TMP/fake/crew-reply-worker"
BASE=/usr/bin:/bin
printf '1\n' | "$TMP/bin/crew-watch-offline" --mode plain --legacy --home "$TMP/boot" --seed 42 >/dev/null
jq '.rules |= map(.base=(if .label=="accept" or .label=="request_relief" then 1000 else 0 end)|.influences=[])' "$TMP/boot/response-policy-watch-v2.json" > "$TMP/accept.json"
prepare() { mkdir -p "$TMP/$1"; jq ".callLimit=${2:-8}" "$TMP/accept.json" > "$TMP/$1/response-policy-watch-v2.json"; }
waitfor() { # waitfor FILE REGEX [SECONDS]
  local n=0; until grep -Eq "$2" "$1" 2>/dev/null; do n=$((n+1)); if [ $n -gt $(( ${3:-30} * 10 )) ]; then echo "timed out waiting for /$2/ in $1" >&2; tail -30 "$1" >&2; exit 1; fi; sleep 0.1; done; }
# Workers carry this run's unique folder name and a job path in their arguments.
WORKERS="$(basename "$TMP")/.*/replies/job-"
workers() { pgrep -f "$WORKERS" | wc -l | tr -d ' '; }
# open NAME [env...]: start the live watch reading commands from a FIFO on fd 3.
# AHEAD is the --prefetch setting (0 isolates replies from prefetch).
AHEAD=0
open_watch() { local name=$1; shift; mkfifo "$TMP/$name.in"; env "$@" "$TMP/bin/crew-watch" --mode plain --legacy --prefetch "$AHEAD" --home "$TMP/$name" --seed 42 < "$TMP/$name.in" > "$TMP/$name.out" 2> "$TMP/$name.err" & PID=$!; exec 3> "$TMP/$name.in"; }
close_watch() { exec 3>&-; wait "$PID"; }
send() { printf '%s\n' "$@" >&3; }

# 1. The decision shows at once; Crew is readable while the words are prepared;
#    the words arrive, are journalled as transport only, and r reads them.
prepare live
open_watch live PATH="$TMP/fake:$BASE" CREW_FIXTURE_DELAY_MS=2000
send 1 1 1
waitfor "$TMP/live.out" 'Replies: 1 preparing, 0 new'
grep -q 'own words are queued' "$TMP/live.out"
[ "$(workers)" -ge 1 ] || { echo "no background worker while playing" >&2; exit 1; }
send c
waitfor "$TMP/live.out" 'VOYAGE / CREW'
until ls "$TMP"/live/runs/*/replies/job-1.json.result >/dev/null 2>&1; do sleep 0.1; done
send ""
waitfor "$TMP/live.out" 'Replies: 0 preparing, 1 new'
send r
waitfor "$TMP/live.out" '\(fixture words, accept\)'
send q
close_watch
[ "$(workers)" = 0 ] || { echo "worker left after quit" >&2; exit 1; }
live=("$TMP"/live/runs/*/journal.jsonl)
jq -s -e '[.[].payload|select(.kind=="wording")]|length==1 and .[0].usage.calls==1 and (.[0].text|startswith("(fixture words"))' "${live[0]}" >/dev/null

# 2. Same seed and inputs with the words already saved: identical domain records
#    (commands, traces, seeds), the words show at once and no job is created.
cp -R "$TMP/live" "$TMP/cached"; rm -rf "$TMP/cached/runs"
printf '1\n1\n1\nq\n' | PATH="$TMP/fake:$BASE" "$TMP/bin/crew-watch" --mode plain --legacy --prefetch 0 --home "$TMP/cached" --seed 42 > "$TMP/cached.out"
cached=("$TMP"/cached/runs/*/journal.jsonl)
dom() { jq -sc '[.[].payload|select(.kind=="host")|{host_input,host_output,seed_before,seed_after}]' "$1"; }
[ "$(dom "${live[0]}")" = "$(dom "${cached[0]}")" ] || { echo "domain records differ between background and saved words" >&2; exit 1; }
grep -q 'scientist: (fixture words, accept)' "$TMP/cached.out"
if ls "$TMP"/cached/runs/*/replies >/dev/null 2>&1; then echo "saved words still created a job" >&2; exit 1; fi

# 3. Quit while a worker is still running: it is stopped, nothing is left behind.
prepare quit
open_watch quit PATH="$TMP/fake:$BASE" CREW_FIXTURE_DELAY_MS=30000
send 1 1 1
waitfor "$TMP/quit.out" 'Replies: 1 preparing'
[ "$(workers)" -ge 1 ] || { echo "no worker to stop" >&2; exit 1; }
send q
close_watch
grep -q 'Stopped 1 background reply' "$TMP/quit.out"
sleep 0.5
[ "$(workers)" = 0 ] || { echo "worker survived quit" >&2; pgrep -fl "$WORKERS" >&2; exit 1; }
quitj=("$TMP"/quit/runs/*/journal.jsonl)
jq -s -e '[.[].payload|select(.kind=="wording")]|length==0' "${quitj[0]}" >/dev/null

# 4. No worker installed: the authored line stands and Replies says why.
prepare missing
printf '1\n1\n1\nr\nq\n' | PATH="$BASE" "$TMP/bin/crew-watch" --mode plain --legacy --prefetch 0 --home "$TMP/missing" --seed 42 > "$TMP/missing.out"
grep -q 'words not fetched (crew-reply-worker is not' "$TMP/missing.out"

# 5. Allowance: one attempt. A zero-call result is refunded, so a second job runs;
#    a one-call result is not, so the next job is withdrawn.
prepare refund 1
open_watch refund PATH="$TMP/fake:$BASE" CREW_FIXTURE_DELAY_MS=200 CREW_FIXTURE_CALLS=0
send 1 1 1
until ls "$TMP"/refund/runs/*/replies/job-1.json.result >/dev/null 2>&1; do sleep 0.1; done
send "" 0 1 2
until ls "$TMP"/refund/runs/*/replies/job-2.json >/dev/null 2>&1; do sleep 0.1; done
send q
close_watch
refundj=("$TMP"/refund/runs/*/journal.jsonl)
jq -s -e '[.[].payload|select(.kind=="wording")]|.[0].usage.calls==0' "${refundj[0]}" >/dev/null
prepare spent 1
open_watch spent PATH="$TMP/fake:$BASE" CREW_FIXTURE_DELAY_MS=200
send 1 1 1
until ls "$TMP"/spent/runs/*/replies/job-1.json.result >/dev/null 2>&1; do sleep 0.1; done
send "" 0 1 2 r
waitfor "$TMP/spent.out" 'no AI attempts remain'
send q
close_watch
if ls "$TMP"/spent/runs/*/replies/job-2.json >/dev/null 2>&1; then echo "job dispatched without an attempt" >&2; exit 1; fi
grep -q 'engineer agree' "$TMP/spent.out" || grep -q 'engineer agreed' "$TMP/spent.out"
# 6. Prefetch: on the bridge the scientist's words for an offer of their work are
#    fetched in the background (invisibly); the offer then shows them at once.
AHEAD=1
prepare ahead
open_watch ahead PATH="$TMP/fake:$BASE" CREW_FIXTURE_DELAY_MS=200
send 1
until ls "$TMP"/ahead/runs/*/replies/job-1.json.result >/dev/null 2>&1; do sleep 0.1; done
send "" 1 1
waitfor "$TMP/ahead.out" 'scientist: \(fixture words, accept\)'
send q
close_watch
if ls "$TMP"/ahead/runs/*/replies/job-2.json >/dev/null 2>&1; then echo "prefetched offer still created a job" >&2; exit 1; fi
if grep -q 'Replies: 1 preparing' "$TMP/ahead.out"; then echo "prefetch shown as a reply" >&2; exit 1; fi
aheadj=("$TMP"/ahead/runs/*/journal.jsonl)
jq -s -e '([.[].payload|select(.kind=="wording")]|length==1) and any(.[].payload;.metadata.usage.source=="cache")' "${aheadj[0]}" >/dev/null
[ "$(dom "${aheadj[0]}")" = "$(dom "${live[0]}")" ] || { echo "prefetch changed domain records" >&2; exit 1; }

# 7. Offer while that prefetch is still running: the job becomes the reply.
prepare adopt
open_watch adopt PATH="$TMP/fake:$BASE" CREW_FIXTURE_DELAY_MS=2500
send 1
until ls "$TMP"/adopt/runs/*/replies/job-1.json >/dev/null 2>&1; do sleep 0.1; done
send 1 1
waitfor "$TMP/adopt.out" 'Replies: 1 preparing, 0 new'
until ls "$TMP"/adopt/runs/*/replies/job-1.json.result >/dev/null 2>&1; do sleep 0.1; done
send "" r
waitfor "$TMP/adopt.out" '\(fixture words, accept\)'
send q
close_watch
if ls "$TMP"/adopt/runs/*/replies/job-2.json >/dev/null 2>&1; then echo "adopted prefetch fetched twice" >&2; exit 1; fi
[ "$(workers)" = 0 ] || { echo "worker left after quit" >&2; exit 1; }

# 8. The real crew-reply-worker module under the AI stub (no provider): the
#    stub's text is not dialogue JSON, so the words are rejected and reported.
mkdir -p "$TMP/stubbed"
cat > "$TMP/stubbed/crew-reply-worker" <<SHIM
#!/bin/sh
exec "$AILANG" run --quiet --package-dir "$EX" --caps FS,Env,AI --ai-stub --entry main "$EX/reply_worker.ail" -- "\$@"
SHIM
chmod +x "$TMP/stubbed/crew-reply-worker"
AHEAD=0
prepare stub
open_watch stub PATH="$TMP/stubbed:$BASE"
send 1 1 1
until ls "$TMP"/stub/runs/*/replies/job-1.json.result >/dev/null 2>&1; do sleep 0.1; done
send "" r
waitfor "$TMP/stub.out" 'personal words unavailable \(AI output'
send q
close_watch
stubj=("$TMP"/stub/runs/*/journal.jsonl)
jq -s -e '[.[].payload|select(.kind=="wording")]|length==1 and .[0].usage.calls==1 and (.[0].error|startswith("AI output rejected"))' "${stubj[0]}" >/dev/null

# 9. Native mode on a real PTY: the arrival is drawn while no key is pressed.
prepare pty
python3 "$EX/test-async-pty.py" "$TMP/bin" "$TMP/fake" "$TMP/pty" >/dev/null

printf 'crew-watch background words: immediate decision, readable while preparing, transport-only journal, identical domain records, quit stops workers, missing worker and allowance handled; prefetch shows words at once and an early offer adopts it; real worker reports rejected words; native PTY draws arrivals while idle\n'
