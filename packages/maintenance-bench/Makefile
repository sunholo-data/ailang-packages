AILANG_BIN ?= ailang
# Native forall properties compile/test but trigger the pinned formatter nil-expression bug.
# Explicit formatting waiver only for these four test modules; both remain compiled/tested.
FMT_FILES = $(filter-out codec_test.ail cohort_test.ail lineage_test.ail metrics_test.ail,$(wildcard *.ail examples/*.ail))
.PHONY: verify test fmt smoke examples integration ledger-integration qualify-taskpacks candidate-grading-test source-consumer scale quality quality-strict package
verify: fmt test smoke examples ledger-examples
	$(AILANG_BIN) lock --check
	$(AILANG_BIN) check --package .
	$(AILANG_BIN) run --caps IO,FS,Env --entry main cli.ail verify-snapshot assets/fixtures/analytical.snapshot.json assets/fixtures/analytical.annotations.json assets/fixtures/analytical.manifest.json assets/fixtures/analytical.expected.json
test:
	$(AILANG_BIN) test --package . --no-color
fmt:
	$(AILANG_BIN) fmt --check $(FMT_FILES)
smoke:
	$(AILANG_BIN) run --caps IO --entry main _smoke.ail
integration:
	AILANG_BIN=$(AILANG_BIN) sh tests/integration.sh
ledger-integration:
	AILANG_BIN=$(AILANG_BIN) sh tests/ledger_integration.sh
candidate-grading-test:
	PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s ../../research/real-world-maintenance/taskpacks/v1 -p candidate_grade_test.py -v
qualify-taskpacks: candidate-grading-test
	AILANG_BIN=$(AILANG_BIN) sh ../../research/real-world-maintenance/taskpacks/v1/qualify.sh
scale:
	@task_tmp=$$(mktemp -d); trap 'rm -rf "$$task_tmp"' EXIT; \
	$(AILANG_BIN) run --caps IO,FS,Env,Clock --entry main benchmark.ail 1000 "$$task_tmp/1000.json" && \
	$(AILANG_BIN) run --caps IO,FS,Env,Clock --entry main benchmark.ail 10000 "$$task_tmp/10000.json"
quality:
	$(AILANG_BIN) pkg quality .
quality-strict:
	$(AILANG_BIN) pkg quality --strict .
package:
	$(AILANG_BIN) publish --dry-run

examples:
	$(AILANG_BIN) run --caps IO --entry main examples/offline_report.ail > /dev/null
	$(AILANG_BIN) run --caps IO --entry main examples/build_cohort.ail
	$(AILANG_BIN) run --caps IO --entry main examples/compare_projects.ail
	@task_tmp=$$(mktemp -d); trap 'rm -rf "$$task_tmp"' EXIT; \
	$(AILANG_BIN) run --caps IO,FS,Env,Clock --entry main examples/scale_bench.ail 24 "$$task_tmp/example.json"

# Ledger examples consume the explicit checked-in instrument/control fixtures.
ledger-examples:
	$(AILANG_BIN) run --caps IO --entry main examples/scoped_index.ail
	$(AILANG_BIN) run --caps IO --entry main examples/usage_accounting.ail
	$(AILANG_BIN) run --caps IO,FS --entry main examples/maintenance_trajectory.ail > /dev/null
	$(AILANG_BIN) run --caps IO,FS --entry main examples/roadmap_card.ail > /dev/null

source-consumer:
	AILANG_BIN=$(AILANG_BIN) sh ../../examples/maintenance-ledger-source/check.sh
