import argparse
import asyncio
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from api.app.ingestion.pipeline import run_poll_loop


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the BahnOps local polling loop for one or more stations."
    )
    parser.add_argument(
        "--station",
        dest="station_names",
        action="append",
        required=True,
        help="Station name to poll. Repeat this flag to poll multiple stations.",
    )
    parser.add_argument(
        "--interval-seconds",
        type=int,
        required=True,
        help="Polling interval in seconds.",
    )
    parser.add_argument(
        "--hour-offset",
        type=int,
        default=0,
        help="Hour offset for the DB plan endpoint.",
    )
    parser.add_argument(
        "--max-runs",
        type=int,
        default=None,
        help="Optional maximum number of polling cycles before stopping.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    asyncio.run(
        run_poll_loop(
            station_names=args.station_names,
            poll_interval_seconds=args.interval_seconds,
            hour_offset=args.hour_offset,
            max_runs=args.max_runs,
        )
    )


if __name__ == "__main__":
    main()
