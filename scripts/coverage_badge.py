"""Create a Python line-and-branch coverage badge from pytest-cov's JSON report."""

import argparse
import json
from pathlib import Path


def render_badge(report):
    try:
        if report["meta"]["branch_coverage"] is not True:
            raise ValueError("Branch coverage must be measured")
        totals = report["totals"]
        lines, covered_lines, branches, covered_branches = (
            totals[key]
            for key in ("num_statements", "covered_lines", "num_branches", "covered_branches")
        )
    except (KeyError, TypeError) as error:
        raise ValueError("Missing coverage measurements") from error
    if any(
        type(value) is not int or value < 0
        for value in (lines, covered_lines, branches, covered_branches)
    ):
        raise ValueError("Coverage counts must be nonnegative integers")
    if covered_lines > lines or covered_branches > branches or lines + branches == 0:
        raise ValueError("Invalid coverage totals")

    # Round down to a tenth so partially covered code can never display 100%.
    tenths = (covered_lines + covered_branches) * 1000 // (lines + branches)
    percentage = f"{tenths // 10}.{tenths % 10}%"
    color = (
        "#4c1"
        if tenths >= 900
        else "#a4a61d"
        if tenths >= 800
        else "#dfb317"
        if tenths >= 700
        else "#e05d44"
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="177" height="20" role="img" aria-label="Python coverage: {percentage}">
  <title>Python coverage: {percentage}</title>
  <rect width="177" height="20" rx="3" fill="#555"/>
  <path d="M120 0h54a3 3 0 0 1 3 3v14a3 3 0 0 1-3 3h-54z" fill="{color}"/>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,DejaVu Sans,sans-serif" font-size="11">
    <text x="60" y="14">Python coverage</text>
    <text x="148" y="14">{percentage}</text>
  </g>
</svg>
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(render_badge(json.loads(args.input.read_text())))


if __name__ == "__main__":
    main()
