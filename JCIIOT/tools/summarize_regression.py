"""Build an ordered regression summary from per-level physical execution reports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


LEVELS = ("L1", "L2", "L3", "L4", "L5")


def main() -> int:
    parser = argparse.ArgumentParser(description="Aggregate L1-L5 physical execution reports")
    parser.add_argument("record_dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    reports = []
    for level in LEVELS:
        report_path = args.record_dir / f"{level}.json"
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            raise SystemExit(f"Missing regression report: {report_path}")
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Invalid JSON in {report_path}: {exc}") from exc
        if report.get("level") != level:
            raise SystemExit(f"Regression report {report_path} identifies as {report.get('level')!r}, not {level}")
        reports.append(report)

    output = args.output or args.record_dir / "summary.json"
    output.write_text(json.dumps(reports, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote regression summary: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
