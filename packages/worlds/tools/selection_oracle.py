#!/usr/bin/env python3
"""Reference values for sunholo/worlds selection. Standard library only.

Role: oracle. It writes selection_reference_test.ail: the prior probability of
twelve acceptance regions, the mean of the life prior, and the distribution of
a sum of two and of three uniforms, each with a native test that holds
selection.ail to it.

    python3 -I tools/selection_oracle.py > selection_reference_test.ail
    python3 -I tools/selection_oracle.py --draws 200000 --no-table   # a quick look

The model is the registry's, written out again here and not read from the
package (stapledons-design physics/life-and-worlds.md, baseline-2026.11):

    life      fLife  = 1 - exp(-10^x),  x ~ Normal(0, 50^2)   (LW-7, Sandberg 2018 s3.1.1)
    minds     fMinds log-uniform on [1e-3, 1]                 (LW-8)
    tech      fTech  log-uniform on [1e-2, 1]                 (LW-9)
    lifetime  L      log-uniform on [1e2, 1e8] yr             (LW-10, LW-39, LW-40)
    window    W      5e9 yr                                   (LW-11)

and the acceptance test of game design r3/universe-lab.md:

    S_found = hzWorlds * fLife*fMinds*fTech * (L/W) * phi(L)
    S_ended = hzWorlds * fLife*fMinds*fTech * endedYr/W
    S_late  = S_found * min(1, gapYr/L)

phi(L) is interpolated between its knots, linearly in log share against log
lifetime, and held constant outside them. A universe is accepted when each
statistic is inside its band, edges included.

Two methods, neither of them the package's (which integrates in the abiogenesis
rate x and in log L with Gauss-Legendre panels placed at the kinks, and uses
the closed-form distribution of a sum of uniforms):

1. Monte Carlo. Draw the four parameters, compute the three statistics as
   written above, count. No algebra. The standard error is binomial.
2. Quadrature. For a given life quantile u1 and lifetime quantile u4 the
   accepted (minds, tech) pairs are the part of the unit square between two
   parallel lines; its area is found by clipping the square (no sum-of-uniforms
   formula). That area is integrated over u1 and u4 by nested adaptive
   Gauss-Kronrod (7, 15), in quantile space, with no knowledge of where the
   kinks are. Each cell is integrated twice, from 96 x 16 and from 160 x 24
   starting panels (not nested). The error stated for a cell is the larger of
   the difference between the two runs and the rule's own summed |K15 - G7|.
   The rule's own estimate is not enough: with 16 starting panels in u1 it
   reported 2e-10 for the cell tail1e5 while the value was off by 1e-7 (the
   accepted life quantiles are a narrow range that the rule under-resolved).
   The package's value showed the gap; tools/selection_validation.md records
   the third computation that settled it.

The script refuses to write a cell whose two methods differ by more than
3.5 standard errors, or whose quadrature error exceeds 1e-9 of the value.
"""
import heapq
import math
import random
import statistics
import sys
import time

W = 5e9
SIGMA = 50.0
MINDS = (1e-3, 1.0)
TECH = (1e-2, 1.0)
LIFE = (1e2, 1e8)
NORMAL = statistics.NormalDist(0.0, SIGMA)
INF = float("inf")
SEED = 20261112

# hzWorlds: disc stars within the radius times 0.20 habitable-zone worlds a star.
HZ_81 = 1003.3
HZ_1000 = 1339731.6428103606
HZ_3000 = 20764332.0
TRACE = 814270.0  # 0.75 x the mean of a log-uniform 1e3..1e7 yr persistence, rounded

ANY = ("any",)


def at_least(lo):
    return ("atLeast", lo)


def at_most(hi):
    return ("atMost", hi)


def between(lo, hi):
    return ("between", lo, hi)


def cell(name, hz, reach, ended_yr, gap_yr, found, ended, late):
    return dict(name=name, hz=hz, reach=reach, endedYr=ended_yr, gapYr=gap_yr, found=found, ended=ended, late=late)


