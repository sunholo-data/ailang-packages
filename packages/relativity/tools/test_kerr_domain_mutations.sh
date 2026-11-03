#!/bin/sh
# Isolated package mutations: explicit ROOT, production never edited.
set -eu
ROOT=${1:?absolute package ROOT}; AILANG=${2:?absolute pinned ailang}
case "$ROOT" in /*) ;; *) exit 2;; esac
scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT HUP INT TERM
cp -R "$ROOT" "$scratch/pkg"
cd "$scratch/pkg"
cp kerr_events.ail "$scratch/original"
killed=0
drill() {
  cp "$scratch/original" kerr_events.ail
  export MUTATION_FROM=$1 MUTATION_TO=$2
  perl -0777 -i -pe 's/\Q$ENV{MUTATION_FROM}\E/$ENV{MUTATION_TO}/g' kerr_events.ail
  if cmp -s "$scratch/original" kerr_events.ail; then exit 3; fi
  set +e
  "$AILANG" test --strict-bytecode kerr_domain_test.ail > "$scratch/log" 2>&1
  rc=$?
  set -e
  test "$rc" = 1
  grep -F -q 'expected true, got false' "$scratch/log"
  killed=$((killed+1))
  echo "kerr-package mutation $3: killed"
}
drill '(0.0-1.0e-5)*sqrt(if radial then 1.0+absf(root) else 1.0)/sqrt(absf(derivative))' '(0.0-1.0e-5)/sqrt(absf(derivative))' unrepresentable-root-departure
test "$killed" = 1
