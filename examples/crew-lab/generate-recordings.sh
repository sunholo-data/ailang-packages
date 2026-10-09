#!/usr/bin/env bash
# Saved synthetic decisions only. Never reads API keys or contacts a provider.
set -euo pipefail
EX=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$EX/recordings"
cmd() { jq -nc "$@"; }
start() { cmd --arg policy "$1" '{command:"start",policy:$policy}'; }
offer() { cmd --arg worker "$1" --arg recipe "$2" --arg id "$3" '{command:"offer",worker:$worker,recipe:$recipe,id:$id}'; }
ask() { cmd --arg actor "$1" --arg task "$2" --arg id "$3" '{command:"ask",actor:$actor,task:$task,id:$id}'; }
answer() {
 local request=$1 choice=$2 phase=$3 roll=$4 body
 body=$(jq -nc --arg choice "$choice" --arg id "synthetic-$request" --arg phase "$phase" '
 {model:"synthetic:jev",id:$id,usage:{input_tokens:0,output_tokens:0,cost:0},answers:{response:{type:"choice",choice:$choice,confidence:0.8,probabilities:
 (if $phase=="working" then {continue:0.05,defer:0.05,request_relief:0.9}
 elif $choice=="decline" then {accept:0.05,concern:0.1,defer:0.05,decline:0.8}
 else {accept:0.8,concern:0.05,defer:0.05,decline:0.1} end)}}}')
 cmd --arg request "$request" --arg body "$body" --argjson roll "$roll" '{command:"answer",request:$request,body:$body,roll:$roll}'
}
start_task() { cmd --arg task "$1" '{command:"start_task",task:$task}'; }
advance() { cmd --argjson tick "$1" '{command:"advance",tick:$tick,budget:64}'; }
resolve() { cmd --arg id "$1" --argjson release "$2" '{command:"resolve_relief",id:$id,release:$release}'; }
agreed() { offer "$1" "$2" "$3"; ask "$1" "$3" "$4"; answer "$4" accept offered 0.1; start_task "$3"; }
{
 start consent; agreed scientist observations science r1; advance 6
} > "$EX/recordings/agreed-science.ndjson"
{
 start orders; offer scientist observations science; ask scientist science r1; answer r1 decline offered 0.9; start_task science
 cmd '{command:"deliver",observer:"engineer",evidence:"science",id:"engineer-offer"}'
 cmd '{command:"deliver",observer:"engineer",evidence:"report-science",id:"engineer-report"}'
 advance 6
} > "$EX/recordings/refused-order.ndjson"
{
 start consent; agreed scientist observations science r1; ask scientist science r2; answer r2 request_relief working 0.5; resolve relief-r2 true
 agreed scientist rest_scientist rest r3; advance 2
} > "$EX/recordings/granted-relief.ndjson"
{
 start consent; agreed scientist observations science r1; ask scientist science r2; answer r2 request_relief working 0.5; resolve relief-r2 false; advance 6
} > "$EX/recordings/denied-relief.ndjson"
{
 start consent; agreed engineer maintenance repairs r1; advance 3
 agreed scientist observations science r2; advance 9
} > "$EX/recordings/competing-projects.ndjson"
