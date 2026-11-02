#!/bin/sh
set -eu
ROOT=${1:?absolute package ROOT}; AILANG=${2:?absolute pinned binary}
case "$ROOT" in /*) ;; *) exit 2;; esac
scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT HUP INT TERM
cp -R "$ROOT" "$scratch/pkg"
cd "$scratch/pkg"
killed=0
drill() {
  file=$1; testfile=$2; export MUTATION_FROM=$3 MUTATION_TO=$4
  cp "$ROOT/$file" "$file"
  perl -0777 -i -pe 's/\Q$ENV{MUTATION_FROM}\E/$ENV{MUTATION_TO}/g' "$file"
  if cmp -s "$ROOT/$file" "$file"; then exit 3; fi
  set +e
  "$AILANG" test --strict-bytecode "$testfile" > "$scratch/log" 2>&1
  rc=$?
  set -e
  test "$rc" = 1
  grep -F -q 'expected true, got false' "$scratch/log"
  cp "$ROOT/$file" "$file"
  killed=$((killed+1))
  echo "kerr-critical mutation $5: killed"
}
drill kerr_radial.ail kerr_radial_test.ail 'r.hi+r.lo' 'u*u*(u*u+s*s-l*l-e)+2.0*(e+(l-s)*(l-s))*u-s*s*e' cancellation
drill kerr_trace.ail kerr_nearcritical_test.ail 'let h=0.0-minf(basic,radialLimit);' 'let h=0.0-basic;' turning-resolution
test "$killed" = 2
