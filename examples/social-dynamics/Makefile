ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/../..)
EX := $(ROOT)/examples/social-dynamics
PKG := $(ROOT)/packages/social-dynamics
AILANG ?= ailang
SCENARIO ?= ship
POLICY ?= care
INPUT ?= $(EX)/recordings/$(SCENARIO)-$(POLICY).ndjson
ENGINE ?= interpreter
OUT := $(ROOT)/.ailang/state/social-experiments
.PHONY: experiment scenarios parity replay validate deps timings
experiment:
	@mkdir -p "$(OUT)"
	@AILANG="$(AILANG)" "$(EX)/run.sh" "$(ENGINE)" "$(INPUT)" > "$(OUT)/latest.ndjson"
	@jq -s 'last.state | {session,tick,actors: [.actors[] | {id,indicators}],resources,conditions,relationships}' "$(OUT)/latest.ndjson"
	@printf 'Full causal trace: %s\n' "$(OUT)/latest.ndjson"
deps:
	@cd "$(PKG)" && "$(AILANG)" lock
	@cd "$(EX)" && "$(AILANG)" lock
scenarios:
	@mkdir -p "$(OUT)"
	@for recording in "$(EX)"/recordings/*.ndjson; do name=$$(basename "$$recording" .ndjson); AILANG="$(AILANG)" "$(EX)/run.sh" interpreter "$$recording" > "$(OUT)/$$name.ndjson" || exit; done
	@jq -s 'last.state | .actors[] | select(.id=="scientist" or .id=="resident") | {id,indicators}' "$(OUT)/ship-care.ndjson" "$(OUT)/ship-collaboration.ndjson" "$(OUT)/ship-renegotiate.ndjson" "$(OUT)/community-repair.ndjson" "$(OUT)/community-festival.ndjson"	
	@"$(EX)/assert-scenarios.sh" "$(OUT)"
parity:
	@mkdir -p "$(OUT)"
	@for recording in "$(EX)"/recordings/*.ndjson; do name=$$(basename "$$recording" .ndjson); for engine in interpreter vm; do AILANG="$(AILANG)" "$(EX)/run.sh" "$$engine" "$$recording" > "$(OUT)/$$name-$$engine.ndjson" || exit; done; cmp "$(OUT)/$$name-interpreter.ndjson" "$(OUT)/$$name-vm.ndjson" || exit; done
	@printf 'Five interpreter/strict-VM traces identical\n'
replay:
	@mkdir -p "$(OUT)"
	@for recording in "$(EX)"/recordings/*.ndjson; do name=$$(basename "$$recording" .ndjson); for pass in 1 2; do AILANG="$(AILANG)" "$(EX)/run.sh" interpreter "$$recording" > "$(OUT)/$$name-replay$$pass.ndjson" || exit; done; cmp "$(OUT)/$$name-replay1.ndjson" "$(OUT)/$$name-replay2.ndjson" || exit; done
	@printf 'Five recordings replay identically; IO capability only\n'
validate: deps
	@"$(AILANG)" check --package "$(PKG)"
	@cd "$(PKG)" && "$(AILANG)" test --package .
	@cd "$(PKG)" && "$(AILANG)" test --allow-skips model.ail
	@cd "$(PKG)" && "$(AILANG)" test _smoke.ail
	@"$(AILANG)" run --package-dir "$(PKG)" --caps IO --entry main "$(PKG)/_smoke.ail"
	@"$(AILANG)" check --package "$(EX)"
	@cd "$(EX)" && "$(AILANG)" test --package .
	@cd "$(EX)" && "$(AILANG)" test --allow-skips config.ail
	@$(MAKE) -f "$(EX)/Makefile" scenarios parity replay AILANG="$(AILANG)"
	@cd "$(PKG)" && "$(AILANG)" pkg quality --strict .
	@cd "$(PKG)" && "$(AILANG)" publish --dry-run
