ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/../..)
EX := $(ROOT)/examples/crew-lab
AILANG ?= ailang
INPUT ?= $(EX)/recordings/agreed-science.ndjson
ENGINE ?= interpreter
OUT := $(ROOT)/.ailang/state/crew-lab
.PHONY: experiment deps tests scenarios parity replay cli-test quality validate fixtures
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
quality:
	@cd "$(EX)" && "$(AILANG)" pkg quality --strict .
validate: deps tests scenarios replay parity cli-test quality
.PHONY: mutations
mutations:
	@AILANG="$(AILANG)" python3 "$(EX)/test-mutations.py"