ALWAYS = [(1e5, 1.0)]
CELLS = [
    cell("found3", HZ_1000, ALWAYS, 0.0, 0.0, at_least(3.0), ANY, ANY),
    cell("threeBands", HZ_1000, [(1e3, 1.0), (1e6, 0.3), (1e8, 0.05)], TRACE, 2000.0,
         between(1.0, 50.0), between(0.5, 500.0), between(0.01, 5.0)),
    cell("nearOne", HZ_1000, ALWAYS, 0.0, 0.0, at_most(300.0), ANY, ANY),
    cell("tail1e5", HZ_81, ALWAYS, 0.0, 0.0, at_least(12.0), ANY, ANY),
    cell("tail1e6", HZ_81, ALWAYS, 0.0, 0.0, at_least(16.0), ANY, ANY),
    cell("narrow", HZ_1000, ALWAYS, TRACE, 1e4, between(3.0, 5.0), between(1.0, 3.0), at_least(0.02)),
    cell("lateOnly", HZ_3000, [(1e4, 1.0), (1e7, 0.01)], 0.0, 5e4, ANY, ANY, between(1.0, 2.0)),
    cell("endedOnly", HZ_1000, ALWAYS, TRACE, 0.0, ANY, at_least(2.0), ANY),
    cell("product32e6", W, ALWAYS, 0.0, 0.0, at_least(3.2e7), ANY, ANY),
    cell("product1e5", W, ALWAYS, 0.0, 0.0, at_least(1e5), ANY, ANY),
    cell("nearlyEmpty", HZ_1000, ALWAYS, 0.0, 0.0, at_most(1e-6), ANY, ANY),
    cell("gapAboveRange", HZ_1000, ALWAYS, 0.0, 1e9, at_least(3.0), ANY, at_most(30.0)),
]


def band_limits(b):
    if b[0] == "any":
        return 0.0, INF
    if b[0] == "atLeast":
        return b[1], INF
    if b[0] == "atMost":
        return 0.0, b[1]
    return b[1], b[2]


def phi(reach, life_yr):
    if life_yr <= reach[0][0]:
        return reach[0][1]
    if life_yr >= reach[-1][0]:
        return reach[-1][1]
    for (l0, s0), (l1, s1) in zip(reach, reach[1:]):
        if life_yr <= l1:
            t = math.log(life_yr / l0) / math.log(l1 / l0)
            return math.exp(math.log(s0) + t * (math.log(s1) - math.log(s0)))
    raise AssertionError


def stats_of(c, f_life, f_minds, f_tech, life_yr):
    lineage = f_life * f_minds * f_tech
    found = c["hz"] * lineage * (life_yr / W) * phi(c["reach"], life_yr)
    ended = c["hz"] * lineage * c["endedYr"] / W
    late = found * min(1.0, c["gapYr"] / life_yr)
    return found, ended, late


def accepted(c, limits, f_life, f_minds, f_tech, life_yr):
    s = stats_of(c, f_life, f_minds, f_tech, life_yr)
    return all(lo <= v <= hi for v, (lo, hi) in zip(s, limits))


def life_of(x):
    return -math.expm1(-(10.0 ** x)) if x < 300.0 else 1.0


def log_uniform(bounds, u):
    lo, hi = bounds
    return lo * (hi / lo) ** u


# ---- method 1: Monte Carlo ------------------------------------------------

def monte_carlo(cells, draws):
    rng = random.Random(SEED)
    limits = [[band_limits(c[k]) for k in ("found", "ended", "late")] for c in cells]
    hits = [0] * len(cells)
    life_sum = 0.0
    for _ in range(draws):
        f_life = life_of(rng.gauss(0.0, SIGMA))
        f_minds = log_uniform(MINDS, rng.random())
        f_tech = log_uniform(TECH, rng.random())
        life_yr = log_uniform(LIFE, rng.random())
        life_sum += f_life
        for i, c in enumerate(cells):
            if accepted(c, limits[i], f_life, f_minds, f_tech, life_yr):
                hits[i] += 1
    out = []
    for h in hits:
        p = h / draws
        out.append((p, math.sqrt(max(p * (1.0 - p), 1.0 / draws) / draws), h))
    return out, life_sum / draws


