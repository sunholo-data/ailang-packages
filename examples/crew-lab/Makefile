ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/../..)
EX := $(ROOT)/examples/crew-lab
AILANG ?= ailang
INPUT ?= $(EX)/recordings/agreed-science.ndjson
ENGINE ?= interpreter
OUT := $(ROOT)/.ailang/state/crew-lab
.PHONY: experiment deps tests library-tests store-test play-test scenarios parity replay cli-test quality validate fixtures
experiment:
	@mkdir -p "$(OUT)"
	@AILANG="$(AILANG)" "$(EX)/run.sh" "$(ENGINE)" "$(INPUT)" > "$(OUT)/latest.ndjson"
	@jq -s 'last.state | {tick,actors,resources,relationships,conditions}' "$(OUT)/latest.ndjson"
	@printf 'Full causal trace: %s\n' "$(OUT)/latest.ndjson"
deps:
	@cd "$(EX)" && "$(AILANG)" lock
fixtures:
	@"$(EX)/generate-recordings.sh"
tests:
	@"$(AILANG)" check --package "$(EX)"
	@cd "$(EX)" && "$(AILANG)" test --package .
	@cd "$(EX)" && "$(AILANG)" test --package . --bytecode --strict-bytecode
	@cd "$(EX)" && "$(AILANG)" test scenario.ail
	@cd "$(EX)" && "$(AILANG)" test --allow-skips watch_scenario.ail
	@cd "$(EX)" && "$(AILANG)" test --allow-skips narrative.ail
	@cd "$(EX)" && "$(AILANG)" test --allow-skips watch_presenter.ail
	@cd "$(EX)" && "$(AILANG)" test --allow-skips session.ail
	@cd "$(EX)" && "$(AILANG)" test --allow-skips reactions.ail
	@cd "$(EX)" && "$(AILANG)" test --allow-skips play_flow.ail
	@cd "$(EX)" && "$(AILANG)" test --allow-skips presenter.ail
	@cd "$(EX)" && "$(AILANG)" test --allow-skips journey_flow.ail
	@cd "$(EX)" && "$(AILANG)" test --allow-skips journey_presenter.ail

scenarios:
	@mkdir -p "$(OUT)"
	@for recording in "$(EX)"/recordings/*.ndjson; do name=$$(basename "$$recording" .ndjson); AILANG="$(AILANG)" "$(EX)/run.sh" interpreter "$$recording" > "$(OUT)/$$name.ndjson" || exit; done
	@printf 'Five saved crew scenarios executed\n'
parity:
	@mkdir -p "$(OUT)"
	@for recording in "$(EX)"/recordings/*.ndjson; do name=$$(basename "$$recording" .ndjson); for engine in interpreter vm; do AILANG="$(AILANG)" "$(EX)/run.sh" "$$engine" "$$recording" > "$(OUT)/$$name-$$engine.ndjson" || exit; done; cmp "$(OUT)/$$name-interpreter.ndjson" "$(OUT)/$$name-vm.ndjson" || exit; done
	@printf 'Five evaluator/strict-VM traces identical\n'
replay:
	@mkdir -p "$(OUT)"
	@for recording in "$(EX)"/recordings/*.ndjson; do name=$$(basename "$$recording" .ndjson); for pass in 1 2; do AILANG="$(AILANG)" "$(EX)/run.sh" interpreter "$$recording" > "$(OUT)/$$name-replay$$pass.ndjson" || exit; done; cmp "$(OUT)/$$name-replay1.ndjson" "$(OUT)/$$name-replay2.ndjson" || exit; done
	@printf 'Five saved recordings replay identically\n'
cli-test: scenarios
	@AILANG="$(AILANG)" "$(EX)/test-cli.sh"
library-tests:
	@"$(AILANG)" check --package "$(ROOT)/packages/content-library"
	@cd "$(ROOT)/packages/content-library" && "$(AILANG)" test --package .
	@cd "$(ROOT)/packages/content-library" && "$(AILANG)" test --package . --bytecode --strict-bytecode
	@cd "$(ROOT)/packages/content-library" && "$(AILANG)" test --allow-skips library.ail
	@cd "$(ROOT)/packages/content-library" && "$(AILANG)" pkg quality --strict .
store-test:
	@AILANG="$(AILANG)" "$(EX)/test-store.sh"
play-test:
	@AILANG="$(AILANG)" "$(EX)/test-play.sh"
quality:
	@cd "$(EX)" && "$(AILANG)" pkg quality --strict .
validate: deps library-tests tests scenarios replay parity cli-test store-test play-test quality
.PHONY: mutations
mutations:
	@AILANG="$(AILANG)" python3 "$(EX)/test-mutations.py"
.PHONY: view
view:
	@"$(AILANG)" run --package-dir "$(EX)" --caps IO --entry main "$(EX)/viewer.ail" < "$(INPUT)"
.PHONY: terminal-tests journey-test
terminal-tests:
	@"$(AILANG)" check --package "$(ROOT)/packages/terminal-ui"
	@cd "$(ROOT)/packages/terminal-ui" && "$(AILANG)" test --package .
	@cd "$(ROOT)/packages/terminal-ui" && "$(AILANG)" test --package . --bytecode --strict-bytecode
	@cd "$(ROOT)/packages/terminal-ui" && "$(AILANG)" test --allow-skips ui.ail
	@cd "$(ROOT)/packages/terminal-ui" && "$(AILANG)" test --allow-skips demo.ail
	@cd "$(ROOT)/packages/terminal-ui" && "$(AILANG)" pkg quality --strict .
journey-test:
	@AILANG="$(AILANG)" "$(EX)/test-journey.sh"
validate: terminal-tests journey-test

.PHONY: watch-test
watch-test:
	@AILANG="$(AILANG)" "$(EX)/test-watch.sh"
validate: watch-test

.PHONY: native-ui-test
native-ui-test:
	@cd "$(EX)" && "$(AILANG)" test native_watch_ui_test.ail native_watch_presenter_test.ail
	@cd "$(EX)" && "$(AILANG)" test native_watch_ui_test.ail native_watch_presenter_test.ail --bytecode --strict-bytecode
	@cd "$(EX)" && "$(AILANG)" test --allow-skips native_watch_ui.ail
	@cd "$(EX)" && "$(AILANG)" test --allow-skips native_watch_presenter.ail
	@cd "$(EX)" && "$(AILANG)" test --allow-skips native_watch_args.ail
validate: native-ui-test

.PHONY: native-watch-test
native-watch-test:
	@AILANG="$(AILANG)" "$(EX)/test-native-watch.sh"
validate: native-watch-test

.PHONY: native-watch-pty-test
native-watch-pty-test:
	@AILANG="$(AILANG)" python3 "$(EX)/test-native-watch-pty.py"
validate: native-watch-pty-test
