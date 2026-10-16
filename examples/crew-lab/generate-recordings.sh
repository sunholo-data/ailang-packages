#!/usr/bin/env bash
# Saved synthetic decisions only. Never reads API keys or contacts a provider.
set -euo pipefail
EX=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$EX/recordings"
cmd() { jq -nc "$@"; }
start() { cmd --arg policy "$1" '{command:"start",policy:$policy,scenario:"watch-v2"}'; }
offer() { cmd --arg worker "$1" --arg recipe "$2" --arg id "$3" '{command:"offer",worker:$worker,recipe:$recipe,id:$id}'; }
ask() { cmd --arg actor "$1" --arg task "$2" --arg id "$3" '{command:"ask",actor:$actor,task:$task,id:$id}'; }
answer() {
 local request=$1 choice=$2 phase=$3 roll=$4 body
 body=$(jq -nc --arg choice "$choice" --arg id "synthetic-$request" --arg phase "$phase" '
 {model:"synthetic:jev",id:$id,usage:{input_tokens:0,output_tokens:0,cost:0},answers:{response:{type:"choice",choice:$choice,confidence:0.8,probabilities:
 (if $phase=="working" then {continue:0.05,defer:0.05,request_relief:0.9}
 elif $phase=="duty" then (if $choice=="stand_down" then {carry_on:0.05,defer:0.05,stand_down:0.9} else {carry_on:0.9,defer:0.05,stand_down:0.05} end)
 elif $choice=="decline" then {accept:0.05,concern:0.1,defer:0.05,decline:0.8}
 else {accept:0.8,concern:0.05,defer:0.05,decline:0.1} end)}}}')
 cmd --arg request "$request" --arg body "$body" --argjson roll "$roll" '{command:"answer",request:$request,body:$body,roll:$roll}'
}
start_task() { cmd --arg task "$1" '{command:"start_task",task:$task}'; }
advance() { cmd --argjson tick "$1" '{command:"advance",tick:$tick,budget:64}'; }
resolve() { cmd --arg id "$1" --argjson release "$2" '{command:"resolve_relief",id:$id,release:$release}'; }
check_in() { cmd --arg actor "$1" --arg id "$2" '{command:"check_in",actor:$actor,id:$id}'; }
resolve_stand_down() { cmd --arg id "$1" --argjson release "$2" '{command:"resolve_stand_down",id:$id,release:$release}'; }
agreed() { offer "$1" "$2" "$3"; ask "$1" "$3" "$4"; answer "$4" accept offered 0.1; start_task "$3"; }
{
 start consent; agreed scientist work_scientist science r1; advance 6
} > "$EX/recordings/agreed-science.ndjson"
{
 start orders; offer scientist work_scientist science; ask scientist science r1; answer r1 decline offered 0.9; start_task science
 cmd '{command:"deliver",observer:"engineer",evidence:"science",id:"engineer-offer"}'
 cmd '{command:"deliver",observer:"engineer",evidence:"report-science",id:"engineer-report"}'
 advance 6
} > "$EX/recordings/refused-order.ndjson"
{
 start consent; agreed scientist work_scientist science r1; ask scientist science r2; answer r2 request_relief working 0.5; resolve relief-r2 true
 agreed scientist rest_scientist rest r3; advance 2
} > "$EX/recordings/granted-relief.ndjson"
{
 start consent; agreed scientist work_scientist science r1; ask scientist science r2; answer r2 request_relief working 0.5; resolve relief-r2 false; advance 6
} > "$EX/recordings/denied-relief.ndjson"
{
 start consent; agreed engineer work_engineer repairs r1; advance 3
 agreed scientist work_scientist science r2; advance 9
} > "$EX/recordings/competing-projects.ndjson"
# crew_core 0.6.0 duty check-ins: a grant halts running work and starts rest,
# a denial reports and lets the rest offer lapse, carry_on changes nothing.
{
 start orders; offer scientist work_scientist science; start_task science
 check_in scientist d1; answer d1 stand_down duty 0.5; resolve_stand_down d1 true
 check_in engineer d2; answer d2 stand_down duty 0.5; resolve_stand_down d2 false
 check_in medic d3; answer d3 carry_on duty 0.5; advance 3
} > "$EX/recordings/stand-down.ndjson"
