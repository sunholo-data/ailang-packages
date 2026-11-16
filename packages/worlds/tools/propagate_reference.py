#!/usr/bin/env python3
"""Reference values for sunholo/worlds propagate.historyKernel. Standard library only.

Role: oracle. It writes propagate_reference_test.ail, a table of the exact
conditional law of history.ail's sampler with a native test that holds
historyKernel to it at 1e-9 per state.

    python3 -I tools/propagate_reference.py > propagate_reference_test.ail

Method, independent of propagate.ail (no capped means, no kernel formulas):
for a fixed lead d, trace persistence r and ending, the state of a world at a
time t is a step function of its onset. So "state s0 at epoch 0 and state s1
at epoch x" is a set of onsets, a union of intervals whose ends are read off
history.stateAt, clipped to the onset window [-W/2, W/2]. Its length is exact.
The law is the ratio of expected lengths, the expectation being over the
log-uniform lead and persistence and the 0.75/0.15/0.10 endings; a complex
biosphere without a lineage (probability 1-q) is Complex at both times.
Nothing is assumed about window edges: this is the sampler's law everywhere,
including where propagate.ail does not claim exactness.

The two expectations are nested 20-point Gauss-Legendre rules in log d and
log r, split at every value where two interval ends can cross (so each piece
is smooth) and graded towards the one logarithmic singularity. Each cell is
computed twice, with the outer panels doubled; the script refuses to write a
cell whose two results differ by more than 1e-11, and prints the worst
difference in the generated file. Stated bound on every reference: 1e-10.
"""
import math
import sys

C, P, T, R, TR, EC = 2, 3, 4, 5, 6, 7
NAMES = {C: "Complex", P: "PreTech", T: "Technological", R: "Remnant"}
DLO, DHI = 1e4, 1e5
ENDINGS = ((R, 0.75), (EC, 0.15), (TR, 0.10))
INF = float("inf")

PARAMS = {
    # name: q = P(lineage | complex biosphere), L, W, traceLo, traceHi
    "base": dict(q=0.01, L=1e5, W=5e9, rlo=1e3, rhi=1e7),
    "busy": dict(q=0.5, L=5e4, W=2e6, rlo=2e4, rhi=2e5),
    "capBinds": dict(q=1.0, L=4e5, W=1e6, rlo=5e4, rhi=5e5),
    "longLife": dict(q=0.7, L=3e5, W=4e5, rlo=1e3, rhi=1e5),
    "fixedTrace": dict(q=0.5, L=1e5, W=1e6, rlo=5e4, rhi=5e4),
}
CELLS = [
    ("base", T, 867.0), ("base", T, 5e4), ("base", T, 1e5), ("base", T, 2e5), ("base", T, 3e6),
    ("base", P, 867.0), ("base", P, 4e4), ("base", P, 1.05e5), ("base", P, 1.5e5), ("base", P, 3e5),
    ("base", P, 2e6), ("base", P, 2e7),
    ("base", R, 867.0), ("base", R, 1e5), ("base", R, 3e6), ("base", R, 2e7),
    ("base", C, 1e5), ("base", C, 1e7), ("base", C, 2.4999e9),
    ("busy", C, 1e4), ("busy", C, 2e5), ("busy", C, 8e5), ("busy", C, 9e5),
    ("busy", P, 1.2e5), ("busy", P, 2e5), ("busy", T, 1e5), ("busy", R, 1e5),
    ("capBinds", R, 2e4), ("capBinds", R, 1e5), ("capBinds", R, 3e5),
    ("capBinds", T, 2e5), ("capBinds", T, 4e5), ("capBinds", C, 3e5), ("capBinds", P, 4e5),
    ("longLife", T, 5e4), ("longLife", T, 1e5), ("longLife", P, 8e4), ("longLife", C, 1e5),
    ("fixedTrace", P, 2e5), ("fixedTrace", P, 3e5), ("fixedTrace", C, 4e5), ("fixedTrace", R, 2e4),
]


