#!/usr/bin/env python3
"""Independent reference values for sunholo/relativity 0.5.0 (photometry for
the relativistic sky). Standard library only.

Every expected number in photometry_sky_test.ail comes from here, never from
the AILANG under test.

  * photopicRadiance: absolute luminance of a blackbody, Km * int B_l ybar dl,
    computed two ways:
      - the package's ybar (Wyman, Sloan & Shirley 2013 fit, transcribed again
        here) with exact SI Planck constants and composite Simpson at 0.05 nm
        (the package sums at 1 nm with a rounded c2); and
      - the official CIE 1931 2-degree ybar at 5 nm (CIE 015:2018 table, as
        distributed by CVRL, cvrl.org ciexyz31_1.csv), trapezoid, which bounds
        the fit's own error.
    Physical anchor: the 1948-1979 candela was 1/60 of the luminance of 1 cm^2
    of a blackbody at the freezing point of platinum, i.e. 6.0e5 cd/m^2 at
    2041.4 K (ITS-90; BIPM SI Brochure, historical note), and the 1979
    definition (Km = 683 lm/W) was chosen to keep that value.
  * CMB seen temperature: T0 D in 50-digit Decimal (T0 = 2.725 K, HB-5), for
    the canon rows HB-62, HB-63 and HB-68 (stapledons-design
    physics/higgs-bubble.md).
  * Surface brightness: V mag/arcsec^2 -> cd/m^2 with the package's V zero
    point (V = -13.98 at 1 lux) over one square arcsecond.
  * Point-source threshold: Crumey (2014), MNRAS 442, 2600, arXiv:1405.4209:
    Eq. 53 (= Eq. 32 with the Blackwell constants of Eq. 26) for scotopic
    backgrounds, Eq. 33 with Eq. 27 above the split point B = 7.08e-2 cd/m^2,
    and the zero-background cut-off at B = 1e-5 cd/m^2 (Section 2, zeta =
    1.150e-9 lx). Crumey's checks: m0 = 6.93 at B = 2e-4 cd/m^2 with his
    zero point Z = 2.54e-6 lx (Section 3.1), 6.18 with F = 2.
  * teffFromBV: linear interpolation in Pecaut & Mamajek 2022.04.16, parsed
    here by column name (not by the generator's indices), at the B-V of the
    literature check stars.

Usage:
  python3 tools/photometry_ref.py [--mamajek EEM_dwarf_UBVIJHK_colors_Teff.txt] [--check]
"""
import argparse
import math
import sys
from decimal import Decimal, getcontext

getcontext().prec = 50

H = 6.62607015e-34        # J s (SI, exact)
C = 299792458.0           # m/s (SI, exact)
KB = 1.380649e-23         # J/K (SI, exact)
KM = 683.0                # lm/W at 540 THz (SI, exact)
T_CMB = 2.725             # K, higgs-bubble HB-5
V_ZERO = -13.98           # V magnitude giving 1 lux (package zero point)

# Official CIE 1931 2-degree ybar, 360-830 nm every 5 nm (CVRL ciexyz31_1.csv).
YBAR_CIE_5NM = [
    3.917e-06, 6.965e-06, 1.239e-05, 2.202e-05, 3.9e-05, 6.4e-05, 0.00012, 0.000217, 0.000396, 0.00064,
    0.00121, 0.00218, 0.004, 0.0073, 0.0116, 0.01684, 0.023, 0.0298, 0.038, 0.048, 0.06, 0.0739, 0.09098,
    0.1126, 0.13902, 0.1693, 0.20802, 0.2586, 0.323, 0.4073, 0.503, 0.6082, 0.71, 0.7932, 0.862, 0.91485,
    0.954, 0.9803, 0.99495, 1.0, 0.995, 0.9786, 0.952, 0.9154, 0.87, 0.8163, 0.757, 0.6949, 0.631, 0.5668,
    0.503, 0.4412, 0.381, 0.321, 0.265, 0.217, 0.175, 0.1382, 0.107, 0.0816, 0.061, 0.04458, 0.032,
    0.0232, 0.017, 0.01192, 0.00821, 0.005723, 0.004102, 0.002929, 0.002091, 0.001484, 0.001047, 0.00074,
    0.00052, 0.0003611, 0.0002492, 0.0001719, 0.00012, 8.48e-05, 6e-05, 4.24e-05, 3e-05, 2.12e-05,
    1.499e-05, 1.06e-05, 7.4657e-06, 5.2578e-06, 3.7029e-06, 2.6078e-06, 1.8366e-06, 1.2934e-06,
    9.1093e-07, 6.4153e-07, 4.5181e-07,
]


