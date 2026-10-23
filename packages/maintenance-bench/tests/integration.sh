#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
AILANG_BIN=${AILANG_BIN:-ailang}
TASK_TMP=$(mktemp -d)
trap 'rm -rf "$TASK_TMP"' EXIT
cd "$ROOT"
# Standard [bin] shims must resolve source from outside the checkout.
"$AILANG_BIN" install --path . --bin-dir "$TASK_TMP/bin"
cd "$TASK_TMP"
"$TASK_TMP/bin/maintenance-bench" verify-snapshot "$ROOT/assets/fixtures/analytical.snapshot.json" "$ROOT/assets/fixtures/analytical.annotations.json" "$ROOT/assets/fixtures/analytical.manifest.json" "$ROOT/assets/fixtures/analytical.expected.json"
"$TASK_TMP/bin/maintenance-bench" analyse "$ROOT/assets/fixtures/analytical.snapshot.json" "$ROOT/assets/fixtures/analytical.annotations.json" "$ROOT/assets/fixtures/analytical.manifest.json" "$TASK_TMP/first.json"
"$TASK_TMP/bin/maintenance-bench" analyse "$ROOT/assets/fixtures/analytical.snapshot.json" "$ROOT/assets/fixtures/analytical.annotations.json" "$ROOT/assets/fixtures/analytical.manifest.json" "$TASK_TMP/second.json"
cmp "$TASK_TMP/first.json" "$TASK_TMP/second.json"
if "$TASK_TMP/bin/maintenance-bench" analyse "$ROOT/assets/fixtures/analytical.snapshot.json" "$ROOT/assets/fixtures/analytical.annotations.json" "$ROOT/assets/fixtures/analytical.manifest.json" "$TASK_TMP/first.json"; then echo 'overwrite unexpectedly succeeded' >&2; exit 1; fi
"$TASK_TMP/bin/maintenance-ledger" runs "$ROOT/assets/fixtures/ledger/plan.json" "$ROOT/assets/fixtures/ledger/runs.json" "$ROOT/assets/fixtures/ledger/empty-usage.json" fixture-runtime "$TASK_TMP/ledger.json"
"$TASK_TMP/bin/maintenance-ledger" cards "$ROOT/assets/fixtures/ledger/cards.json" fixture-runtime "$TASK_TMP/cards.json"
# Network-free gh replay covers pagination, all review endpoints and failed requests.
export PATH="$ROOT/tests/fake-bin:$PATH"
export MB_GH_LOG="$TASK_TMP/gh.log"
"$TASK_TMP/bin/maintenance-collect" github acme/demo ailang 1792713600000 2 2 "$TASK_TMP/gh.json"
printf '%s\n' '{"schema":"maintenance.annotations/1","annotations":[]}' > "$TASK_TMP/annotations.json"
"$TASK_TMP/bin/maintenance-bench" validate "$TASK_TMP/gh.json" "$TASK_TMP/annotations.json" "$ROOT/assets/fixtures/analytical.manifest.json"
grep -q 'page=2' "$MB_GH_LOG"
grep -q '/reviews?' "$MB_GH_LOG"
grep -q '/pulls/1/comments?' "$MB_GH_LOG"
grep -q '/issues/1/comments?' "$MB_GH_LOG"
"$TASK_TMP/bin/maintenance-collect" github acme/demo ailang 1792713600000 2 1 "$TASK_TMP/capped.json"
if "$TASK_TMP/bin/maintenance-bench" validate "$TASK_TMP/capped.json" "$TASK_TMP/annotations.json" "$ROOT/assets/fixtures/analytical.manifest.json"; then echo 'incomplete cohort unexpectedly accepted' >&2; exit 1; fi
if MB_GH_FAIL=1 "$TASK_TMP/bin/maintenance-collect" github acme/demo ailang 1792713600000 2 2 "$TASK_TMP/failure.json"; then echo 'failed gh unexpectedly succeeded' >&2; exit 1; fi
[ ! -e "$TASK_TMP/failure.json" ]
# Disposable real Git history: Unicode/spaces and rename, no source-repo mutation.
git init -q "$TASK_TMP/source"
git -C "$TASK_TMP/source" config user.name 'Fixture'
git -C "$TASK_TMP/source" config user.email fixture@example.invalid
printf 'first\n' > "$TASK_TMP/source/old 解析.ail"
git -C "$TASK_TMP/source" add .
GIT_AUTHOR_DATE='2000-01-01T00:00:00Z' GIT_COMMITTER_DATE='2000-01-01T00:00:00Z' git -C "$TASK_TMP/source" commit -qm first
git -C "$TASK_TMP/source" mv 'old 解析.ail' 'new 解析.ail'
GIT_AUTHOR_DATE='2000-01-02T00:00:00Z' GIT_COMMITTER_DATE='2000-01-02T00:00:00Z' git -C "$TASK_TMP/source" commit -qm rename
BEFORE=$(git -C "$TASK_TMP/source" rev-parse HEAD)
"$TASK_TMP/bin/maintenance-collect" git "$TASK_TMP/source" acme/local ailang HEAD 1792713600000 20 "$TASK_TMP/git.json"
[ "$BEFORE" = "$(git -C "$TASK_TMP/source" rev-parse HEAD)" ]
[ -z "$(git -C "$TASK_TMP/source" status --porcelain)" ]
if "$TASK_TMP/bin/maintenance-bench" validate "$TASK_TMP/git.json" "$TASK_TMP/annotations.json" "$ROOT/assets/fixtures/analytical.manifest.json"; then echo 'commit age unexpectedly treated as acceptance' >&2; exit 1; fi
echo 'OK: installed CLI, offline replay, immutable outputs, gh failure/caps/reviews, real Git rename and acceptance-time controls'
