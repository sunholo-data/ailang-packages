#!/usr/bin/env python3
"""Generate blackbody_photometry_table.ail: Gaia EDR3 G/BP/RP and Bessell-Murphy V
response samples, the two colour zero points and the 61-node colour -> ln T table
for sunholo/relativity 0.3.0 (blackbody white-dwarf photometry). Stdlib only.

usage: python3 tools/gaia_bb_to_ail.py --input-dir D [--output F] check|validate|emit

Input directory layout (flat; sha256 of the first three is verified, a mismatch aborts):
  passband.dat            ESA cosmos GaiaEDR3_passbands_zeropoints_version2 (= VizieR J/A+A/649/A3)
  zeropt.dat              same zip
  alpha_lyr_mod_002.fits  CALSPEC Vega model (Riello+2021 eq. 18)
  validate only (not hashed; not committed): gf21.tsv (VizieR J/MNRAS/508/3877 query, see
  design doc row P12) and the CALSPEC STIS spectra named in STIS below, e.g.
  g191b2b_stiswfcnic_004.fits, gd153_stiswfcnic_004.fits, gd71_stiswfcnic_004.fits,
  gd50_stis_001.fits, wd1327_083_stiswfc_005.fits, wd0308_565_stis_010.fits, lds749b_stisnic_008.fits
"""
import argparse, hashlib, math, os, struct, sys
ap = argparse.ArgumentParser()
ap.add_argument("--input-dir", required=True)
ap.add_argument("--output", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "blackbody_photometry_table.ail"))
ap.add_argument("cmd", choices=["check", "validate", "emit"])
ARGS = ap.parse_args()
D = ARGS.input_dir
SHA = {"passband.dat": "46160d3b84dc0b78530d1ef3d18c0cf632fdaeb27876c0773c7a62033127f301",
       "zeropt.dat": "6370f5f9efe1d6c87b8922dea41ecd7e97e981d5dc2ad0f01f24f33f8044cec9",
       "alpha_lyr_mod_002.fits": "03491147809bb610975604589a4a3e68f866b080edb36c82b6ce76359d62991e"}
for name, want in SHA.items():
    got = hashlib.sha256(open(f"{D}/{name}", "rb").read()).hexdigest()
    if got != want:
        sys.exit(f"sha256 mismatch for {name}: got {got}, want {want}")
C2 = 14387769.0                                   # nm K, as blackbody.c2()
BM12_V = [0.000, 0.033, 0.176, 0.485, 0.811, 0.986, 1.000, 0.955, 0.865, 0.750, 0.656, 0.545, 0.434, 0.334,
          0.249, 0.180, 0.124, 0.075, 0.041, 0.022, 0.014, 0.011, 0.008, 0.006, 0.004, 0.002, 0.001, 0.000]
GRID = {"G": (320, 1050, 5), "BP": (325, 750, 5), "RP": (610, 1080, 5), "V": (470, 740, 10)}  # nm lo, hi, step
VEGA_V = 0.03                                     # Bessell & Murphy 2012, V of Vega
TLO, THI, N = 3000.0, 100000.0, 61

def load_bands():
    b = {"G": {}, "BP": {}, "RP": {}}
    for line in open(f"{D}/passband.dat"):
        r = line.split(); lam = float(r[0])
        for col, k in ((1, "G"), (3, "BP"), (5, "RP")):
            b[k][lam] = 0.0 if r[col] == "99.99" else float(r[col])
    b["V"] = {470.0 + 10 * i: s for i, s in enumerate(BM12_V)}
    return b

def fits_spectrum(path):                          # CALSPEC BINTABLE: WAVELENGTH [A], FLUX [FLAM]
    d = open(path, "rb").read(); off = 0
    while True:
        cards = {}
        while True:
            blk = d[off:off + 2880]; off += 2880
            cs = [blk[i:i + 80].decode("ascii", "replace") for i in range(0, 2880, 80)]
            for c in cs:
                if "=" in c[:10]: cards[c[:8].strip()] = c[10:].split("/")[0].strip().strip("'").strip()
            if any(c.startswith("END") for c in cs): break
        naxis = int(cards.get("NAXIS", 0))
        if cards.get("XTENSION", "").startswith("BINTABLE"):
            n1, n2 = int(cards["NAXIS1"]), int(cards["NAXIS2"])
            forms = [cards[f"TFORM{i + 1}"] for i in range(int(cards["TFIELDS"]))]
            names = [cards[f"TTYPE{i + 1}"] for i in range(len(forms))]
            fmt = ">" + "".join({"1D": "d", "1E": "f", "1I": "h", "1J": "i"}[f] for f in forms)
            rows = [struct.unpack(fmt, d[off + j * n1: off + (j + 1) * n1]) for j in range(n2)]
            return [r[names.index("WAVELENGTH")] / 10 for r in rows], [r[names.index("FLUX")] for r in rows], cards
        size = abs(int(cards["BITPIX"])) // 8 * math.prod(int(cards[f"NAXIS{i + 1}"]) for i in range(naxis)) if naxis else 0
        off += (size + 2879) // 2880 * 2880