def planck_per_nm(l_nm, t):
    """Spectral radiance B_lambda in W m^-2 sr^-1 nm^-1."""
    lm = l_nm * 1e-9
    x = H * C / (lm * KB * t)
    if x > 700.0:
        return 0.0
    return 2.0 * H * C * C / lm ** 5 / math.expm1(x) * 1e-9


def ybar_fit(l):
    """Wyman, Sloan & Shirley (2013) JCGT 2(2), multi-lobe fit to CIE 1931 ybar."""
    def g(mu, s1, s2):
        t = (l - mu) / (s1 if l < mu else s2)
        return math.exp(-0.5 * t * t)
    return 0.821 * g(568.8, 46.9, 40.5) + 0.286 * g(530.9, 16.3, 31.1)


def radiance_fit(t, step=0.05):
    n = int(round((830.0 - 360.0) / step))
    total = 0.0
    for i in range(n + 1):
        l = 360.0 + i * step
        w = 1.0 if i in (0, n) else (4.0 if i % 2 else 2.0)
        total += w * ybar_fit(l) * planck_per_nm(l, t)
    return KM * total * step / 3.0


def radiance_cie(t):
    total = 0.0
    for i, y in enumerate(YBAR_CIE_5NM):
        l = 360.0 + 5.0 * i
        w = 0.5 if i in (0, len(YBAR_CIE_5NM) - 1) else 1.0
        total += w * y * planck_per_nm(l, t)
    return KM * total * 5.0


def cmb_rows():
    t0 = Decimal("2.725")
    one = Decimal(1)
    rows = []
    for label, eps in (("0.99c", Decimal("0.01")), ("1-beta=1e-6", Decimal("0.000001"))):
        beta = one - eps
        gamma = one / (eps * (2 - eps)).sqrt()
        efwd = ((2 - eps) / eps).sqrt()          # gamma (1 + beta) = e^phi
        rows.append((f"cmb ahead {label}", t0 * efwd))
        rows.append((f"cmb rest-frame 90deg {label} (gamma T0)", t0 * gamma))
        rows.append((f"cmb seen 90deg {label} (T0 / gamma)", t0 / gamma))
        # HB-68: theta' = 1/gamma rad from the pole, D = 1 / (gamma (1 - beta cos theta'))
        th = float(one / gamma)
        c = Decimal(repr(math.cos(th)))
        rows.append((f"cmb seen at 1/gamma rad {label}", t0 / (gamma * (one - beta * c))))
        rows.append((f"1/gamma {label} (deg)", Decimal(repr(math.degrees(th)))))
    return rows


def arcsec2_sr():
    a = math.pi / (180.0 * 3600.0)
    return a * a


def surface_lum(mu):
    return 10.0 ** (-0.4 * (mu - V_ZERO)) / arcsec2_sr()


R1, R2 = 6.505e-4, -8.461e-4      # Crumey Eq. 26 (Blackwell, scotopic)
R3, R4 = 1.772e-4, 7.167e-5       # Crumey Eq. 27 (Blackwell, photopic)
B_SPLIT = 7.08e-2                 # cd/m^2, Crumey Section 2.2
B_DARK = 1.0e-5                   # cd/m^2, zero-background cut-off


def crumey_dI(b):
    if not (b > B_DARK):
        b = B_DARK
    q = b ** 0.25
    h = b ** 0.5
    if b <= B_SPLIT:
        return (R1 * q + R2 * h) ** 2
    return (R3 * q + R4 * h) ** 2


def mamajek_bv(path):
    rows = []
    header = None
    for line in open(path, encoding="utf-8"):
        if line.startswith("#SpT"):
            if header is not None:
                break
            header = line[1:].split()
            continue
        if header is None or line.startswith("#"):
            continue
        f = line.split()
        if len(f) < len(header) - 1 or not f[0].endswith("V"):
            continue
        rec = dict(zip(header, f))
        try:
            rows.append((float(rec["B-V"]), float(rec["Teff"]), f[0]))
        except ValueError:
            continue
    return rows


def interp(rows, x):
    xs = [r[0] for r in rows]
    ys = [r[1] for r in rows]
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    for i in range(len(xs) - 1):
        if xs[i] <= x <= xs[i + 1]:
            return ys[i] + (x - xs[i]) * (ys[i + 1] - ys[i]) / (xs[i + 1] - xs[i])
    raise ValueError(x)


