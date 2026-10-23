#!/usr/bin/env python3
"""Independent effects-fixture reference and descriptive whole-CLI timings."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import platform
import statistics
import struct
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "packages/audio"
OUT = Path(__file__).resolve().parent


def run(entry, arg, vm, contracts=True):
    command = ["ailang", "run", "--package-dir", str(PACKAGE)]
    if vm:
        command.append("--strict-bytecode")
    if contracts:
        command.append("--verify-contracts")
    command += ["--entry", entry, "--args-json", str(arg),
                str(PACKAGE / "examples/effects_pipeline.ail")]
    start = time.perf_counter()
    result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=60)
    return result.stdout.strip(), (time.perf_counter() - start) * 1000


def reference():
    # Exact binary fractions, independent of AILANG's delay/gain implementation.
    source = [0, 4096, 8192, 4096, 0, -4096, -8192, -4096]
    xs = [x / 32768 * ((i + 1) / 8) for i, x in enumerate(source)] + [0.0] * 720
    ring, output = [0.0] * 120, []
    for i, x in enumerate(xs):
        old = ring[i % 120]
        output.append(x + 0.5 * old)
        ring[i % 120] = x + 0.5 * old
    assert max(map(abs, output)) < 0.5  # PeakSafe leaves this fixture unchanged.
    pcm = [int(math.copysign(math.floor(abs(x) * 32767 + 0.5), x)) for x in output]
    data = struct.pack("<" + "h" * len(pcm), *pcm)
    wav = (b"RIFF" + struct.pack("<I", 36 + len(data)) + b"WAVEfmt "
           + struct.pack("<IHHIIHH", 16, 1, 1, 24000, 48000, 2, 16)
           + b"data" + struct.pack("<I", len(data)) + data)
    decoded = [x / 32768 for x in pcm]
    return {"frames": len(output), "wavBytes": len(wav),
            "wavSha256": hashlib.sha256(wav).hexdigest(),
            "preparedPeak": max(map(abs, output)),
            "deliveredPeak": max(map(abs, decoded)),
            "deliveredRms": math.sqrt(sum(x*x for x in decoded) / len(decoded))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timings", action="store_true", help="also run 24 descriptive CLI timing probes")
    args = parser.parse_args()
    expected = reference()
    engines = {}
    for vm in [False, True]:
        value, elapsed = run("demo", 0, vm)
        report = json.loads(value)
        for key, want in expected.items():
            if key == "deliveredRms":
                assert math.isclose(report[key], want, rel_tol=1e-14, abs_tol=1e-15)
            else:
                assert report[key] == want, (key, report[key], want)
        engines["strictVM" if vm else "interpreter"] = {"report": report, "cliMs": elapsed}
    assert engines["interpreter"]["report"] == engines["strictVM"]["report"]
    (OUT / "headless-example.json").write_text(json.dumps({
        "independentPythonReference": expected, "runtimeContractsEnabled": True,
        "engines": engines}, indent=2) + "\n")

    if not args.timings:
        print("PASS: independent PCM/WAV reference and interpreter/strict VM parity with runtime contracts")
        return

    timings = []
    for vm in [False, True]:
        for delay in [1, 127, 48000, 96000]:
            samples = []
            for _ in range(3):
                output, elapsed = run("benchmark", delay, vm, contracts=False)
                assert output == f"OK: 49152 stereo frames at 48000 Hz; delayFrames={delay}"
                samples.append(elapsed)
            timings.append({"engine": "strictVM" if vm else "interpreter",
                            "delayFrames": delay, "cliMs": samples,
                            "medianMs": statistics.median(samples)})
    (OUT / "timings.json").write_text(json.dumps({
        "kind": "descriptive whole-CLI timings including compile/startup/validation",
        "machine": platform.machine(), "os": platform.system(),
        "audioFrames": 49152, "channels": 2, "rate": 48000, "blockFrames": 4096,
        "runtimeContractsEnabled": False, "callbackDeadlineEstablished": False,
        "measurements": timings}, indent=2) + "\n")
    print("PASS: independent PCM/WAV reference, interpreter/strict VM parity, 24 CLI timing runs")


if __name__ == "__main__":
    main()
