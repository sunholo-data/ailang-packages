#!/bin/sh
# Isolated package mutations: explicit ROOT, production never edited.
set -eu
ROOT=${1:?absolute package ROOT}; AILANG=${2:?absolute pinned ailang}
case "$ROOT" in /*) ;; *) exit 2;; esac
scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT HUP INT TERM
cp -R "$ROOT" "$scratch/pkg"
cd "$scratch/pkg"
cp kerr_shadow.ail "$scratch/original"
killed=0
drill() {
  cp "$scratch/original" kerr_shadow.ail
  export MUTATION_FROM=$1 MUTATION_TO=$2
  perl -0777 -i -pe 's/\Q$ENV{MUTATION_FROM}\E/$ENV{MUTATION_TO}/g' kerr_shadow.ail
  if cmp -s "$scratch/original" kerr_shadow.ail; then exit 3; fi
  set +e
  "$AILANG" test --strict-bytecode kerr_shadow_test.ail > "$scratch/log" 2>&1
  rc=$?
  set -e
  test "$rc" = 1
  grep -F -q 'expected true, got false' "$scratch/log"
  killed=$((killed+1))
  echo "kerr-package mutation $3: killed"
}
drill '(0.0-p.lambda)/sqrt(sin2)' 'p.lambda/sqrt(sin2)' shadow-mirror
drill '*c*c/sin2' '*c*c' inclination
drill 'else lo+(hi-lo)*intToFloat(i)/intToFloat(n-1)' 'else lo+(hi-lo)*intToFloat(i)/intToFloat(n)' discrete-measure
test "$killed" = 3
