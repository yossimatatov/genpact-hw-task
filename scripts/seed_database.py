import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from tools.sql import DB_PATH, SEED_PATH, SCHEMA_PATH, seed_database  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Create and seed the local SQLite database.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete the existing database file before seeding.",
    )
    args = parser.parse_args()

    seed_database(reset=args.reset)

    print(f"Database ready: {DB_PATH}")
    print(f"Schema: {SCHEMA_PATH}")
    print(f"Seed: {SEED_PATH}")


if __name__ == "__main__":
    main()
