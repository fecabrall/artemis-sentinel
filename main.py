"""CLI entrypoint for ARTEMIS Sentinel."""

from __future__ import annotations

import argparse
import json

from src.pipeline import run_artemis_pipeline


def main() -> None:
    """Run pipeline from CLI."""
    parser = argparse.ArgumentParser(description="ARTEMIS Sentinel mission validation pipeline")
    parser.add_argument("--anomaly", action="store_true", help="Enable anomaly mode in telemetry simulation")
    args = parser.parse_args()

    result = run_artemis_pipeline(samples=120, anomaly_mode=args.anomaly)
    print(json.dumps(result["summary"], indent=2, ensure_ascii=False))
    print(f"Relatório Excel: {result['report_path']}")


if __name__ == "__main__":
    main()
