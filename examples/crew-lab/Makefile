ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/../..)
EX := $(ROOT)/examples/crew-lab
CORE := $(ROOT)/packages/crew-core
AILANG ?= ailang
INPUT ?= $(EX)/recordings/agreed-science.ndjson
ENGINE ?= interpreter
OUT := $(ROOT)/.ailang/state/crew-lab
.PHONY: experiment deps fixtures tests core-tests library-tests terminal-tests store-test scenarios parity replay quality validate mutations native-ui-test native-watch-test native-watch-pty-test short-reply-test conversations-test sim-test scenario-test

# One NDJSON host run (crew-host protocol) over a saved recording.
experiment:
	@mkdir -p "$(OUT)"
	@AILANG="$(AILANG)" "$(EX)/run.sh" "$(ENGINE)" "$(INPUT)" > "$(OUT)/latest.ndjson"
	@jq -s 'last.state | {tick,actors,resources,relationships,conditions}' "$(OUT)/latest.ndjson"
	@printf 'Full causal trace: %s\n' "$(OUT)/latest.ndjson"
deps:
	@cd "$(CORE)" && "$(AILANG)" lock >/dev/null
	@cd "$(EX)" && "$(AILANG)" lock >/dev/null
fixtures:
	@"$(EX)/generate-recordings.sh"

# crew_core: the publishable pure host. example.ail must match data/watch-scenario.json.
core-tests:
	@"$(CORE)/tools/gen-example.sh" --check
	@"$(AILANG)" check --package "$(CORE)"
	@cd "$(CORE)" && "$(AILANG)" test --package . --allow-skips
	@cd "$(CORE)" && "$(AILANG)" test --package . --allow-skips --bytecode --strict-bytecode
	@cd "$(CORE)" && "$(AILANG)" test --allow-skips scenario.ail
	@cd "$(CORE)" && "$(AILANG)" test --allow-skips session.ail
	@cd "$(CORE)" && "$(AILANG)" test --allow-skips conversations.ail
	@cd "$(CORE)" && "$(AILANG)" test --allow-skips personality_host.ail
	@cd "$(CORE)" && "$(AILANG)" pkg quality --strict .

tests:
	@"$(AILANG)" check --package "$(EX)"
	@cd "$(EX)" && "$(AILANG)" test --package . --allow-skips
	@cd "$(EX)" && "$(AILANG)" test --package . --allow-skips --bytecode --strict-bytecode
	@cd "$(EX)" && for m in narrative watch_presenter dialogue play_flow presenter journey_flow ship sim_cli; do "$(AILANG)" test --allow-skips $$m.ail || exit; done

library-tests:
	@"$(AILANG)" check --package "$(ROOT)/packages/content-library"
	@cd "$(ROOT)/packages/content-library" && "$(AILANG)" test --package .
	@cd "$(ROOT)/packages/content-library" && "$(AILANG)" test --package . --bytecode --strict-bytecode
	@cd "$(ROOT)/packages/content-library" && "$(AILANG)" test --allow-skips library.ail
	@cd "$(ROOT)/packages/content-library" && "$(AILANG)" pkg quality --strict .
terminal-tests:
	@"$(AILANG)" check --package "$(ROOT)/packages/terminal-ui"
	@cd "$(ROOT)/packages/terminal-ui" && "$(AILANG)" test --package .
	@cd "$(ROOT)/packages/terminal-ui" && "$(AILANG)" test --package . --bytecode --strict-bytecode
	@cd "$(ROOT)/packages/terminal-ui" && "$(AILANG)" test --allow-skips ui.ail
	@cd "$(ROOT)/packages/terminal-ui" && "$(AILANG)" test --allow-skips demo.ail
	@cd "$(ROOT)/packages/terminal-ui" && "$(AILANG)" pkg quality --strict .