# ---- method 2: clipped areas inside adaptive Gauss-Kronrod ----------------

XGK = (0.991455371120812639206854697526329, 0.949107912342758524526189684047851,
       0.864864423359769072789712788640926, 0.741531185599394439863864773280788,
       0.586087235467691130294144838258730, 0.405845151377397166906606412076961,
       0.207784955007898467600689403773245, 0.0)
WGK = (0.022935322010529224963732008058970, 0.063092092629978553290700663189204,
       0.104790010322250183839876322541518, 0.140653259715525918745189590510238,
       0.169004726639267902826583426598550, 0.190350578064785409913256402421014,
       0.204432940075298892414161999234649, 0.209482141084727828012999174891714)
WG = (0.129484966168869693270611432679082, 0.279705391489276667901467771423780,
      0.381830050505118944950369775488975, 0.417959183673469387755102040816327)


def gk15(f, a, b):
    c, h = 0.5 * (a + b), 0.5 * (b - a)
    fc = f(c)
    k = WGK[7] * fc
    g = WG[3] * fc
    for j in range(7):
        d = h * XGK[j]
        s = f(c - d) + f(c + d)
        k += WGK[j] * s
        if j % 2 == 1:
            g += WG[j // 2] * s
    return k * h, abs(k - g) * h


def adaptive(f, a, b, rel, floor, panels=8, limit=4000):
    """Global adaptive G7K15. Returns (value, summed error estimate)."""
    heap = []
    total = err = 0.0
    step = (b - a) / panels
    for i in range(panels):
        lo, hi = a + i * step, a + (i + 1) * step
        v, e = gk15(f, lo, hi)
        heapq.heappush(heap, (-e, lo, hi, v))
        total += v
        err += e
    count = panels
    while err > max(rel * abs(total), floor) and count < limit:
        e, lo, hi, v = heapq.heappop(heap)
        mid = 0.5 * (lo + hi)
        v1, e1 = gk15(f, lo, mid)
        v2, e2 = gk15(f, mid, hi)
        heapq.heappush(heap, (-e1, lo, mid, v1))
        heapq.heappush(heap, (-e2, mid, hi, v2))
        count += 1
        if count % 64 == 0:
            total = sum(item[3] for item in heap)
            err = sum(-item[0] for item in heap)
        else:
            total += v1 + v2 - v
            err += e1 + e2 + e
    total = math.fsum(item[3] for item in heap)
    err = math.fsum(-item[0] for item in heap)
    return total, err


def clip(poly, a, b, c):
    """Keep the part of a convex polygon where a*x + b*y <= c."""
    out = []
    n = len(poly)
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        dp, dq = a * p[0] + b * p[1] - c, a * q[0] + b * q[1] - c
        if dp <= 0.0:
            out.append(p)
        if (dp < 0.0 < dq) or (dq < 0.0 < dp):
            t = dp / (dp - dq)
            out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return out


def area(poly):
    n = len(poly)
    if n < 3:
        return 0.0
    return 0.5 * abs(math.fsum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1] for i in range(n)))


SQUARE = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]


def strip_area(wx, wy, lo, hi):
    """Area of the unit square where lo <= wx*x + wy*y <= hi."""
    poly = SQUARE
    if hi < INF:
        poly = clip(poly, wx, wy, hi)
    if lo > -INF:
        poly = clip(poly, -wx, -wy, -lo)
    return area(poly)


WM = math.log10(MINDS[1] / MINDS[0])
WT = math.log10(TECH[1] / TECH[0])
Y0 = math.log10(MINDS[0] * TECH[0])