def gauss_legendre(n):
    out = []
    for i in range(1, n + 1):
        x = math.cos(math.pi * (i - 0.25) / (n + 0.5))
        for _ in range(100):
            p0, p1 = 1.0, x
            for k in range(2, n + 1):
                p0, p1 = p1, ((2 * k - 1) * x * p1 - (k - 1) * p0) / k
            dp = n * (x * p1 - p0) / (x * x - 1)
            x -= p1 / dp
        p0, p1 = 1.0, x
        for k in range(2, n + 1):
            p0, p1 = p1, ((2 * k - 1) * x * p1 - (k - 1) * p0) / k
        dp = n * (x * p1 - p0) / (x * x - 1)
        out.append((x, 2 / ((1 - x * x) * dp * dp)))
    return out


GL = gauss_legendre(20)


def onset_sets(t, d, r, L, ending):
    """(state, lo, hi): the world is in `state` at time t iff lo < onset <= hi.
    From history.stateAt: before onset-d the background, then PreTech until
    onset, Technological until onset+L, then the ending; a Remnant fades back
    to the (complex) background at onset+L+r."""
    sets = [(C, t + d, INF), (P, t, t + d), (T, t - L, t)]
    if ending == R:
        sets += [(R, t - L - r, t - L), (C, -INF, t - L - r)]
    else:
        sets.append((ending, -INF, t - L))
    return sets


def lengths(seen, x, d, r, p):
    """Expected onset length, over endings, of {seen at 0} and of {seen at 0, s at x}."""
    half = p["W"] / 2
    out = [0.0] * 8
    for ending, share in ENDINGS:
        later = onset_sets(x, d, r, p["L"], ending)
        for s0, lo0, hi0 in onset_sets(0.0, d, r, p["L"], ending):
            if s0 != seen:
                continue
            lo0, hi0 = max(lo0, -half), min(hi0, half)
            if hi0 <= lo0:
                continue
            for s1, lo1, hi1 in later:
                span = min(hi0, hi1) - max(lo0, lo1)
                if span > 0:
                    out[s1] += share * span
    return out


def pieces(lo, hi, cuts):
    pts = sorted({c for c in cuts if lo < c < hi} | {lo, hi})
    return list(zip(pts, pts[1:]))


def log_average(f, lo, hi, cuts, panels):
    """E[f(v)] for v log-uniform on [lo, hi]; f returns a list of 8."""
    if hi <= lo:
        return f(lo)
    k = math.log(hi / lo)
    total = [0.0] * 8
    for a, b in pieces(lo, hi, cuts):
        ua, ub = math.log(a / lo) / k, math.log(b / lo) / k
        h = (ub - ua) / panels
        for i in range(panels):
            for node, w in GL:
                u = ua + h * (i + (node + 1) / 2)
                val = f(lo * math.exp(k * u))
                for j in range(8):
                    total[j] += w * h / 2 * val[j]
    return total


def law(name, seen, x, panels):
    p = PARAMS[name]
    L, half = p["L"], p["W"] / 2

    def given_lead(d):
        cuts = [half - L, x - L - d, x - L, x, x - L + half, x - L - half]
        return log_average(lambda r: lengths(seen, x, d, r, p), p["rlo"], p["rhi"], cuts, 1)

    cuts = [x, x - L, half, half - x, x - half, x - L - p["rlo"], x - L - p["rhi"]]
    # Grade towards d = x - L, where the inner limit x-L-d reaches zero.
    cuts += [x - L - p["rlo"] * 2.0 ** j for j in range(1, 40)]
    cuts += [x - L - p["rhi"] / 2.0 ** j for j in range(1, 14)]
    m = log_average(given_lead, DLO, DHI, cuts, panels)
    q = p["q"]
    num = [q * v for v in m]
    if seen == C:
        num[C] += (1 - q) * p["W"]
    den = sum(num)
    return [v / den for v in num]


