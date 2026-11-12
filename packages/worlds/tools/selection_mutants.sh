#!/bin/sh
# Deliberate faults for selection.ail and the 0.3.0 closed forms in
# epoch_statistics.ail. Each fault is applied to a scratch copy of the package
# and the three test files are run on the bytecode VM; a fault "survives" if
# every test still passes. Prints one line per fault. Exit 1 if any survives.
#
#   sh tools/selection_mutants.sh            (from packages/worlds)
#
# Needs perl and the pinned ailang on PATH. Writes only under $TMPDIR.
set -u
here=$(cd "$(dirname "$0")/.." && pwd)
work=$(mktemp -d "${TMPDIR:-/tmp}/worlds-mutants.XXXXXX")
trap 'rm -rf "$work"' EXIT
tests="selection_test.ail selection_reference_test.ail epoch_closed_forms_test.ail"
survived=0

run() { # name file from to
  name=$1; file=$2
  rm -rf "$work/worlds"; mkdir -p "$work/worlds"
  (cd "$here" && cp ./*.ail ailang.toml ailang.lock "$work/worlds/")
  FROM=$3 TO=$4 perl -0pi -e '$c=()=/\Q$ENV{FROM}\E/g; exit 3 if $c!=1; s/\Q$ENV{FROM}\E/$ENV{TO}/' "$work/worlds/$file"
  if [ $? -ne 0 ]; then echo "$name | NOT APPLIED (pattern must match once in $file)"; survived=1; return; fi
  failed=""
  for t in $tests; do
    out=$(cd "$work/worlds" && ailang test --strict-bytecode "$t" 2>&1 | sed 's/\x1b\[[0-9;]*m//g')
    n=$(printf '%s\n' "$out" | grep '^  ✗ ' | grep -vc 'Failed:')
    if ! printf '%s\n' "$out" | grep -q 'tests: .* passed'; then failed="$failed ${t%_test.ail}:did-not-run"
    elif [ "$n" -gt 0 ]; then failed="$failed ${t%_test.ail}:$n"; fi
  done
  if [ -z "$failed" ]; then echo "$name | SURVIVED"; survived=1; else echo "$name | killed |$failed"; fi
}

# Control: an edit that changes nothing must survive, or the table means nothing.
control=$(run "control (no fault)" selection.ail 'pure func xTop() -> float = 2.0' 'pure func xTop() -> float = 2.0')
case "$control" in *SURVIVED) echo "control (no fault) | passes, as it must";; *) echo "$control"; echo "the unmutated tree does not pass; stopping"; exit 2;; esac
run "minds prior lower bound 0.001 -> 0.002" baseline.ail 'prior:LogUniform(0.001,1.0)' 'prior:LogUniform(0.002,1.0)'
run "life prior width 50 -> 49 dex" baseline.ail 'abiogenesisSigmaDex() -> float = 50.0' 'abiogenesisSigmaDex() -> float = 49.0'
run "draw: minds and tech read each other's uniform" selection.ail 'let fMinds=quantileOf(r.minds,nth_or(u,1,0.5));' 'let fMinds=quantileOf(r.minds,nth_or(u,2,0.5));'
run "draw: complex-life clamp at 1 dropped" selection.ail 'let capped=if raw>1.0 then 1.0 else raw;' 'let capped=raw;'
run "dialOf: round-trip check dropped" selection.ail 'else if sameParams(applyDial(b,d),p) then Ok(d) else Err(NotADial)' 'else Ok(d)'
run "dialOf: round-trip tolerance 1e-12 -> 1e-3" selection.ail 'abs_Float(a-b)<=1e-12*abs_Float(b)' 'abs_Float(a-b)<=1e-3*abs_Float(b)'
run "statistics: ended-sign time not held to the window" selection.ail 'else if s.endedYr>p.windowYr/2.0-p.lifetimeYr then Err(EndedOutsideWindow) else {' 'else {'
run "probability: ended-sign time not held to the window" selection.ail 'Ok(q) => if s.endedYr>q.window/2.0-q.longest then Err(EndedOutsideWindow) else {' 'Ok(q) => {'
run "luck over the mean uses the median lifetime" selection.ail 'Ok(m) => dexOver(p,m.life,m.minds,m.tech,m.lifetimeYr)' 'Ok(m) => dexOver(p,m.life,m.minds,m.tech,100000.0)'
run "Gauss-Legendre: one weight 0.1 % high" selection.ail '(0.09501250983763744,0.1894506104550685)' '(0.09501250983763744,0.1896400610655236)'
run "Normal density constant 0.1 % high" selection.ail 'sigma*2.5066282746310002' 'sigma*2.5091349029056312'
run "mass at fLife = 1 dropped" selection.ail '[xmin]++inner++[xTop()],n,sigma/2.0)+h(0.0)*above' '[xmin]++inner++[xTop()],n,sigma/2.0)'
run "mass below the lowest kink dropped" selection.ail 'hLow*normalCdf(xmin/sigma)+pieces' 'pieces'
run "sum of uniforms: a subset sign not flipped" selection.ail '(s,sign) => (s+x,0.0-sign)' '(s,sign) => (s+x,sign)'
run "survival taken as 1 - cdf in the upper tail" selection.ail 'else if x>=law.total/2.0 then lowerHalf(law,law.total-x) else 1.0-lowerHalf(law,x)' 'else 1.0-cdfOf(law,x)'
run "band: lower edge exclusive" selection.ail 'Between(lo,hi) => v>=lo && v<=hi,' 'Between(lo,hi) => v>lo && v<=hi,'
run "band: upper edge exclusive" selection.ail ' AtMost(hi) => v<=hi,' ' AtMost(hi) => v<hi,'
run "statistics: late share not capped at 1" selection.ail 'late:found*(if s.gapYr<p.lifetimeYr then s.gapYr/p.lifetimeYr else 1.0)' 'late:found*(s.gapYr/p.lifetimeYr)'
run "probability: late line not capped at the gap" selection.ail '(if v<fr.gap then v else fr.gap)' 'fr.gap'
run "probability: band edge enters without its log" selection.ail 'acc.lower++[{stat:stat,edge:log10(lo)}]' 'acc.lower++[{stat:stat,edge:lo}]'
run "probability: found line loses the lifetime" selection.ail 'Found => ln.edge-(fr.base+v+logShare(fr.reach,v)),' 'Found => ln.edge-(fr.base+logShare(fr.reach,v)),'
run "probability: hzWorlds/window inverted" selection.ail 'base:log10(s.hzWorlds)-log10(q.window)' 'base:log10(q.window)-log10(s.hzWorlds)'
run "probability: reach knots not used as panel ends" selection.ail 'let knots=map(\k. log10(k.lifetimeYr),s.reach)++(if s.gapYr>0.0 then [fr.gap] else []);' 'let knots=[];'
run "probability: line crossings not used as panel ends" selection.ail 'crossings(fr,ln.lower++ln.upper++levels,a,b)));' 'crossings(fr,[],a,b)));'
run "convergence rule 1e-6 -> 1e-3" selection.ail 'not (change<=1e-6*abs_Float(fine))' 'not (change<=1e-3*abs_Float(fine))'
run "expectedDraws of an empty region returns a number" selection.ail 'if pr.p>0.0 && pr.p<=1.0 then Ok(1.0/pr.p)' 'if pr.p>=0.0 && pr.p<=1.0 then Ok(1.0/pr.p)'
run "ended bins: ecocide given the transcendence share" epoch_statistics.ail 'ecocide:lineage*ecocideShare()*over/p.windowYr' 'ecocide:lineage*transcendenceShare()*over/p.windowYr'
run "ended bins: window edge ignored" epoch_statistics.ail 'let over=positive(p.windowYr/2.0-p.lifetimeYr);' 'let over=p.windowYr/2.0;'
run "late share: cap at 1 dropped" epoch_statistics.ail 'else Ok(minF(1.0,gapYr/lifetimeYr))' 'else Ok(gapYr/lifetimeYr)'
run "lineages: traces capped at the spacing, not the quiet gap" epoch_statistics.ail 'traceCappedMean(p.remnantLoYr,p.remnantHiYr,quiet)/p.windowYr' 'traceCappedMean(p.remnantLoYr,p.remnantHiYr,spacing)/p.windowYr'
run "lineages: overlap not refused" epoch_statistics.ail 'if spacing<p.lifetimeYr then Err(LineagesOverlap) else {' 'if spacing<0.0 then Err(LineagesOverlap) else {'
exit $survived
