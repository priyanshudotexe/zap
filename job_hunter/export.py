"""Export ranked job results to various formats."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path

from .ranker import ScoredJob


def to_csv(jobs: list[ScoredJob], output_path: str = "output/results.csv"):
    """Write ranked jobs to CSV."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    if not jobs:
        return

    fieldnames = list(asdict(jobs[0]).keys())
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for job in jobs:
            writer.writerow(asdict(job))


def to_json(jobs: list[ScoredJob], output_path: str = "output/results.json"):
    """Write ranked jobs to JSON."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump([asdict(j) for j in jobs], f, indent=2)


def print_table(jobs: list[ScoredJob], max_rows: int = 30):
    """Pretty-print results to the terminal."""
    try:
        from rich.console import Console
        from rich.table import Table

        console = Console()
        table = Table(title="Job Matches", show_lines=True, expand=True)
        table.add_column("#", style="dim", width=3, no_wrap=True)
        table.add_column("Score", style="bold", width=5, no_wrap=True)
        table.add_column("Tier", width=14)
        table.add_column("Title", min_width=20, ratio=2)
        table.add_column("Company", min_width=12, ratio=1)
        table.add_column("Location", min_width=10, ratio=1)
        table.add_column("Site", width=8, no_wrap=True)
        table.add_column("URL", min_width=20, ratio=2, no_wrap=True)

        tier_colors = {
            "Strong Match": "green",
            "Worth Applying": "yellow",
            "Stretch": "dim",
        }

        for i, job in enumerate(jobs[:max_rows], 1):
            color = tier_colors.get(job.tier, "white")
            table.add_row(
                str(i),
                f"{job.score:.2f}",
                f"[{color}]{job.tier}[/{color}]",
                job.title,
                job.company,
                job.location,
                job.site,
                job.job_url,
            )

        console.print(table)
        console.print(f"\nTotal: {len(jobs)} matches shown (out of max {max_rows})")

    except ImportError:
        _print_plain(jobs, max_rows)


def _print_plain(jobs: list[ScoredJob], max_rows: int = 30):
    """Fallback plain text output if rich is not installed."""
    print(f"\n{'#':<4} {'Score':<7} {'Tier':<15} {'Title':<30} {'Company':<20} {'URL'}")
    print("-" * 120)
    for i, job in enumerate(jobs[:max_rows], 1):
        print(
            f"{i:<4} {job.score:<7.2f} {job.tier:<15} "
            f"{job.title[:29]:<30} {job.company[:19]:<20} {job.job_url}"
        )
    print(f"\nTotal: {len(jobs)} matches")
