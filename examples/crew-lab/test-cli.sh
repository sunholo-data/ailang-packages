#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
AILANG=${AILANG:-ailang}
TMP=$(mktemp -d "${TMPDIR:-/tmp}/crew-cli.XXXXXX")
trap 'rm -rf "$TMP"' EXIT
"$AILANG" install --path "$ROOT/examples/crew-lab" --bin-dir "$TMP/bin"
cd "$TMP"
for recording in "$ROOT"/examples/crew-lab/recordings/*.ndjson; do
 name=$(basename "$recording" .ndjson)
 "$TMP/bin/crew-lab" < "$recording" > "$TMP/$name.ndjson"
 cmp "$TMP/$name.ndjson" "$ROOT/.ailang/state/crew-lab/$name.ndjson"
 "$TMP/bin/crew-view" < "$recording" > "$TMP/$name.txt"
 rg -q 'scientist: fatigue' "$TMP/$name.txt"
 rg -q 'engineer: fatigue' "$TMP/$name.txt"
 rg -q 'Latest crew response' "$TMP/$name.txt"
done
# Material and personal consequences must match the experiment, not just replay.
check() {
 local name=$1 fatigue=$2 trust=$3 available=$4 consumed=$5
 jq -s -e --argjson fatigue "$fatigue" --argjson trust "$trust" --argjson available "$available" --argjson consumed "$consumed" '
 last.state |
 ([.actors[] | select(.id=="scientist") | .indicators[] | select(.id=="fatigue") | .value] == [$fatigue]) and
 ([.relationships[] | select(.from=="scientist" and .to=="captain" and .dimension=="trust") | .value] == [$trust]) and
 ([.resources[] | select(.id=="materials") | {available,reserved,consumed}] == [{available:$available,reserved:0,consumed:$consumed}]) and
 all(.resources[]; .available+.reserved+.consumed == .initial+.transferred_in-.transferred_out)
 ' "$TMP/$name.ndjson" >/dev/null
}
check agreed-science 70 52 2 4
check refused-order 70 42 2 4
check granted-relief 30 58 6 0
check denied-relief 70 48 2 4
check competing-projects 70 52 0 6
jq -s -e '
 def trust: [.state.relationships[] | select(.from=="engineer" and .to=="captain" and .dimension=="trust") | .value][0];
 .[4] | trust == 50
 ' "$TMP/refused-order.ndjson" >/dev/null
jq -s -e 'last.state.relationships | any(.[]; .from=="engineer" and .to=="captain" and .value==42)' "$TMP/refused-order.ndjson" >/dev/null
set +e
printf '%s\n' '{"invalid":true}' | "$TMP/bin/crew-lab" > "$TMP/invalid.ndjson"
rc=$?
set -e
test "$rc" = 1
set +e
printf '%s\n' '{"invalid":true}' | "$TMP/bin/crew-view" > "$TMP/invalid.txt"
view_rc=$?
set -e
test "$view_rc" = 1
rg -q '^ERROR:' "$TMP/invalid.txt"
jq -e 'has("error")' "$TMP/invalid.ndjson" >/dev/null
# Friendly terminal aliases retain the same received consequences.
"$TMP/bin/crew-view" < "$ROOT/examples/crew-lab/recordings-care.txt" > "$TMP/friendly-care.txt"
rg -q 'scientist: fatigue \[###-------\] 30' "$TMP/friendly-care.txt"
rg -q 'trust -> captain \[#####-----\] 58' "$TMP/friendly-care.txt"
rg -q 'materials: available 6, reserved 0, used 0' "$TMP/friendly-care.txt"
"$TMP/bin/crew-view" < "$ROOT/examples/crew-lab/recordings-order.txt" > "$TMP/friendly-order.txt"
rg -q 'scientist: fatigue \[#######---\] 70' "$TMP/friendly-order.txt"
rg -q 'trust -> captain \[####------\] 42' "$TMP/friendly-order.txt"
cat > "$TMP/recover.txt" <<'RECOVER'
start consent
offer science scientist observations
work science
ask r1 scientist science
reply r1 accept
work science
advance 4
quit
RECOVER
"$TMP/bin/crew-view" < "$TMP/recover.txt" > "$TMP/recovered.txt"
rg -q 'ERROR:.*personal consent required' "$TMP/recovered.txt"
rg -q 'scientist: fatigue \[#######---\] 70' "$TMP/recovered.txt"
rg -q 'trust -> captain \[#####-----\] 52' "$TMP/recovered.txt"
# Cancellation is a host action, never a synthetic crew response/roll.
cat > "$TMP/cancel.ndjson" <<'CANCEL'
{"command":"start","policy":"consent"}
{"command":"offer","worker":"scientist","recipe":"observations","id":"science"}
{"command":"ask","actor":"scientist","task":"science","id":"r1"}
{"command":"cancel_request","id":"r1"}
CANCEL
"$TMP/bin/crew-view" < "$TMP/cancel.ndjson" > "$TMP/cancel.txt"
rg -q 'Latest request: scientist/science cancelled' "$TMP/cancel.txt"
if rg -q 'Latest crew response|completed, roll' "$TMP/cancel.txt"; then exit 1; fi
# UI control words cannot bypass the raw line bound through whitespace.
awk 'BEGIN {for(i=0;i<65536;i++) printf " "; print "help"}' > "$TMP/control-oversize.txt"
set +e
"$TMP/bin/crew-view" < "$TMP/control-oversize.txt" > "$TMP/control-error.txt"
control_rc=$?
set -e
test "$control_rc" = 1
rg -q 'ERROR: line limit' "$TMP/control-error.txt"
# Finite saved-file launcher rejects blank, oversize, empty and too-many lines.
printf '\n' > "$TMP/blank.ndjson"
: > "$TMP/empty.ndjson"
awk 'BEGIN {for(i=0;i<65537;i++) printf "x"; printf "\n"}' > "$TMP/oversize.ndjson"
awk 'BEGIN {for(i=0;i<10001;i++) print "{}"}' > "$TMP/too-many.ndjson"
for invalid in blank empty oversize too-many; do
 if AILANG="$AILANG" "$ROOT/examples/crew-lab/run.sh" interpreter "$TMP/$invalid.ndjson" > /dev/null 2>&1; then printf 'Accepted invalid recording: %s\n' "$invalid" >&2; exit 1; fi
done
printf 'Installed crew JSON/readable CLI: five traces identical from unrelated cwd; malformed input exits1; finite framing guards and friendly controls pass\n'