def lit(v):
    s = repr(float(v))
    return s if ("." in s or "e" in s or "inf" in s) else s + ".0"


def main():
    rows, worst = [], 0.0
    for name, seen, x in CELLS:
        a, b = law(name, seen, x, 2), law(name, seen, x, 4)
        gap = max(abs(u - v) for u, v in zip(a, b))
        worst = max(worst, gap)
        if gap > 1e-11 or abs(sum(b) - 1) > 1e-12:
            sys.exit(f"not converged: {name} {NAMES[seen]} {x}: {gap:.3e}")
        rows.append((name, seen, x, b))
    w = sys.stdout.write
    w("module sunholo/worlds/propagate_reference_test\n")
    w("-- GENERATED by tools/propagate_reference.py; do not edit by hand.\n")
    w("-- The sampler's exact conditional law at %d cells, from an independent\n" % len(rows))
    w("-- Python oracle (onset-interval lengths, nested Gauss-Legendre). Reference\n")
    w("-- error bound 1e-10; worst difference between the two panel counts in this\n")
    w("-- run: %.2e. historyKernel must agree to 1e-9 in every state.\n" % worst)
    w("import ./propagate (Belief,PredictionError,historyKernel,exactDomain)\n")
    w("import ./history (PlanetState,Complex,PreTech,Technological,Remnant)\n")
    w("import ./dial (Params)\n")
    w("import std/result (Result,Ok,Err)\n")
    w("import std/math (abs_Float)\n")
    w("import std/list (foldl,range,nth_or,length)\n\n")
    w("type Cell = {name:string,p:Params,seen:PlanetState,years:float,want:[float]}\n")
    for name, p in PARAMS.items():
        w("pure func %s() -> Params = {fLife:1.0,fComplex:1.0,fMinds:1.0,fTech:%s,lifetimeYr:%s,windowYr:%s,remnantLoYr:%s,remnantHiYr:%s}\n"
          % (name, lit(p["q"]), lit(p["L"]), lit(p["W"]), lit(p["rlo"]), lit(p["rhi"])))
    for name in PARAMS:
        w("pure func %sCells() -> [Cell] = [\n" % name)
        mine = [r for r in rows if r[0] == name]
        for i, (_, seen, x, v) in enumerate(mine):
            w(" {name:\"%s\",p:%s(),seen:%s,years:%s,want:[%s]}%s\n"
              % (name, name, NAMES[seen], lit(x), ",".join(lit(t) for t in v), "," if i + 1 < len(mine) else ""))
        w("]\n")
    w("""pure func toL(b:Belief) -> [float] = [b.sterile,b.microbial,b.complex,b.preTech,b.technological,b.remnant,b.transcended,b.ecocide]
pure func worstGap(c:Cell) -> float = match historyKernel(c.p,c.seen,c.years) {
 Err(e) => 1.0,
 Ok(b) => foldl(\\acc i. {let d=abs_Float(nth_or(toL(b),i,9.0)-nth_or(c.want,i,9.0)); if d>acc then d else acc},0.0,range(0,8))
}
pure func allWithin(cells:[Cell]) -> bool = foldl(\\ok c. ok && exactDomain(c.p,c.years) && worstGap(c)<=1e-9,true,cells)
""")
    for name in PARAMS:
        n = len([r for r in rows if r[0] == name])
        w("test \"historyKernel equals the oracle's exact law to 1e-9: %s (%d cells)\" { length(%sCells())==%d && allWithin(%sCells()) }\n"
          % (name, n, name, n, name))
    w("-- Probe: the worst gap per cell, for tools/propagate_validation.md.\n")
    w("export pure func referenceProbe() -> string =\n foldl(\\acc c. \"${acc}${c.name} ${show(c.seen)} ${c.years} gap ${worstGap(c)}\\n\",\"\",%s)\n"
      % "++".join("%sCells()" % n for n in PARAMS))


if __name__ == "__main__":
    main()