B = load_bands(); KEYS = {k: sorted(v) for k, v in B.items()}
def resp(k, lam):                                 # linear interpolation of the tabulated response
    ks = KEYS[k]
    if lam <= ks[0] or lam >= ks[-1]: return 0.0
    lo, hi = 0, len(ks) - 1
    while hi - lo > 1:
        m = (lo + hi) // 2; lo, hi = (m, hi) if ks[m] <= lam else (lo, m)
    a, b = ks[lo], ks[hi]
    return B[k][a] + (B[k][b] - B[k][a]) * (lam - a) / (b - a)

def spec_int(k, wl, fl):                          # photon count ∝ ∫ f S λ dλ on the spectrum's own grid
    lo, hi, _ = GRID[k]; s = 0.0
    for i in range(len(wl) - 1):
        a, b = wl[i], wl[i + 1]
        if lo <= a and b <= hi:
            s += 0.5 * (resp(k, a) * a * fl[i] + resp(k, b) * b * fl[i + 1]) * (b - a)
    return s

def planck(l, T):                                 # same form as blackbody.planck
    e = C2 / (l * T)
    return 0.0 if e > 700.0 else (l / 1000.0) ** -5 / math.expm1(e)

def q(k, T, step=None):                           # package quadrature: trapezoid on the fixed grid
    lo, hi, st = GRID[k]; st = step or st; n = round((hi - lo) / st)
    return st * sum((0.5 if i in (0, n) else 1.0) * resp(k, lo + st * i) * (lo + st * i) * planck(lo + st * i, T)
                    for i in range(n + 1))

wl, fl, _ = fits_spectrum(f"{D}/alpha_lyr_mod_002.fits")       # alpha_lyr_mod_002 (Riello+2021 eq. 18)
VI = {k: spec_int(k, wl, fl) for k in GRID}
# Gaia mag of the unscaled Vega model through the published VEGAMAG ZPs (pupil 0.7278 m^2, SI):
ZP = dict(zip(("G", "BP", "RP"), map(float, open(f"{D}/zeropt.dat").readline().split()[0:6:2])))
VEGA_GAIA = {k: -2.5 * math.log10(0.7278 * VI[k] * 1e-2 * 1e-9 / 1.98644586e-25) + ZP[k] for k in ZP}
Z_BPRP = ZP["BP"] - ZP["RP"]                      # P/hc cancels: the colour ZP is the ZP difference
Z_BPRP_VEGA = 2.5 * math.log10(VI["BP"] / VI["RP"])  # cross-check: Vega colour 0 by Riello eq. 18
Z_GV = 2.5 * math.log10(VI["G"] / VI["V"]) + VEGA_GAIA["G"] - VEGA_V

def bprp(T, step=None): return -2.5 * math.log10(q("BP", T, step) / q("RP", T, step)) + Z_BPRP
def gmv(T, step=None): return -2.5 * math.log10(q("G", T, step) / q("V", T, step)) + Z_GV
def exact(c):                                     # 48 fixed bisection halvings in ln T
    if not c == c or c >= bprp(TLO): return TLO
    if c <= bprp(THI): return THI
    a, b = math.log(TLO), math.log(THI)
    for _ in range(48):
        m = 0.5 * (a + b); a, b = (m, b) if bprp(math.exp(m)) > c else (a, m)
    return math.exp(0.5 * (a + b))

LNT = [math.log(THI) + (math.log(TLO) - math.log(THI)) * i / (N - 1) for i in range(N)]  # colour ascending
COL = [bprp(math.exp(x)) for x in LNT]; GV = [gmv(math.exp(x)) for x in LNT]
def table(c, ys):
    if not c == c or c >= COL[-1]: return ys[-1]
    if c <= COL[0]: return ys[0]
    i = next(i for i in range(N - 1) if c <= COL[i + 1])
    return ys[i] + (c - COL[i]) * (ys[i + 1] - ys[i]) / (COL[i + 1] - COL[i])
def teff(c): return TLO if not c == c or c >= COL[-1] else THI if c <= COL[0] else math.exp(table(c, LNT))