# (name, B-V, source of colour, literature Teff, source of Teff)
STARS = [
    ("Sun", 0.65, "Mamajek G2V", 5772.0, "IAU 2015 B3"),
    ("Sirius A", 0.009, "Hipparcos", 9940.0, "0.2.0 test row"),
    ("alpha Cen B", 0.900, "Hipparcos", 5260.0, "Kervella et al. 2003, A&A 404, 1087"),
    ("Barnard's", 1.729, "Koen et al. 2010 (B 11.24, V 9.511)", 3224.0, "Boyajian et al. 2012, ApJ 757, 112 (interferometric)"),
    ("Proxima", 1.82, "Jao et al. 2014 (B 12.95, V 11.13)", 3054.0, "Boyajian et al. 2012, ApJ 757, 112"),
    ("Proxima (Boyajian phot.)", 1.97, "Boyajian 2012 Table 3 (B 13.02, V 11.05)", 3054.0, "Boyajian et al. 2012"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mamajek")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    bad = []

    def want(label, got, expect, rel):
        ok = abs(got - expect) <= rel * abs(expect)
        if not ok:
            bad.append(f"{label}: {got!r} vs {expect!r} (rel {rel})")

    print("# photopicRadiance (cd/m^2): fit+Simpson | CIE 1931 5nm | fit/CIE - 1")
    for t in (2041.4, 2856.0, 3853.7, 3853.730994033574, 5772.0, 1926.9, 798.0, 38.44):
        f = radiance_fit(t)
        c = radiance_cie(t)
        rel = f / c - 1.0 if c > 0.0 else float("nan")
        print(f"T={t!r:>8}  {f!r:<24} {c!r:<24} {rel:+.3e}")
    print(f"T=2.725 photopic radiance: {radiance_fit(2.725)!r} (exp(-c2/(830 nm T)) = 10^{-0.014387768775/(830e-9*2.725)/math.log(10):.0f})")
    want("Pt-point candela anchor (CIE ybar)", radiance_cie(2041.4), 6.0e5, 0.01)

    print("\n# CMB seen temperature (K), Decimal")
    for label, v in cmb_rows():
        print(f"{label:<44} {v:.12f}")
    rows = dict(cmb_rows())
    want("HB-62", float(rows["cmb ahead 0.99c"]), 38.44, 0.00013)
    want("HB-63", float(rows["cmb ahead 1-beta=1e-6"]), 3853.7, 0.000013)
    want("HB-68", float(rows["1/gamma 1-beta=1e-6 (deg)"]), 0.0810, 0.0007)

    print("\n# Surface brightness (cd/m^2)")
    for mu in (22.0, 21.83, 18.0, 0.0):
        print(f"mu={mu!r:<6} {surface_lum(mu)!r}")
    want("mu=22 design 1.726e-4", surface_lum(22.0), 1.726e-4, 0.0005)

    print("\n# Crumey (2014) point threshold, F = 1 (lux)")
    for b in (0.0, 1.0e-6, 1.0e-5, 2.0e-4, 1.0e-3, 1.0e-2, 7.08e-2, 7.0801e-2, 1.0, 100.0, 1.0e4):
        print(f"B={b!r:<10} dI={crumey_dI(b)!r}")
    m0 = -2.5 * math.log10(crumey_dI(2.0e-4) / 2.54e-6)
    m0f2 = -2.5 * math.log10(2.0 * crumey_dI(2.0e-4) / 2.54e-6)
    mpkg = V_ZERO - 2.5 * math.log10(crumey_dI(2.0e-4))
    print(f"m0(2e-4) Crumey zero point: {m0!r}; F=2: {m0f2!r}; package zero point: {mpkg!r}")
    print(f"zeta = dI(1e-5) = {crumey_dI(1.0e-5)!r}  (Crumey: 1.150e-9 lx)")
    want("Crumey m0 6.93", m0, 6.93, 0.0008)
    want("Crumey m0 F=2 6.18", m0f2, 6.18, 0.0008)
    want("Crumey zeta", crumey_dI(1.0e-5), 1.150e-9, 0.0005)

    if args.mamajek:
        rows = mamajek_bv(args.mamajek)
        print(f"\n# teffFromBV, {len(rows)} rows {rows[0][2]}..{rows[-1][2]} (B-V {rows[0][0]}..{rows[-1][0]})")
        for name, bv, src, lit, lsrc in STARS:
            t = interp(rows, bv)
            print(f"{name:<26} B-V {bv:<6} -> {t!r:<20} lit {lit} ({100*(t/lit-1):+.2f}%)  [{src}; {lsrc}]")
        for bv in (-1.0, 0.0175, 1.5, 3.0):
            print(f"B-V {bv}: {interp(rows, bv)!r}")
    if args.check:
        if bad:
            print("\nFAIL:\n  " + "\n  ".join(bad))
            sys.exit(1)
        print("\nOK: every reference row matches its published value")


if __name__ == "__main__":
    main()
