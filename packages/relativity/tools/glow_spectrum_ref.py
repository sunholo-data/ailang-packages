#!/usr/bin/env python3
"""Independent reference values for sunholo/relativity 0.8.0: the wall
glow's spectrum (medium.glowTemperatureAt, glowRadianceAt, glowEfficacyAt,
glowLuminanceAt; blackbody.stefanBoltzmannSI, luminousEfficacy). Standard
library only.

Every expected number for those functions in glow_spectrum_test.ail comes
from here, never from the AILANG under test.

Model (stapledons ledger D-30; stapledons-design physics/higgs-bubble.md
section 6): the wall is a greybody of emissivity eps. The thermalised flux
eps K max(0, cos theta) is radiated as eps sigma T^4, so

    T = (K max(0, cos theta) / sigma)^(1/4)          (eps cancels)

and the inner face emits eps fIn sigma T^4 = glowEmittanceAt, a blackbody
spectrum at T. Radiance L = emittance / pi (Lambertian). Luminance
= L x efficacy(T), efficacy(T) = pi Km int B_lambda(T) ybar dlambda
/ (sigma T^4), Km = 683 lm/W.

Independence from the package:
  * sigma is computed here from the exact SI constants h, k, c as
    2 pi^5 k^4 / (15 h^3 c^2) and checked against the package's
    5.670374419e-8; the oracle then uses the package's value, as the
    package does.
  * T is the Decimal fourth root (Decimal ** 1/4), not two float sqrts.
  * the Stefan-Boltzmann law and the package's radiance normalisation
    (2 h c^2 = 1.1910429723971884e5 W m^-2 sr^-1 nm^-1 per unit of
    `planck`) are checked by integrating Planck's law over all
    wavelengths (Simpson in x = hc / lambda k T): pi int B = sigma T^4.
  * the visible integral is the package's definition (its CIE ybar fit,
    360-830 nm, 1 nm rectangle sum, c2 = 14387769 nm K) evaluated in
    60-digit Decimal; a 0.1 nm Simpson integral of the same fit shows the
    1 nm sum's discretisation error (reported, not asserted).
  * efficacy's maximum over T is searched and compared with the CIE
    blackbody maximum (about 95 lm/W near 6,600 K).

Usage:
  python3 tools/glow_spectrum_ref.py          # print every check row
  python3 tools/glow_spectrum_ref.py --check  # also assert the canon digits
                                              # (higgs-bubble.md HB-95..HB-112)
                                              # and the relations; exit 1 on
                                              # mismatch
"""
import math
import sys
from decimal import Decimal, getcontext

getcontext().prec = 60
D = Decimal

C_SI = D(299792458)                    # m/s, exact
H_SI = D("6.62607015e-34")             # J s, exact
K_B = D("1.380649e-23")                # J/K, exact
M_P = D(1.67262192369e-27)             # kg, the package's float64 constant
N_ISM = D(100000)                      # m^-3 (0.1 cm^-3, HB-3)
EPS = D(1e-10)                         # HB-111 canon since the D-29 follow-up (float64 value)
EPS_D29 = D(1e-11)                     # the first D-29 value (0.8.0 check rows)
EPS_OLD = D(1e-9)                      # D-15, superseded by D-29
F_IN = D(0.5)
SIGMA_PKG = D(5.670374419e-8)          # the package's float64 constant
C2_PKG = D(14387769)                   # nm K, blackbody.c2()
RAD_PKG = D(119104.29723971884)        # W m^-2 sr^-1 nm^-1 per unit of planck
KM = D(683)
DARK_SKY_MU = D("23.5")                # mag/arcsec^2, the M1.5 dark sky


def dpi():
    def arctan_inv(m):
        x = D(1) / m
        s, t, k, x2 = D(0), x, 1, x * x
        while abs(t) > D(10) ** -65:
            s += t / k
            t = -t * x2
            k += 2
        return s
    return 16 * arctan_inv(5) - 4 * arctan_inv(239)


PI = dpi()


def dsinh(x):
    e = x.exp()
    return (e - 1 / e) / 2


def kinetic_flux(n, phi):
    phi = D(phi)
    h = dsinh(phi / 2)
    return n * dsinh(phi) * 2 * h * h * M_P * C_SI ** 3


def clamp_cos(c):
    return max(D(0), min(D(1), D(c)))


def temperature(n, phi, cos_t):
    x = kinetic_flux(n, phi) * clamp_cos(cos_t) / SIGMA_PKG
    return x ** (D(1) / 4) if x > 0 else D(0)


def emittance(n, phi, eps, fin, cos_t):
    return eps * fin * kinetic_flux(n, phi) * clamp_cos(cos_t)


# ---------- the package's CIE ybar fit and Planck, in Decimal ----------

