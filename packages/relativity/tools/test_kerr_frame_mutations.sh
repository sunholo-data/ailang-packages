#!/bin/sh
# Isolated package mutations: explicit ROOT, production never edited.
set -eu
ROOT=${1:?absolute package ROOT}; AILANG=${2:?absolute pinned ailang}
case "$ROOT" in /*) ;; *) exit 2;; esac
scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT HUP INT TERM
cp -R "$ROOT" "$scratch/pkg"
cd "$scratch/pkg"
cp kerr_frame.ail "$scratch/original"
killed=0
drill() {
  cp "$scratch/original" kerr_frame.ail
  export MUTATION_FROM=$1 MUTATION_TO=$2
  perl -0777 -i -pe 's/\Q$ENV{MUTATION_FROM}\E/$ENV{MUTATION_TO}/g' kerr_frame.ail
  if cmp -s "$scratch/original" kerr_frame.ail; then exit 3; fi
  set +e
  "$AILANG" test --strict-bytecode kerr_frame_test.ail > "$scratch/log" 2>&1
  rc=$?
  set -e
  test "$rc" = 1
  grep -F -q 'expected true, got false' "$scratch/log"
  killed=$((killed+1))
  echo "kerr-package mutation $3: killed"
}
drill 'f.lapse-f.omega*f.h*n.z' 'f.lapse' killing-energy
drill '{x:b*sqrt((1.0-v.z)*(1.0+v.z)),y:0.0,z:v.z}' '{x:b,y:0.0,z:v.z}' noncollinear-boost
test "$killed" = 2