def pair_area(c, limits, f_life, life_yr):
    """Share of (minds, tech) pairs accepted at this life fraction and lifetime."""
    per = stats_of(c, f_life, 1.0, 1.0, life_yr)  # each statistic per unit fMinds*fTech
    lo_y, hi_y = 0.0, INF
    for g, (lo, hi) in zip(per, limits):
        if g <= 0.0:
            if lo > 0.0:
                return 0.0
            continue
        lo_y = max(lo_y, lo / g)
        hi_y = min(hi_y, hi / g)
    if hi_y < lo_y:
        return 0.0
    lo_s = math.log10(lo_y) - Y0 if lo_y > 0.0 else -INF
    hi_s = math.log10(hi_y) - Y0 if hi_y < INF else INF
    if hi_y <= 0.0:
        return 0.0
    return strip_area(WM, WT, lo_s, hi_s)


def quadrature(c, inner_panels, outer_panels):
    limits = [band_limits(c[k]) for k in ("found", "ended", "late")]

    def outer(u4):
        life_yr = log_uniform(LIFE, u4)

        def inner(u1):
            return pair_area(c, limits, life_of(NORMAL.inv_cdf(u1)), life_yr)

        v, _ = adaptive(inner, 1e-300, 1.0 - 1e-16, 1e-12, 1e-20, panels=inner_panels)
        return v

    return adaptive(outer, 0.0, 1.0, 2e-11, 1e-22, panels=outer_panels)


def quadrature_twice(c):
    """Two runs from different, non-nested starting panels; the value of the
    finer and the larger of (their difference, the rule's own estimate)."""
    coarse, _ = quadrature(c, 96, 16)
    fine, err = quadrature(c, 160, 24)
    return fine, max(abs(fine - coarse), err)


def life_mean():
    return adaptive(lambda u: life_of(NORMAL.inv_cdf(u)), 1e-300, 1.0 - 1e-16, 1e-13, 1e-16, panels=16)


# ---- sums of uniforms, geometrically --------------------------------------

def sum2_cdf(w, x):
    return strip_area(w[0], w[1], -INF, x)


def sum3_cdf(w, x):
    v, _ = adaptive(lambda u: sum2_cdf(w, x - w[2] * u), 0.0, 1.0, 1e-14, 1e-26, panels=64)
    return v


def sum_cdf(w, x):
    return sum2_cdf(w, x) if len(w) == 2 else sum3_cdf(w, x)


SUM_POINTS = [((3.0, 2.0), x) for x in (0.5, 1.0, 2.0, 2.5, 3.7, 4.9)] + \
             [((3.0, 2.0, 6.0), x) for x in (0.3, 2.5, 5.5, 8.2, 10.6, 10.99)]


# ---- output ---------------------------------------------------------------

def lit(v):
    r = repr(float(v))
    return r if ("." in r or "e" in r or "inf" in r) else r + ".0"


def band_lit(b):
    if b[0] == "any":
        return "AnyCount"
    if b[0] == "atLeast":
        return "AtLeast(%s)" % lit(b[1])
    if b[0] == "atMost":
        return "AtMost(%s)" % lit(b[1])
    return "Between(%s,%s)" % (lit(b[1]), lit(b[2]))


def selftest():
    for k in range(0, 23):
        got, _ = gk15(lambda x: x ** k, -1.0, 1.0)
        want = 0.0 if k % 2 else 2.0 / (k + 1)
        assert abs(got - want) < 1e-14, (k, got, want)
    assert abs(strip_area(3.0, 2.0, -INF, 2.5) - 0.5) < 1e-15
    assert abs(sum3_cdf((1.0, 1.0, 1.0), 1.0) - 1.0 / 6.0) < 1e-13
    assert abs(phi([(1e3, 1.0), (1e5, 0.01)], 1e4) - 0.1) < 1e-15