def lobe(l, mu, s1, s2):
    s = s1 if l < mu else s2
    t = (l - mu) / s
    return (D("-0.5") * t * t).exp()


def ybar(l):
    l = D(l)
    return (D(0.821) * lobe(l, D(568.8), D(46.9), D(40.5))
            + D(0.286) * lobe(l, D(530.9), D(16.3), D(31.1)))


def planck_pkg(l, t):
    """blackbody.planck: (l/1000)^-5 / (exp(c2 / (l T)) - 1), l in nm."""
    l = D(l)
    e = C2_PKG / (l * t)
    if e > 700:
        return D(0)
    return (l / 1000) ** -5 / (e.exp() - 1)


YBAR_1NM = [(D(l), ybar(l)) for l in range(360, 831)]


def photopic_radiance(t):
    """blackbody.photopicRadiance: 683 x 1.19104e5 x sum ybar planck, 1 nm."""
    if t <= 0:
        return D(0)
    return KM * RAD_PKG * sum(y * planck_pkg(l, t) for l, y in YBAR_1NM)


def efficacy(t):
    p = photopic_radiance(t)
    return PI * p / (SIGMA_PKG * t ** 4) if p > 0 else D(0)


def efficacy_simpson(t, step=D("0.1")):
    """The same fit integrated by Simpson at `step` nm (discretisation check)."""
    m = int((D(830) - D(360)) / step)
    s = D(0)
    for i in range(m + 1):
        l = D(360) + i * step
        w = 1 if i in (0, m) else (4 if i % 2 else 2)
        s += w * ybar(l) * planck_pkg(l, t)
    integ = s * step / 3
    return PI * KM * RAD_PKG * integ / (SIGMA_PKG * t ** 4)


def sigma_exact():
    return 2 * PI ** 5 * K_B ** 4 / (15 * H_SI ** 3 * C_SI ** 2)


def stefan_by_planck(t, m=4000):
    """pi int_0^inf B_lambda(T) dlambda with the package's normalisation.

    Substituting x = c2 / (lambda T): int B dlambda = RAD (T/c2)^4 1e15
    int_0^inf x^3 / (e^x - 1) dx, with lambda in nm and (lambda/1000)^-5 in
    `planck` giving the 1e15. The x integral (pi^4/15) is done by
    Simpson on [1e-9, 60]; the tail beyond 60 is < 1e-20.
    """
    a, b = D("1e-9"), D(60)
    h = (b - a) / m
    s = D(0)
    for i in range(m + 1):
        x = a + i * h
        f = x ** 3 / (x.exp() - 1)
        w = 1 if i in (0, m) else (4 if i % 2 else 2)
        s += w * f
    integ = s * h / 3
    return PI * RAD_PKG * (t / C2_PKG) ** 4 * D(10) ** 15 * integ


def rgb_unit(t):
    """blackbody.rgbUnitLuminance (linear sRGB, Y = 1), Decimal."""
    X = Y = Z = D(0)
    for l in range(360, 831):
        dl = D(l)
        p = planck_pkg(dl, t)
        X += (D(1.056) * lobe(dl, D(599.8), D(37.9), D(31.0))
              + D(0.362) * lobe(dl, D(442.0), D(16.0), D(26.7))
              - D(0.065) * lobe(dl, D(501.1), D(20.4), D(26.2))) * p
        Y += ybar(dl) * p
        Z += (D(1.217) * lobe(dl, D(437.0), D(11.8), D(36.0))
              + D(0.681) * lobe(dl, D(459.0), D(26.0), D(13.8))) * p
    x, z = X / Y, Z / Y
    r = D(3.2404542) * x - D(1.5371385) - D(0.4985314) * z
    g = D(-0.9692660) * x + D(1.8760108) + D(0.0415560) * z
    b = D(0.0556434) * x - D(0.2040259) + D(1.0572252) * z
    mn = min(r, g, b)
    if mn < 0:
        k = -mn / (1 - mn)
        r, g, b = r * (1 - k) + k, g * (1 - k) + k, b * (1 - k) + k
    s = X + Y + Z
    return (r, g, b), (X / s, Y / s)


def dark_sky():
    """photometry.luminanceFromSurfaceMag(23.5) in Decimal."""
    a = PI / 648000
    return D(10) ** (D("-0.4") * (DARK_SKY_MU + D("13.98"))) / (a * a)


def rapidity_of_beta(b):
    b = D(b)
    return ((1 + b) / (1 - b)).ln() / 2


PHI05 = math.atanh(0.5)
PHI099 = 2.6466524123622457               # kinematics.rapidityOfBeta(0.99), the tests' phi099
PHI0999 = math.atanh(0.999)
PHICAP = 0.5 * (math.log(2.0 - 1.0e-6) - math.log(1.0e-6))
ANGLES = [0.0, 45.0, 80.0, 90.0, 120.0]


