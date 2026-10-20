"""Measure actual process startup and application snapshot restore costs."""

import argparse
import json
import pickle
import platform
import subprocess
import sys
import time
from pathlib import Path

CONFIGS = {
    "minimal": ["-S", "-c", "pass"],
    "stdlib": ["-c", "import json,sqlite3"],
    "application-snapshot": [
        "-c",
        "import pickle,sys; state=pickle.loads(sys.stdin.buffer.read()); assert len(state)==10000",
    ],
}


def measure(count: int = 20, inject_ms: float = 0) -> list[dict]:
    snapshot = pickle.dumps({str(i): i for i in range(10000)})
    rows = []
    for name, args in CONFIGS.items():
        values = []
        for _ in range(count):
            start = time.perf_counter()
            subprocess.run(
                [sys.executable, *args],
                input=snapshot if name == "application-snapshot" else b"",
                check=True,
            )
            time.sleep(inject_ms / 1000)
            values.append((time.perf_counter() - start) * 1000)
        rows.append(
            {
                "configuration": name,
                "runs": count,
                "p50_ms": sorted(values)[len(values) // 2],
                "p99_ms": max(values),
                "raw_ms": values,
            }
        )
    return rows


def benchmark() -> dict:
    rows = measure()
    result = {
        "configurations_measured": len(rows),
        "process_runs": sum(r["runs"] for r in rows),
        "kernel": platform.release(),
        "criu_restores": 0,
        "container_runs": 0,
        "rows": rows,
    }
    Path("evidence/baseline.json").write_text(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", action="store_true")
    parser.add_argument("--inject-ms", type=float, default=0)
    args = parser.parse_args()
    if args.gate:
        budget = (
            max(r["p99_ms"] for r in json.loads(Path("evidence/baseline.json").read_text())["rows"])
            + 50
        )
        observed = max(r["p99_ms"] for r in measure(2, args.inject_ms))
        passed = observed <= budget
        print(json.dumps({"p99_ms": observed, "budget_ms": budget, "passed": passed}))
        raise SystemExit(0 if passed else 1)
    print(json.dumps(benchmark(), indent=2))
