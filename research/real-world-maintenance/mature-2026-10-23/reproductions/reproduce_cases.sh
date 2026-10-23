#!/bin/sh
# Public immutable source only. No model calls. Keep per-revision Rust build outputs separate.
set -eu
: "${AILANG_BIN:?Set AILANG_BIN to the validated v0.54.17 compiler}"
case_root=${1:?Supply a fresh absolute output directory}
case "$case_root" in /*) ;; *) echo 'Use an absolute directory' >&2; exit 2;; esac
if [ -e "$case_root" ]; then echo 'Output already exists' >&2; exit 2; fi
case_script_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
mkdir "$case_root"
python3 "$case_script_root/make_image_fixtures.py" "$case_root/fixtures"
for case_arm in before after; do
  if [ "$case_arm" = before ]; then case_sha=d8c04a66993d8abbe97a286be40ac975d1858557; case_expected=1; else case_sha=583e7d57cc53455af2268cd9fdb140507463941e; case_expected=0; fi
  mkdir -p "$case_root/ailang-$case_arm/docparse/services" "$case_root/ailang-$case_arm/docparse/types"
  for case_module in services/zip_extract types/document; do
    gh api -H 'Accept: application/vnd.github.raw+json' "repos/sunholo-data/ailang-parse/contents/docparse/$case_module.ail?ref=$case_sha" > "$case_root/ailang-$case_arm/docparse/$case_module.ail"
  done
  cp "$case_script_root/image_collision.ail.txt" "$case_root/ailang-$case_arm/probe.ail"
  (
    cd "$case_root/ailang-$case_arm"
    export AILANG_CACHE_DIR="$case_root/ailang-$case_arm-cache"
    "$AILANG_BIN" check probe.ail > "$case_root/ailang-$case_arm.check.log" 2>&1
    if "$AILANG_BIN" run --entry main --caps IO,FS,Env probe.ail -- "$case_root/fixtures" "$case_root/ailang-$case_arm-images" > "$case_root/ailang-$case_arm.json" 2> "$case_root/ailang-$case_arm.stderr.log"; then case_status=0; else case_status=$?; fi
    test "$case_status" -eq "$case_expected"
  )
done
jq -e '.pathsEqual==true and .firstImageStillOwnedByFirstDocument==false' "$case_root/ailang-before.json" >/dev/null
jq -e '.pathsEqual==false and .firstImageStillOwnedByFirstDocument==true' "$case_root/ailang-after.json" >/dev/null
for case_arm in before after; do
  if [ "$case_arm" = before ]; then case_sha=058cb507c8d74541f96d6439b6abd80e52f0c058; else case_sha=bec70ca56621a6aab429d676a14ee8db5b1a3c1c; fi
  mkdir "$case_root/rust-$case_arm"
  gh api "repos/tafia/calamine/tarball/$case_sha" > "$case_root/rust-$case_arm.tar.gz"
  tar -xzf "$case_root/rust-$case_arm.tar.gz" -C "$case_root/rust-$case_arm" --strip-components=1
  cp "$case_script_root/Cargo.lock" "$case_root/rust-$case_arm/Cargo.lock"
  cp "$case_script_root/maintenance_whitespace.rs" "$case_root/rust-$case_arm/tests/maintenance_whitespace.rs"
done
# Both revisions see exactly the same new input fixture and oracle. Production source is untouched.
cp "$case_root/rust-after/tests/whitespace_trim.xlsx" "$case_root/rust-before/tests/whitespace_trim.xlsx"
for case_arm in before after; do
  if [ "$case_arm" = before ]; then case_expected=101; else case_expected=0; fi
  (
    cd "$case_root/rust-$case_arm"
    if env -i PATH="$PATH" CARGO_HOME="$case_root/cargo-home" CARGO_TARGET_DIR="$case_root/rust-$case_arm-target" CARGO_BUILD_JOBS=4 cargo test --locked --test maintenance_whitespace -- --nocapture > "$case_root/rust-$case_arm.log" 2>&1; then case_status=0; else case_status=$?; fi
    test "$case_status" -eq "$case_expected"
  )
done
grep -q '0 passed; 2 failed;' "$case_root/rust-before.log"
grep -q '2 passed; 0 failed;' "$case_root/rust-after.log"
(
  cd "$case_root/rust-before"
  env -i PATH="$PATH" CARGO_HOME="$case_root/cargo-home" CARGO_TARGET_DIR="$case_root/rust-before-target" CARGO_BUILD_JOBS=4 cargo test --locked --test test test_whitespace_trim -- --nocapture > "$case_root/rust-before-existing.log" 2>&1
)
grep -q '2 passed; 0 failed;' "$case_root/rust-before-existing.log"
echo 'Confirmed: both AILANG sources type-check; ownership oracle fails before and passes after. Rust new oracle: 2 fail before / 2 pass after; original focused tests pass before.'