def cos_deg(deg):
    return math.cos(deg * math.pi / 180.0)


def fmt(x):
    return repr(float(x))


def pole_luminance(phi, eps):
    t = temperature(N_ISM, phi, 1.0)
    return emittance(N_ISM, phi, eps, F_IN, 1.0) / PI * efficacy(t)


def gamma_where(f, target, lo=D(1), hi=D(707)):
    """Bisection in gamma for f(phi) = target, f increasing in gamma."""
    for _ in range(80):
        mid = (lo + hi) / 2
        phi = (mid + (mid * mid - 1).sqrt()).ln()
        if f(phi) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def main():
    check = "--check" in sys.argv
    ok = True

    def expect(cond, label):
        nonlocal ok
        print(f"  relation {label}: {'ok' if cond else 'FAIL'}")
        ok = ok and cond

    print("constants:")
    se = sigma_exact()
    print(f"  sigma exact SI = {se} ; package {fmt(SIGMA_PKG)} ; rel {fmt(SIGMA_PKG / se - 1)}")
    expect(abs(SIGMA_PKG / se - 1) < D("1e-10"), "package sigma = 2 pi^5 k^4 / (15 h^3 c^2) to 1e-10")
    for t in (D(1357), D(6600), D(14114)):
        r = stefan_by_planck(t) / (SIGMA_PKG * t ** 4)
        print(f"  pi int B_lambda({t} K) / sigma T^4 = {fmt(r)}")
        # 6.2e-8 low: the package's c2 = 14387769 nm K is rounded from 14387768.775 (4 x 1.56e-8)
        expect(abs(r - 1) < D("1e-7"), f"Stefan-Boltzmann by Planck integral at {t} K (1e-7; c2 rounding)")
    ld = dark_sky()
    print(f"  dark sky 23.5 mag/arcsec^2 = {fmt(ld)} cd/m^2")

    print("efficacy (lm/W):")
    for t in (D(290), D(798), D(1000), D(1357.5), D(1500), D(2481.9), D(2856), D(4448.9), D(5772), D(6600), D(14114)):
        e = efficacy(t)
        print(f"  T={t} efficacy={fmt(e)} photopicRadiance={fmt(photopic_radiance(t))}")
    best = max((efficacy(D(t)), t) for t in range(6000, 7300, 50))
    print(f"  maximum over 6000..7250 K step 50: {fmt(best[0])} lm/W at {best[1]} K")
    expect(abs(best[0] - 95) < 2 and 6300 <= best[1] <= 6900, "efficacy peak ~95 lm/W near 6,600 K (CIE blackbody)")
    for t in (D(1357.5), D(6600), D(14114)):
        e1, es = efficacy(t), efficacy_simpson(t)
        print(f"  1 nm sum vs 0.1 nm Simpson at {t} K: {fmt(e1)} vs {fmt(es)} (rel {fmt(e1 / es - 1)})")

    print("glow temperature, emittance, radiance, efficacy, luminance (n 0.1 cm^-3, f_in 1/2):")
    for name, phi in (("0.5c", PHI05), ("0.99c", PHI099), ("0.999c", PHI0999), ("cap", PHICAP)):
        k = kinetic_flux(N_ISM, phi)
        print(f"{name}: phi={fmt(phi)} gamma={fmt(D(phi).exp() / 2 + (-D(phi)).exp() / 2)} K={fmt(k)}")
        for deg in ANGLES:
            c = cos_deg(deg)
            t = temperature(N_ISM, phi, c)
            eff = efficacy(t) if t > 0 else D(0)
            for epsname, eps in (("1e-10", EPS), ("1e-11", EPS_D29), ("1e-9", EPS_OLD)):
                e = emittance(N_ISM, phi, eps, F_IN, c)
                rad = e / PI
                lum = rad * eff
                print(f"  {name} theta={deg:g} cos={fmt(c)} T={fmt(t)} eff={fmt(eff)} eps={epsname}"
                      f" E={fmt(e)} L_rad={fmt(rad)} lum={fmt(lum)} lum/dark={fmt(lum / ld)}")
        tp = temperature(N_ISM, phi, 1.0)
        expect(abs(SIGMA_PKG * tp ** 4 / k - 1) < D("1e-50"), f"{name} sigma T_pole^4 = K")
        t45 = temperature(N_ISM, phi, cos_deg(45.0))
        expect(abs(t45 / (tp * D(cos_deg(45.0)) ** (D(1) / 4)) - 1) < D("1e-50"), f"{name} T(45) = T_pole cos^1/4")

    print("colour (linear sRGB, Y = 1; CIE x, y):")
    for name, phi in (("0.99c", PHI099), ("0.999c", PHI0999), ("cap", PHICAP)):
        t = temperature(N_ISM, phi, 1.0)
        rgb, xy = rgb_unit(t)
        print(f"  {name} pole T={fmt(t)} rgb=({fmt(rgb[0])}, {fmt(rgb[1])}, {fmt(rgb[2])}) x={fmt(xy[0])} y={fmt(xy[1])}")

    print("thresholds:")
    g_draper = gamma_where(lambda p: temperature(N_ISM, float(p), 1.0), D(798))
    g_dark = gamma_where(lambda p: pole_luminance(float(p), EPS), ld)
    g_03 = gamma_where(lambda p: pole_luminance(float(p), EPS), D("0.3") * ld)
    g_dark_old = gamma_where(lambda p: pole_luminance(float(p), EPS_OLD), ld)
    print(f"  gamma where the glow pole reaches the Draper point 798 K: {fmt(g_draper)}")
    print(f"  gamma where the pole luminance equals the dark sky, eps 1e-10: {fmt(g_dark)}")
    print(f"  gamma where the pole luminance reaches 0.3 of the dark sky, eps 1e-10 (HB-112): {fmt(g_03)}")
    print(f"  the same at eps 1e-9 (D-15, superseded): {fmt(g_dark_old)}")
    lum099 = pole_luminance(PHI099, EPS)
    eps_13 = D("1.3") * ld / (lum099 / EPS)
    print(f"  eps that would put the 0.99c pole at 1.3 x the dark sky with this spectrum: {fmt(eps_13)}")
    lum099_white = emittance(N_ISM, PHI099, EPS_OLD, F_IN, 1.0) / PI * D("182.5654375783963")
    print(f"  M4.2 placeholder (eps 1e-9, 182.565 lm/W white) at 0.99c: {fmt(lum099_white)} cd/m^2 = {fmt(lum099_white / ld)} x dark sky")

    if check:
        def printed(got, want, half, label):
            nonlocal ok
            good = abs(D(got) - D(want)) <= D(half)
            print(f"  check {label}: {fmt(got)} vs {want} +- {half}: {'ok' if good else 'MISMATCH'}")
            ok = ok and good

        print("canon digits (higgs-bubble.md section 6):")
        printed(temperature(N_ISM, PHI05, 1.0), "290", "0.5", "HB-95 T pole 0.5c")
        printed(temperature(N_ISM, PHI099, 1.0), "1358", "0.5", "HB-96 T pole 0.99c")
        printed(temperature(N_ISM, PHI0999, 1.0), "2482", "0.5", "HB-97 T pole 0.999c")
        printed(temperature(N_ISM, PHICAP, 1.0), "14114", "0.5", "HB-98 T pole cap")
        printed(g_draper, "2.89", "0.005", "HB-99 gamma at Draper")
        printed(efficacy(temperature(N_ISM, PHI099, 1.0)), "0.0233", "0.00005", "HB-100 efficacy 0.99c")
        printed(efficacy(temperature(N_ISM, PHICAP, 1.0)), "43.7", "0.05", "HB-101 efficacy cap")
        printed(emittance(N_ISM, PHI099, EPS, F_IN, 1.0), "9.63e-6", "5e-9", "HB-102 pole emittance 0.99c")
        printed(emittance(N_ISM, PHICAP, EPS, F_IN, 1.0), "0.1125", "5e-5", "HB-103 pole emittance cap")
        printed(lum099, "7.14e-8", "5e-11", "HB-104 pole luminance 0.99c")
        printed(lum099 / ld, "1.65e-3", "5e-6", "HB-105 0.99c / dark sky")
        printed(pole_luminance(PHICAP, EPS), "1.56", "0.005", "HB-106 pole luminance cap")
        printed(pole_luminance(PHICAP, EPS) / ld, "3.61e4", "50", "HB-107 cap / dark sky")
        printed(g_dark, "16.2", "0.05", "HB-108 gamma where pole = dark sky")
        printed(emittance(N_ISM, PHI099, EPS, F_IN, 1.0) / 4, "2.41e-6", "5e-9", "HB-109 mean inward glow 0.99c")
        printed(emittance(N_ISM, PHICAP, EPS, F_IN, 1.0) / 4, "2.81e-2", "5e-5", "HB-110 mean inward glow cap")
        printed(g_03, "13.5", "0.05", "HB-112 gamma where pole = 0.3 x dark sky")
        printed(EPS, "1e-10", "1e-25", "HB-111 eps")
        printed(1 / (F_IN * kinetic_flux(N_ISM, PHICAP) / 4), "3.6e-9", "5e-11", "HB-61 unchanged")
        printed(kinetic_flux(N_ISM, PHI099), "1.93e5", "500", "HB-45 unchanged")
        printed(kinetic_flux(N_ISM, PHICAP), "2.25e9", "5e6", "HB-46 unchanged")

    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
