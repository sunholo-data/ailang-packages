# ailang-packages root Makefile
#
# Targets:
#   verify-extensions   — boot-probe each motoko-ext-* package's
#                          register_with_config to catch runtime panics
#                          before publish (e.g. match-against-wrong-ADT,
#                          panicking readFile, cross-package shape drift).
#                          Process-per-package isolation.
#
# Why this exists: the AILANG typechecker doesn't enforce constructor-ADT
# cross-checking on match arms (loose exhaustiveness), so writing
# `match getString(...) { Err(_) => ..., Ok(_) => ... }` against a value
# of type Option[string] passes `ailang check` but crashes at runtime.
# The bug only surfaces when a consumer (motoko_agent) loads the
# extension and the JSON field IS present. Per-package boot probe
# catches this BEFORE the package ships to the registry.

AILANG ?= ailang
PACKAGES_DIR := packages

.PHONY: verify-extensions

verify-extensions:
	@ok=0; fail=0; missing=0; failed=""; \
	for pkg in $(PACKAGES_DIR)/motoko-ext-*; do \
		[ -d "$$pkg" ] || continue; \
		name=$$(basename "$$pkg"); \
		smoke="$$pkg/_smoke.ail"; \
		if [ ! -f "$$smoke" ]; then \
			echo "  ⚠ $$name: no _smoke.ail (TODO: add boot probe)"; \
			missing=$$((missing + 1)); \
			continue; \
		fi; \
		out=$$(cd "$$pkg" && AILANG_RELAX_MODULES=1 \
			$(AILANG) run --caps Net,AI,SharedMem,IO,Env,Clock,FS,Process,Stream \
			  --ai-stub --entry main _smoke.ail 2>&1); \
		rc=$$?; \
		if [ $$rc -eq 0 ] && echo "$$out" | grep -q "^OK:"; then \
			echo "  ✓ $$name"; \
			ok=$$((ok + 1)); \
		else \
			echo "  ✗ $$name"; \
			echo "$$out" | sed -E 's/\x1b\[[0-9;]*[a-zA-Z]//g' | grep -E "Error|panic" | head -3 | sed 's/^/      /'; \
			fail=$$((fail + 1)); \
			failed="$$failed $$name"; \
		fi; \
	done; \
	echo "verify-extensions: $$ok passed, $$fail failed, $$missing missing _smoke.ail"; \
	if [ "$$fail" -ne 0 ]; then \
		echo "FAILED:$$failed"; \
		exit 1; \
	fi
