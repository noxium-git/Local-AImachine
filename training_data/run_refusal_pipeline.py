import argparse
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRAINING_DIR = ROOT / "training_data"

BASE_MODEL = "godmoded/llama3-lexi-uncensored:latest"
TARGET_MODEL = "court-refusal-v1"


def run_cmd(cmd):
    print("$", " ".join(cmd))
    subprocess.run(cmd, cwd=str(ROOT), check=True)


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def parse_args():
    parser = argparse.ArgumentParser(description="Run end-to-end refusal reduction workflow.")
    parser.add_argument("--base", default=BASE_MODEL, help="Baseline model name")
    parser.add_argument("--target", default=TARGET_MODEL, help="Target policy model name")
    parser.add_argument("--skip-create", action="store_true", help="Skip model creation step")
    return parser.parse_args()


def main():
    args = parse_args()

    run_cmd(["python", "training_data/build_refusal_reduction_dataset.py"])

    base_report = TRAINING_DIR / "eval_report_baseline.json"
    target_report = TRAINING_DIR / "eval_report_target.json"

    run_cmd([
        "python",
        "eval_runner.py",
        "--model",
        args.base,
        "--report",
        str(base_report),
    ])

    if not args.skip_create:
        run_cmd([
            "python",
            "training_data/create_court_refusal_model.py",
            "--base",
            args.base,
            "--target",
            args.target,
        ])

    run_cmd([
        "python",
        "eval_runner.py",
        "--model",
        args.target,
        "--report",
        str(target_report),
    ])

    base = read_json(base_report)
    target = read_json(target_report)

    comparison = {
        "base_model": args.base,
        "target_model": args.target,
        "base_score": base.get("score", {}),
        "target_score": target.get("score", {}),
        "delta_false_refusals": target.get("score", {}).get("false_refusals", 0)
        - base.get("score", {}).get("false_refusals", 0),
        "delta_missed_refusals": target.get("score", {}).get("missed_refusals", 0)
        - base.get("score", {}).get("missed_refusals", 0),
        "delta_accuracy": round(
            target.get("score", {}).get("accuracy", 0.0)
            - base.get("score", {}).get("accuracy", 0.0),
            4,
        ),
    }

    comparison_path = TRAINING_DIR / "eval_comparison.json"
    comparison_path.write_text(json.dumps(comparison, indent=2), encoding="utf-8")
    print(json.dumps(comparison, indent=2))

    print("\nTo run app with the new model in PowerShell:")
    print(f"$env:COURT_MODEL='{args.target}'; python app.py")


if __name__ == "__main__":
    main()