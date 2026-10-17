"""Publish successful measurements to the generated benchmark-results branch."""

import argparse
import gzip
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

PLATFORMS = {"ubuntu-latest", "macos-latest"}


def stage_reports(artifacts, destination, run_id, run_url):
    if not re.fullmatch(r"[0-9]+-[0-9]+", run_id) or not run_url.startswith("https://github.com/"):
        raise ValueError("Use an explicit GitHub run ID/attempt and run URL")
    if (destination / "runs" / run_id).exists():
        raise ValueError(f"Run already exists: {run_id}")
    reports = {}
    for platform in sorted(PLATFORMS):
        source = artifacts / f"pipeline-reports-{platform}"
        report = json.loads((source / "releases.json").read_text())
        if report.get("error") or report.get("schema") != 1 or not report.get("runs"):
            raise ValueError(f"Cannot publish failed or empty report: {platform}")
        if not (source / "releases.md").is_file() or not (source / "locks").is_dir():
            raise ValueError(f"Incomplete benchmark report: {platform}")
        reports[platform] = (source, report)
    destination.mkdir(parents=True, exist_ok=True)
    history_file = destination / "history.json"
    history = json.loads(history_file.read_text()) if history_file.exists() else []
    for platform, (source, report) in reports.items():
        relative = Path("runs") / run_id / platform
        directory = destination / relative
        directory.mkdir(parents=True)
        shutil.copy2(source / "releases.md", directory / "releases.md")
        shutil.copytree(source / "locks", directory / "locks")
        raw = gzip.compress((source / "releases.json").read_bytes(), mtime=0)
        (directory / "releases.json.gz").write_bytes(raw)
        (destination / f"latest-{platform}.json.gz").write_bytes(raw)
        shutil.copy2(source / "releases.md", destination / f"latest-{platform}.md")
        products = report["environments"]["candidate"]["identity"]["packages"]
        versions = {
            name: value["version"] for name, value in products.items() if name.endswith("-turbo")
        }
        history.append(
            {
                "run_id": run_id,
                "platform": platform,
                "date": report["date"],
                "revision": report["source_revision"],
                "versions": versions,
                "report": str(relative / "releases.md"),
                "raw": str(relative / "releases.json.gz"),
                "workflow": run_url,
            }
        )
    history.sort(
        key=lambda value: (value["date"], value["run_id"], value["platform"]), reverse=True
    )
    history_file.write_text(json.dumps(history, indent=2) + "\n")
    lines = [
        "# Companion turbo performance history",
        "",
        "Generated from successful shared-dataset benchmarks. PRs cannot publish here.",
        "Each run compares the original Python trio, the initial turbo releases, the latest compatible published turbo set, and exact candidate wheels.",
        "Timing and whole-process peak RSS are descriptive measurements on shared CI machines. Compare the recorded hardware/platform and full-output parity before interpreting changes.",
        "",
        "| Date | Platform | Candidate versions | Report | Raw evidence | CI run |",
        "|---|---|---|---|---|---|",
    ]
    for entry in history:
        versions = ", ".join(
            f"{name} {version}" for name, version in sorted(entry["versions"].items())
        )
        lines.append(
            f"| {entry['date']} | {entry['platform']} | {versions} | [report]({entry['report']}) | [JSON.gz]({entry['raw']}) | [run]({entry['workflow']}) |"
        )
    (destination / "README.md").write_text("\n".join(lines) + "\n")


def run(*arguments):
    return subprocess.check_output(list(map(str, arguments)), text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", required=True, type=Path)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--run-url", required=True)
    parser.add_argument("--output", type=Path, help="Stage locally without GitHub writes")
    args = parser.parse_args()
    if args.output:
        stage_reports(args.artifacts, args.output, args.run_id, args.run_url)
        return
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", args.repository):
        raise ValueError("Expected owner/repository")
    run("gh", "auth", "setup-git")
    with tempfile.TemporaryDirectory(prefix="turbo-benchmark-history-") as temporary:
        checkout = Path(temporary) / "history"
        url = f"https://github.com/{args.repository}.git"
        exists = bool(run("git", "ls-remote", "--heads", url, "refs/heads/benchmark-results"))
        run("git", "clone", "--no-checkout", "--filter=blob:none", url, checkout)
        if exists:
            run(
                "git",
                "-C",
                checkout,
                "checkout",
                "-b",
                "benchmark-results",
                "origin/benchmark-results",
            )
        else:
            run("git", "-C", checkout, "switch", "--orphan", "benchmark-results")
        stage_reports(args.artifacts, checkout, args.run_id, args.run_url)
        run("git", "-C", checkout, "config", "user.name", "github-actions[bot]")
        run(
            "git",
            "-C",
            checkout,
            "config",
            "user.email",
            "41898282+github-actions[bot]@users.noreply.github.com",
        )
        run("git", "-C", checkout, "add", ".")
        run(
            "git",
            "-C",
            checkout,
            "-c",
            "commit.gpgsign=false",
            "commit",
            "-m",
            f"perf(history): record measured pipeline run {args.run_id}",
        )
        run("git", "-C", checkout, "push", "origin", "HEAD:refs/heads/benchmark-results")


if __name__ == "__main__":
    main()