def main():
    args = sys.argv[1:]
    draws = 10_000_000
    if "--draws" in args:
        draws = int(args[args.index("--draws") + 1])
    table = "--no-table" not in args
    selftest()
    t0 = time.time()
    mc, mc_life = monte_carlo(CELLS, draws)
    sys.stderr.write("monte carlo: %d draws, %.0f s\n" % (draws, time.time() - t0))
    rows = []
    worst_z = 0.0
    for c, (p_mc, se, hits) in zip(CELLS, mc):
        t0 = time.time()
        p, err = quadrature_twice(c)
        z = (p_mc - p) / se
        worst_z = max(worst_z, abs(z))
        sys.stderr.write("%-14s p %.12e  err %.1e (%.1e of p)  mc %.6e +- %.2e  hits %d  z %+.2f  %.0f s\n"
                         % (c["name"], p, err, err / p if p else 0.0, p_mc, se, hits, z, time.time() - t0))
        if abs(z) > 3.5:
            sys.exit("refused: %s differs from its Monte Carlo by %.2f standard errors" % (c["name"], z))
        if err > 1e-9 * p:
            sys.exit("refused: %s quadrature error %.2e of its value" % (c["name"], err / p))
        rows.append((c, p, err, p_mc, se, hits))
    mean, mean_err = life_mean()
    sys.stderr.write("life mean %.15f err %.1e; monte carlo %.6f\n" % (mean, mean_err, mc_life))
    if abs(mean - mc_life) > 3.5 * 0.5 / math.sqrt(draws):
        sys.exit("refused: life mean differs from its Monte Carlo")
    sums = [(w, x, sum_cdf(w, x), sum_cdf(w, sum(w) - x)) for w, x in SUM_POINTS]
    if not table:
        return
    out = []
    out.append("module sunholo/worlds/selection_reference_test")
    out.append("-- GENERATED by tools/selection_oracle.py; do not edit by hand.")
    out.append("-- The prior probability of %d acceptance regions, the mean of the life prior" % len(rows))
    out.append("-- and the distribution of a sum of uniforms, from an independent Python")
    out.append("-- oracle: clipped areas inside nested adaptive Gauss-Kronrod in quantile")
    out.append("-- space, and a Monte Carlo of the same priors (%d draws, seed %d)." % (draws, SEED))
    out.append("-- Reference error bound: 1e-9 of each probability; largest difference between")
    out.append("-- two starting grids in this run: %.2e of the value. Largest gap between the two" %
               max(err / p for _, p, err, _, _, _ in rows))
    out.append("-- oracle methods: %.2f standard errors. selection.ail must agree with the" % worst_z)
    out.append("-- quadrature to 1e-8 of the value and with the Monte Carlo within 3 standard errors.")
    out.append("import ./selection (Setting,Band,Between,AtLeast,AtMost,AnyCount,Probability,SelectionError,acceptanceProbability,productTail,priorMeans,sumUniformCdf,sumUniformSurvival)")
    out.append("import ./baseline (baseline)")
    out.append("import std/result (Result,Ok,Err)")
    out.append("import std/math (abs_Float)")
    out.append("import std/list (foldl,length)")
    out.append("")
    out.append("type Cell = {name:string,s:Setting,want:float,mc:float,se:float,hits:int}")
    out.append("pure func cells() -> [Cell] = [")
    body = []
    for c, p, err, p_mc, se, hits in rows:
        reach = ",".join("{lifetimeYr:%s,share:%s}" % (lit(l), lit(s)) for l, s in c["reach"])
        body.append(" {name:\"%s\",s:{hzWorlds:%s,reach:[%s],endedYr:%s,gapYr:%s,found:%s,ended:%s,late:%s},want:%s,mc:%s,se:%s,hits:%d}"
                    % (c["name"], lit(c["hz"]), reach, lit(c["endedYr"]), lit(c["gapYr"]), band_lit(c["found"]),
                       band_lit(c["ended"]), band_lit(c["late"]), lit(p), lit(p_mc), lit(se), hits))
    out.append(",\n".join(body))
    out.append("]")
    out.append("pure func lifeMeanWant() -> float = %s" % lit(mean))
    out.append("-- widths, x, P(sum <= x), P(sum >= x)")
    out.append("pure func sums() -> [{w:[float],x:float,cdf:float,survival:float}] = [")
    out.append(",\n".join(" {w:[%s],x:%s,cdf:%s,survival:%s}" % (",".join(lit(v) for v in w), lit(x), lit(f), lit(s))
                          for w, x, f, s in sums))
    out.append("]")
    out.append("pure func named(name:string) -> [Cell] = foldl(\\acc c. if c.name==name then acc++[c] else acc,[],cells())")
    out.append("pure func holds(name:string) -> bool = match named(name) {")
    out.append(" [c] => (match acceptanceProbability(baseline(),c.s,1) {")
    out.append("  Ok(pr) => abs_Float(pr.p-c.want)+pr.error<=1e-8*c.want && abs_Float(c.mc-pr.p)<=3.0*c.se,")
    out.append("  Err(e) => false")
    out.append(" }),")
    out.append(" _ => false")
    out.append("}")
    for c, p, err, p_mc, se, hits in rows:
        out.append("test \"acceptanceProbability equals the oracle to 1e-8 and its Monte Carlo within 3 se: %s (p = %.3e)\" { holds(\"%s\") }"
                   % (c["name"], p, c["name"]))
    out.append("test \"the reference table has %d cells\" { length(cells())==%d }" % (len(rows), len(rows)))
    out.append("pure func tailGap(name:string,threshold:float) -> float = match (named(name),productTail(baseline(),threshold,1)) {")
    out.append(" ([c],Ok(pr)) => (abs_Float(pr.p-c.want)+pr.error)/c.want,")
    out.append(" _ => 1.0")
    out.append("}")
    out.append("test \"productTail (the three-uniform route) equals the oracle to 1e-8 at 3.2e7 and 1e5\" {")
    out.append(" tailGap(\"product32e6\",3.2e7)<=1e-8 && tailGap(\"product1e5\",1e5)<=1e-8")
    out.append("}")
    out.append("test \"the mean of the life prior equals the oracle to 1e-10\" {")
    out.append(" match priorMeans(baseline()) { Ok(m) => abs_Float(m.life-lifeMeanWant())<=1e-10, Err(e) => false }")
    out.append("}")
    out.append("pure func sumGap(r:{w:[float],x:float,cdf:float,survival:float}) -> float = match (sumUniformCdf(r.w,r.x),sumUniformSurvival(r.w,r.x)) {")
    out.append(" (Ok(f),Ok(s)) => { let a=abs_Float(f-r.cdf)/r.cdf; let b=abs_Float(s-r.survival)/r.survival; if a>b then a else b },")
    out.append(" _ => 1.0")
    out.append("}")
    out.append("test \"sums of two and three uniforms equal the oracle's clipped areas to 1e-11 of the value, both tails (12 points)\" {")
    out.append(" length(sums())==12 && foldl(\\ok r. ok && sumGap(r)<=1e-11,true,sums())")
    out.append("}")
    out.append("-- Probe: one line per cell, for tools/selection_validation.md.")
    out.append("export pure func referenceProbe() -> string =")
    out.append(" foldl(\\acc c. match acceptanceProbability(baseline(),c.s,1) {")
    out.append("  Err(e) => \"${acc}${c.name} ERR\\n\",")
    out.append("  Ok(pr) => \"${acc}${c.name} p ${pr.p} error ${pr.error} oracle ${c.want} gap ${abs_Float(pr.p-c.want)/c.want} mc ${c.mc} se ${c.se} z ${(c.mc-pr.p)/c.se}\\n\"")
    out.append(" },\"\",cells())")
    sys.stdout.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
