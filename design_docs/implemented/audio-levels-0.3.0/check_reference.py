"""Independent Decimal energy oracle and descriptive CLI timing, not audio latency.

Run from any directory: python3 <this-file> [--benchmark].
Requires the installed AILANG binary; never opens an audio device or writes audio.
"""
import argparse
from decimal import Decimal, localcontext
import json
import math
from pathlib import Path
import platform
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PROBE = HERE / "reference_probe.ail"


def rms(values):
    if not values:
        return 0.0
    # Direct arbitrary-precision squares, independent of the implementation's
    # peak-scaled streaming recurrence and floating-point sum order.
    with localcontext() as context:
        context.prec = 90
        total = sum((Decimal.from_float(x) ** 2 for x in values), Decimal(0))
        return float((total / len(values)).sqrt())


def expected(index):
    channels = 1 if index % 2 == 0 else 2
    frames = 37 + index * 3 if index < 10 else 1027
    scale = 1e308 if index == 10 else 1e-300 if index == 11 else 4.0 if index == 9 else 1.0
    values = [
        [0.0 if (i // 7 + index) % 3 == 0 else ((i * 17 + ch * 11 + index * 3) % 29 - 14) / 16.0 * scale
         for ch in range(channels)]
        for i in range(frames)
    ]
    all_samples = [x for frame in values for x in frame]
    active = []
    active_frames = 0
    for start in range(0, frames, 7):
        window = values[start:start + 7]
        samples = [x for frame in window for x in frame]
        if rms(samples) >= 0.2:
            active.extend(samples)
            active_frames += len(window)
    return dict(frames=frames, samples=frames * channels,
                peak=max(map(abs, all_samples), default=0.0), rms=rms(all_samples),
                activeRms=rms(active), activeFrames=active_frames,
                fullScaleSamples=sum(abs(x) >= 1 for x in all_samples),
                overRangeSamples=sum(abs(x) > 1 for x in all_samples))


def run(entry, value, bytecode):
    command = ["ailang", "run", "--quiet", "--package-dir", str(ROOT / "packages/audio"),
               "--relax-modules", "--verify-contracts", "--entry", entry, "--args-json", str(value)]
    if bytecode:
        command.append("--strict-bytecode")
    command.append(str(PROBE))
    started = time.perf_counter()
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=60, check=True)
    return json.loads(result.stdout), round((time.perf_counter() - started) * 1000, 3)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", action="store_true")
    args = parser.parse_args()
    evidence = dict(kind="independent Decimal level reference and CLI timing",
                    platform=platform.platform(), architecture=platform.machine(),
                    physicalLatencyMeasured=False, relativeTolerance=1e-12, comparisons=[])
    for bytecode in (False, True):
        for index in range(12):
            actual, elapsed = run("probe", index, bytecode)
            want = expected(index)
            assert actual.keys() == want.keys(), (index, actual)
            for key, value in want.items():
                if key in ("rms", "activeRms"):
                    assert math.isclose(actual[key], value, rel_tol=1e-12, abs_tol=0.0), (index, key, actual[key], value)
                else:
                    assert actual[key] == value, (index, key, actual[key], value)
            evidence["comparisons"].append(dict(engine="strict-bytecode" if bytecode else "interpreter",
                                                fixture=index, checkedFields=len(want), passed=True, cliMs=elapsed))
    if args.benchmark:
        evidence["benchmark"] = []
        # Avoid pretending interpreter callback suitability from a tiny fixture.
        for bytecode, sizes in ((False, (4800,)), (True, (4800, 384000, 768000))):
            for frames in sizes:
                actual, elapsed = run("benchmark", frames, bytecode)
                assert actual == dict(frames=frames, gain=2), actual
                evidence["benchmark"].append(dict(engine="strict-bytecode" if bytecode else "interpreter",
                                                   frames=frames, rate=48000, audioSeconds=frames / 48000,
                                                   cliMs=elapsed, includes="startup, allocation, guards, contracts, analysis, gain and output checks"))
    evidence["passed"] = True
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()
