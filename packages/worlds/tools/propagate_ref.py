#!/usr/bin/env python3
"""Independent oracle for sunholo/worlds propagate (0.2.0). Standard library only.

Role: oracle. It shares no code with the package. It reads the output of

    ailang run --entry oracleProbe propagate_test.ail > probe.txt
    python3 -I tools/propagate_ref.py probe.txt

and checks:
  1. `chain` rows: the Markov chain on the baseline generator, recomputed in
     50-digit decimal arithmetic (Taylor series with scaling and squaring),
     to 1e-13 per state.
  2. `exact` and `busy` rows: the exact kernels against a direct Monte Carlo
     of history.ail's sampler (re-implemented here: uniform onset, log-uniform
     lead and traces, fixed lifetime, .75/.15/.10 endings), to 5 standard
     errors + 1e-5 per state. Seeded, so the run is reproducible.
Exit status 0 only if every row agrees.
"""
import math, random, sys
from decimal import Decimal as D, getcontext

getcontext().prec = 50
NAMES = ["Sterile", "Microbial", "Complex", "PreTech", "Technological", "Remnant", "Transcended", "Ecocide"]
S, MI, C, P, T, R, TR, EC = range(8)
BASE = dict(q=0.03162277660168379 * 0.1 / 0.31622776601683794, L=1e5, W=5e9, rlo=1e3, rhi=1e7)
BUSY = dict(q=0.5, L=5e4, W=2e6, rlo=2e4, rhi=2e5)
DLO, DHI = 1e4, 1e5
MIXED = [0.05, 0.1, 0.2, 0.15, 0.3, 0.1, 0.04, 0.06]


def log_uniform_mean(lo, hi):
    return (D(hi) - D(lo)) / (D(hi) / D(lo)).ln()


def generator(p):
    """Rates per year, as stated in propagate.ail's header, in Decimal."""
    L, W, q = D(p["L"]), D(p["W"]), D(p["q"])
    lo, hi = D(p["rlo"]), D(p["rhi"])
    lead, traces = log_uniform_mean(DLO, DHI), log_uniform_mean(lo, hi)
    cap = max(W / 2 - L, D(0))
    # E[(cap-R)+] for R log-uniform, by direct integration of its density.
    k = (hi / lo).ln()
    if cap <= lo:
        faded = D(0)
    elif cap >= hi:
        faded = cap - traces
    else:
        faded = (cap * (cap / lo).ln() - (cap - lo)) / k
    still = 1 - q + q * (D("0.5") - lead / W + D("0.75") * faded / W)
    Q = [[D(0)] * 8 for _ in range(8)]
    Q[C][P] = q / W / still
    Q[P][T] = 1 / lead
    Q[T][R], Q[T][EC], Q[T][TR] = D("0.75") / L, D("0.15") / L, D("0.10") / L
    Q[R][C] = 1 / traces
    for i in range(8):
        Q[i][i] = -sum(Q[i])
    return Q


def matmul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(8)) for j in range(8)] for i in range(8)]


def expm(Q, t):
    t = D(t)
    norm = max(-Q[i][i] for i in range(8)) * t
    k = 0
    while norm > D("0.5"):
        norm /= 2
        k += 1
    A = [[Q[i][j] * t / (2 ** k) for j in range(8)] for i in range(8)]
    eye = [[D(1) if i == j else D(0) for j in range(8)] for i in range(8)]
    out, term = [row[:] for row in eye], [row[:] for row in eye]
    for n in range(1, 60):
        term = [[x / n for x in row] for row in matmul(term, A)]
        out = [[out[i][j] + term[i][j] for j in range(8)] for i in range(8)]
    for _ in range(k):
        out = matmul(out, out)
    return out


def state_at(h, t):
    if h is None:
        return C
    pre, tech, end, ending, traces = h
    if t < pre:
        return C
    if t < tech:
        return P
    if t < end:
        return T
    if ending == R:
        return R if t < traces else C
    return ending


def draw(p, rng, lo, hi):
    if rng.random() >= p["q"]:
        return None
    onset = lo + (hi - lo) * rng.random()
    lead = DLO * (DHI / DLO) ** rng.random()
    u = rng.random()
    ending = R if u < 0.75 else (EC if u < 0.90 else TR)
    end = onset + p["L"]
    return (onset - lead, onset, end, ending, end + p["rlo"] * (p["rhi"] / p["rlo"]) ** rng.random())


def monte_carlo(p, seen, years, kept, rng):
    """Frequencies at each of `years`, among histories in `seen` at epoch 0.
    Onset is drawn only where `seen` is possible at epoch 0 (exact conditioning)."""
    L, W = p["L"], p["W"]
    lo, hi = {T: (-L, 0.0), P: (0.0, DHI), R: (-L - p["rhi"], -L), C: (-W / 2, W / 2)}[seen]
    q1 = dict(p, q=1.0) if seen != C else p
    counts = [[0] * 8 for _ in years]
    n = 0
    while n < kept:
        h = draw(q1, rng, lo, hi)
        if state_at(h, 0.0) != seen:
            continue
        n += 1
        for i, t in enumerate(years):
            counts[i][state_at(h, t)] += 1
    return [[c / kept for c in row] for row in counts]


def main(path):
    rows = [line.split() for line in open(path) if line.strip()]
    worst_chain, worst_z, bad = 0.0, 0.0, 0
    Q = generator(BASE)
    exact = {}
    for row in rows:
        if row[0] == "rates":
            for got, want in zip(row[1:], (Q[C][P], Q[P][T], Q[R][C])):
                rel = abs(D(got) - want) / want
                worst_chain = max(worst_chain, float(rel))
                bad += rel > D("1e-13")
        elif row[0] == "chain":
            m = expm(Q, row[1])
            for j in range(8):
                want = sum(D(repr(MIXED[i])) * m[i][j] for i in range(8))
                err = abs(D(row[2 + j]) - want)
                worst_chain = max(worst_chain, float(err))
                bad += err > D("1e-13")
        elif row[0] == "exact":
            exact.setdefault(("base", row[1]), []).append((float(row[2]), [float(x) for x in row[3:]]))
        elif row[0] == "busy":
            exact.setdefault(("busy", "Complex"), []).append((float(row[1]), [float(x) for x in row[2:]]))
    rng = random.Random(20261112)
    kept = 400000
    for (which, name), items in sorted(exact.items()):
        p = BASE if which == "base" else BUSY
        freq = monte_carlo(p, NAMES.index(name), [t for t, _ in items], kept, rng)
        for (t, got), f in zip(items, freq):
            assert abs(sum(got) - 1) < 1e-12 and min(got) >= 0
            for j in range(8):
                tol = 5 * math.sqrt(got[j] * (1 - got[j]) / kept) + 1e-5
                z = abs(got[j] - f[j]) / tol
                worst_z = max(worst_z, z)
                if z > 1:
                    bad += 1
                    print("MISMATCH", which, name, t, NAMES[j], "kernel", got[j], "monte carlo", f[j])
    print(f"chain rows: worst error {worst_chain:.3e} (limit 1e-13)")
    print(f"exact rows: worst |kernel - monte carlo| / tolerance {worst_z:.3f} (limit 1, {kept} histories per seen state)")
    print("OK" if bad == 0 else f"FAIL: {bad} mismatches")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