def check():
    print("Vega Gaia mags via published ZPs:", {k: round(v, 5) for k, v in VEGA_GAIA.items()})
    print(f"Z_BPRP_VEGA={Z_BPRP_VEGA:.12f} (diff {Z_BPRP - Z_BPRP_VEGA:+.1e})")
    print(f"Z_BPRP={Z_BPRP:.12f} Z_GV={Z_GV:.12f} colour span [{COL[0]:.12f}, {COL[-1]:.12f}]")
    for T in (3000, 4000, 5772, 10000, 20000, 40000, 100000):
        print(f"T={T:6d} bbBpRp={bprp(T):+.12f} bbGMinusV={gmv(T):+.12f} |5nm-1nm|={abs(bprp(T) - bprp(T, 1)):.1e}")
    assert all(COL[i] < COL[i + 1] for i in range(N - 1)) and all(map(math.isfinite, COL + GV))
    sweep = [math.exp(math.log(TLO) + (math.log(THI) - math.log(TLO)) * i / 400) for i in range(401)]
    print("round trip table max rel %.3e" % max(abs(teff(bprp(T)) / T - 1) for T in sweep))
    print("round trip exact max rel %.3e" % max(abs(exact(bprp(T)) / T - 1) for T in sweep[::20]))
    print("G-V table max abs %.3e" % max(abs(table(bprp(T), GV) - gmv(T)) for T in sweep))
    ok = abs(Z_BPRP - 0.5906467146) < 1e-10 and all(abs(v - 0.023) <= 0.001 for v in VEGA_GAIA.values()) and abs(Z_BPRP - Z_BPRP_VEGA) < 1e-4
    print("AC-W1 check:", "PASS" if ok else "FAIL")
    if not ok: sys.exit(1)
    print("digest(400) =", repr(sum(teff(-0.6 + 2.9 * i / 400) for i in range(401))))

OBS = [  # name, Gaia DR3 source, DR3 BP-RP, literature Teff, Teff source
    ("G191-B2B", 266077145295627520, -0.524274, 59000, "CALSPEC g191b2b_mod_012"), ("GD 153", 3944400490365194368, -0.481523, 40204, "CALSPEC gd153_mod_012"),
    ("GD 71", 3348071631670500736, -0.452312, 33301, "CALSPEC gd71_mod_012"), ("GD 50", 3251244858154433536, -0.482519, 43740, "CALSPEC gd50_mod_001"),
    ("WD 1327-083", 3630035787972473600, -0.134162, 15100, "CALSPEC wd1327_083_mod_001"), ("WD 0308-565", 4727581523318486912, -0.268777, 22200, "CALSPEC wd0308_565_mod_008"),
    ("LDS 749B", 2687733913283870336, -0.092795, 13906, "CALSPEC lds749b_mod_008"), ("40 Eri B", 3195919254111315712, -0.191004, 16265, "GF21 TeffH"),
    ("Wolf 1346", 1831553382794173824, -0.275433, 20144, "GF21 TeffH"), ("L 745-46A", 5717278911884258176, 0.341712, 8154, "GF21 TeffH"),
    ("van Maanen 2", 2552928187080872832, 0.597588, 6594, "GF21 TeffH"), ("WD 0552-041", 3022956969731332096, 1.133657, 4900, "GF21 TeffH")]
STIS = {"G191-B2B": "g191b2b_stiswfcnic_004", "GD 153": "gd153_stiswfcnic_004", "GD 71": "gd71_stiswfcnic_004", "GD 50": "gd50_stis_001",
        "WD 1327-083": "wd1327_083_stiswfc_005", "WD 0308-565": "wd0308_565_stis_010", "LDS 749B": "lds749b_stisnic_008"}


