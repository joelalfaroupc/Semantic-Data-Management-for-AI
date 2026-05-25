import argparse
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"


def pipeline_commands(p1_root: Path) -> list[list[str]]:
    return [
        ["build_kg.py", "--p1-root", str(p1_root)],
        ["run_sparql_analysis.py"],
        ["run_embedding_ml.py"],
        ["build_embedding_dashboard.py"],
    ]


def run_pipeline(p1_root: Path) -> None:
    for command in pipeline_commands(p1_root):
        script = SCRIPTS_DIR / command[0]
        subprocess.run([sys.executable, script, *command[1:]], check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the full semantic data management pipeline.")
    parser.add_argument(
        "--p1-root",
        type=Path,
        default=PROJECT_ROOT.parent / "BDA_DataPipeline",
        help="Path to the Project 1 BDA_DataPipeline repository",
    )
    args = parser.parse_args()

    run_pipeline(args.p1_root)


if __name__ == "__main__":
    main()
