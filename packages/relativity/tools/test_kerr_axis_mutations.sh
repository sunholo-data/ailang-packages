#!/bin/sh
# Isolated angular-chart source mutations; never edits the production tree.
set -eu
ROOT=${1:?absolute package ROOT}; AILANG=${2:?absolute pinned binary}
case "$ROOT" in /*) ;; *) exit 2;; esac
scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT HUP INT TERM
cp -R "$ROOT" "$scratch/pkg"
cd "$scratch/pkg"
killed=0
drill() {
  file=$1; export MUTATION_FROM=$2 MUTATION_TO=$3
  cp "$ROOT/$file" "$file"
  perl -0777 -i -pe 's/\Q$ENV{MUTATION_FROM}\E/$ENV{MUTATION_TO}/g' "$file"
  if cmp -s "$ROOT/$file" "$file"; then exit 3; fi
  set +e
  "$AILANG" test --strict-bytecode "$4" > "$scratch/log" 2>&1
  rc=$?
  set -e
  test "$rc" = 1
  grep -F -q 'expected true, got false' "$scratch/log"
  cp "$ROOT/$file" "$file"
  killed=$((killed+1))
  echo "kerr-axis mutation $5: killed"
}
drill kerr_sphere.ail '(f+s*s)*y.m.z' 'f*y.m.z' kerr_sphere_test.ail angular-force
drill kerr_sphere.ail 'if l>0.0 then 0.0-angle else angle' '0.0' kerr_sphere_test.ail pole-phase-reset
drill kerr_trace.ail 'r/(2.0*c.u0)*sqrt(q)' 'absf(y.x)*r/(2.0*c.u0)*sqrt(q)' kerr_axis_test.ail tangent-root-stall
test "$killed" = 3
