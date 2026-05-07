from pathlib import Path
import json


RAW_DATA_DIR = Path("data/raw")
OUTPUT_PATH = Path("data/processed/jobs.json")


def main() -> None:
    jobs = []

    for path in sorted(RAW_DATA_DIR.glob("*.txt")):
        jobs.append(
            {
                "source_file": path.name,
                "title": "",
                "company": "",
                "location": "",
                "url": "",
            }
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(jobs, indent=2))
    print(f"Wrote {len(jobs)} jobs to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