# Host protocol recordings: run, replay twice, and compare interpreter with strict VM.
scenarios:
	@mkdir -p "$(OUT)"
	@for recording in "$(EX)"/recordings/*.ndjson; do name=$$(basename "$$recording" .ndjson); AILANG="$(AILANG)" "$(EX)/run.sh" interpreter "$$recording" > "$(OUT)/$$name.ndjson" || exit; done
	@printf 'Saved host recordings executed\n'
parity:
	@mkdir -p "$(OUT)"
	@for recording in "$(EX)"/recordings/*.ndjson; do name=$$(basename "$$recording" .ndjson); for engine in interpreter vm; do AILANG="$(AILANG)" "$(EX)/run.sh" "$$engine" "$$recording" > "$(OUT)/$$name-$$engine.ndjson" || exit; done; cmp "$(OUT)/$$name-interpreter.ndjson" "$(OUT)/$$name-vm.ndjson" || exit; done
	@printf 'Interpreter and strict-VM host traces identical\n'
replay:
	@mkdir -p "$(OUT)"
	@for recording in "$(EX)"/recordings/*.ndjson; do name=$$(basename "$$recording" .ndjson); for pass in 1 2; do AILANG="$(AILANG)" "$(EX)/run.sh" interpreter "$$recording" > "$(OUT)/$$name-replay$$pass.ndjson" || exit; done; cmp "$(OUT)/$$name-replay1.ndjson" "$(OUT)/$$name-replay2.ndjson" || exit; done
	@printf 'Saved host recordings replay identically\n'

store-test:
	@AILANG="$(AILANG)" "$(EX)/test-store.sh"
quality:
	@cd "$(EX)" && "$(AILANG)" pkg quality --strict .
mutations:
	@AILANG="$(AILANG)" python3 "$(EX)/test-mutations.py"

native-ui-test:
	@cd "$(EX)" && "$(AILANG)" test native_watch_ui_test.ail native_watch_presenter_test.ail
	@cd "$(EX)" && "$(AILANG)" test native_watch_ui_test.ail native_watch_presenter_test.ail --bytecode --strict-bytecode
	@cd "$(EX)" && "$(AILANG)" test --allow-skips native_watch_ui.ail
	@cd "$(EX)" && "$(AILANG)" test --allow-skips native_watch_presenter.ail
	@cd "$(EX)" && "$(AILANG)" test --allow-skips native_watch_args.ail
native-watch-test:
	@AILANG="$(AILANG)" "$(EX)/test-native-watch.sh"
native-watch-pty-test:
	@AILANG="$(AILANG)" python3 "$(EX)/test-native-watch-pty.py"
short-reply-test:
	@AILANG="$(AILANG)" bash "$(EX)/test-short-reply.sh"
scenario-test:
	@AILANG="$(AILANG)" "$(EX)/test-scenario-errors.sh"
sim-test:
	@AILANG="$(AILANG)" "$(EX)/test-sim.sh"
conversations-test:
	@cd "$(ROOT)/packages/terminal-ui" && "$(AILANG)" test --allow-skips text_field.ail
	@cd "$(ROOT)/packages/social-dynamics" && "$(AILANG)" test --allow-skips personality.ail
	@AILANG="$(AILANG)" python3 "$(EX)/test-conversations.py"
	@AILANG="$(AILANG)" "$(EX)/test-conversation-replay.sh"
# Background crew words: the pure inbox and file protocol on both engines, then
# the installed live watch with provider-free fixture and stubbed workers.
reply-test:
	@cd "$(EX)" && for m in reply_jobs reply_codec; do "$(AILANG)" test --allow-skips $$m.ail || exit; "$(AILANG)" test --allow-skips --bytecode --strict-bytecode $$m.ail || exit; done
async-test:
	@AILANG="$(AILANG)" "$(EX)/test-async.sh"
# Verification loop: claims over crew-sim runs, and long sessions.
claims-test:
	@cd "$(EX)" && "$(AILANG)" test --allow-skips claims.ail
	@cd "$(EX)" && "$(AILANG)" test --allow-skips --bytecode --strict-bytecode claims.ail
	@AILANG="$(AILANG)" "$(EX)/test-claims.sh"
sample-test:
	@AILANG="$(AILANG)" "$(EX)/test-sample.sh"
# Draft Stapledon scenario pack: every scenario and claims file loads and runs clean.
scenario-pack-test:
	@cd "$(EX)" && for f in scenarios/stapledon/*.claims.json; do s=$${f%.claims.json}.json; "$(AILANG)" run --quiet --bytecode --package-dir . --caps IO,FS,Env --fs-max-bytes 64MB sim_cli.ail -- --scenario "$$s" --seeds 1..3 --turns 12 | jq -s -e 'length==3 and all(.[]; .errors==0)' >/dev/null || { echo "scenario failed: $$s" >&2; exit 1; }; "$(AILANG)" run --quiet --bytecode --package-dir . --caps IO,FS,Env --fs-max-bytes 64MB sim_cli.ail -- --check "$$f" --scenario "$$s" --seeds 1 | grep -q 'claims hold' || { echo "claims did not run: $$f" >&2; exit 1; }; done; printf '1\n1\n1\n2\nq\n' | "$(AILANG)" run --quiet --package-dir . --entry offline --caps IO,FS,Env,AI,Process,Clock --ai-stub --fs-max-bytes 16MB native_watch.ail -- --mode plain --scenario scenarios/stapledon/ergosphere-question.json --home "$$(mktemp -d)" --seed 42 > "$${TMPDIR:-/tmp}/crew-pack-watch.out" && grep -q 'navigator: Model the tidal margins' "$${TMPDIR:-/tmp}/crew-pack-watch.out" && grep -q 'Calculate how close the ship can pass' "$${TMPDIR:-/tmp}/crew-pack-watch.out" || { echo "watch did not play a non-default crew" >&2; exit 1; }; printf 'Stapledon scenario pack: all scenarios run clean and all claims files load; the watch plays a non-default crew\n'

validate: deps core-tests library-tests terminal-tests tests scenarios replay parity store-test quality native-ui-test native-watch-test native-watch-pty-test short-reply-test conversations-test sim-test scenario-test reply-test async-test claims-test sample-test scenario-pack-test