def validate():
    for name, src, c, tl, ref in OBS:
        line = f"{name:13s} obs {c:+.4f}  T_bb {teff(c):8.0f}  T_lit {tl:6d} ({ref})  ratio {teff(c) / tl:.3f}"
        if name in STIS:
            w, f, _ = fits_spectrum(f"{D}/{STIS[name]}.fits"); I = {k: spec_int(k, w, f) for k in GRID}
            syn = -2.5 * math.log10(I["BP"] / I["RP"]) + Z_BPRP; sgv = -2.5 * math.log10(I["G"] / I["V"]) + Z_GV
            line += f"  synth-obs BP-RP {syn - c:+.4f}  bbG-V minus SED G-V {table(c, GV) - sgv:+.4f}"
            SYN.append(syn - c)
            if name in LANDOLT:
                dv = VEGA_V - 2.5 * math.log10(I["V"] / VI["V"]) - LANDOLT[name]
                line += f"  synth V - Landolt {dv:+.4f}"; DV[name] = dv
        print(line)
    rs = []
    for l in open(f"{D}/gf21.tsv"):
        f = l.rstrip("\n").split("\t")
        try: rs.append(teff(float(f[9])) / float(f[11]))
        except (ValueError, IndexError): pass
    rs.sort(); p = lambda x: rs[int(x * (len(rs) - 1))]
    w10 = sum(abs(r - 1) <= .1 for r in rs) / len(rs)
    print(f"GF21 50 pc n={len(rs)} median {p(.5):.3f} p16 {p(.16):.3f} p84 {p(.84):.3f} p2.5 {p(.025):.3f} p97.5 {p(.975):.3f} within10% {w10:.3f}")
    syn = sorted(SYN); med = syn[len(syn) // 2]
    ok = [-0.03 <= med <= 0.0, all(abs(v) <= 0.02 for v in DV.values()) and len(DV) == 3, w10 >= 0.95 and 1.00 <= p(.5) <= 1.06]
    print(f"AC-W2 CALSPEC median synth-obs BP-RP {med:+.4f} in [-0.03,0]: {ok[0]}; Landolt V within 0.02 (3 stars): {ok[1]}; GF21 >=95% within 10% and median in [1.00,1.06]: {ok[2]}")
    sys.exit(0 if all(ok) else 1)

def arr(name, xs, doc):
    body = ",\n".join("  " + ", ".join(repr(x) for x in xs[i:i + 6]) for i in range(0, len(xs), 6))
    return f"-- {doc}\nexport pure func {name}() -> [float] = [\n{body}\n]\n"

def emit():
    resp_nodes = lambda k: [resp(k, GRID[k][0] + GRID[k][2] * i) for i in range(round((GRID[k][1] - GRID[k][0]) / GRID[k][2]) + 1)]
    out = "\n".join([
        "-- Generated by: python3 tools/gaia_bb_to_ail.py --input-dir D emit   (do not edit; regenerate)",
        "-- Sources (sha256 verified by the generator):",
        "--   passband.dat  46160d3b...f301, zeropt.dat 6370f5f9...cec9: Gaia EDR3 passbands, Riello et al. 2021 (A&A 649, A3),",
        "--     https://www.cosmos.esa.int/documents/29201/1770596/GaiaEDR3_passbands_zeropoints.zip (version2; VizieR J/A+A/649/A3)",
        "--   alpha_lyr_mod_002.fits 03491147...991e: https://archive.stsci.edu/hlsps/reference-atlases/cdbs/calspec/alpha_lyr_mod_002.fits",
        "--   V: Bessell & Murphy 2012 (PASP 124, 140) Table 1 photonic V, typed in the generator; V of Vega = 0.03",
        "-- Samples are published values at the grid (no interpolation): G 320-1050 nm/5, BP 325-750/5, RP 610-1080/5, V 470-740/10.",
        "-- Convention: photon counting, Vega-mag (see CHANGELOG 0.3.0). Nodes: 61, uniform in ln T from 100000 K down to 3000 K.",
        "module sunholo/relativity/blackbody_photometry_table\n",
        arr("gaiaGResponse", resp_nodes("G"), "Gaia G photon response, 320-1050 nm step 5 (147 samples)"),
        arr("gaiaBpResponse", resp_nodes("BP"), "Gaia BP photon response, 325-750 nm step 5 (86 samples)"),
        arr("gaiaRpResponse", resp_nodes("RP"), "Gaia RP photon response, 610-1080 nm step 5 (95 samples)"),
        arr("johnsonVResponse", resp_nodes("V"), "Bessell-Murphy photonic V, 470-740 nm step 10 (28 samples)"),
        f"-- ZP_BP - ZP_RP (Gaia EDR3 VEGAMAG zero points)\nexport pure func zBpRp() -> float = {Z_BPRP!r}\n",
        f"-- 2.5 log10(I_G(Vega)/I_V(Vega)) + G(Vega) - V(Vega)\nexport pure func zGMinusV() -> float = {Z_GV!r}\n",
        arr("bbColourNodes", COL, "blackbody BP-RP at the nodes, strictly increasing (T from 100000 K down to 3000 K)"),
        arr("bbLnTeffNodes", LNT, "ln T at the nodes, from ln 100000 down to ln 3000"),
        arr("bbGMinusVNodes", GV, "blackbody G-V at the nodes"),
    ])
    open(ARGS.output, "w", encoding="utf-8").write(out)
    print("wrote", ARGS.output)

SYN, DV = [], {}
LANDOLT = {"GD 71": 13.032, "GD 153": 13.349, "GD 50": 14.063}   # Landolt V (SIMBAD), design row P6

if __name__ == "__main__":
    {"check": check, "validate": validate, "emit": emit}[ARGS.cmd]()
