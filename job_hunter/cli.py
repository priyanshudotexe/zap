"""CLI entry point for the job hunter."""

from __future__ import annotations

import logging
import sys

import click

from .config import DEFAULT_LOCATIONS, ROLE_PROFILES, SEARCH_SITES
from .export import print_table, to_csv, to_json
from .ranker import rank_jobs
from .resume_parser import extract_text
from .scraper import load_stored_jobs, scrape_role

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


@click.group()
def cli():
    """Zap Job Hunter — find PM and VC jobs matched to your resume."""
    pass


@cli.command()
@click.option(
    "--resume", "-r", required=True, type=click.Path(exists=True), help="Path to your resume PDF"
)
@click.option(
    "--role",
    "-R",
    required=True,
    type=click.Choice(list(ROLE_PROFILES.keys()), case_sensitive=False),
    help="Job role profile to search",
)
@click.option("--location", "-l", default="India", help="Job location filter")
@click.option("--remote", is_flag=True, default=False, help="Only remote jobs")
@click.option(
    "--sites",
    "-s",
    default=",".join(SEARCH_SITES),
    help="Comma-separated job sites (linkedin,indeed,glassdoor,zip_recruiter)",
)
@click.option("--top", "-n", default=30, help="Number of top matches to show")
@click.option("--export-csv", type=click.Path(), default=None, help="Export results to CSV")
@click.option("--export-json", type=click.Path(), default=None, help="Export results to JSON")
def search(resume, role, location, remote, sites, top, export_csv, export_json):
    """Scrape jobs and rank them against your resume."""
    profile = ROLE_PROFILES[role]
    site_list = [s.strip() for s in sites.split(",")]

    click.echo(f"\n=== Zap Job Hunter ===")
    click.echo(f"Role: {profile['name']}")
    click.echo(f"Location: {location}")
    click.echo(f"Sites: {', '.join(site_list)}")
    click.echo(f"Remote only: {remote}\n")

    click.echo("Parsing resume...")
    resume_text = extract_text(resume)
    click.echo(f"  Extracted {len(resume_text)} characters from resume\n")

    click.echo("Scraping jobs...")
    jobs_df = scrape_role(
        keywords=profile["keywords"],
        role=role,
        location=location,
        sites=site_list,
        is_remote=remote or None,
    )
    click.echo(f"  Scraped {len(jobs_df)} total job listings\n")

    if jobs_df.empty:
        click.echo("No jobs found. Try broader search terms or different sites.")
        sys.exit(0)

    click.echo("Ranking jobs against your resume...")
    ranked = rank_jobs(resume_text, jobs_df, role, top_n=top)
    click.echo(f"  Ranked {len(ranked)} jobs\n")

    print_table(ranked, max_rows=top)

    if export_csv:
        to_csv(ranked, export_csv)
        click.echo(f"\nExported to {export_csv}")
    if export_json:
        to_json(ranked, export_json)
        click.echo(f"\nExported to {export_json}")

    default_csv = f"output/{role}_results.csv"
    default_json = f"output/{role}_results.json"
    to_csv(ranked, default_csv)
    to_json(ranked, default_json)
    click.echo(f"\nResults saved to {default_csv} and {default_json}")


@cli.command()
@click.option(
    "--resume", "-r", required=True, type=click.Path(exists=True), help="Path to your resume PDF"
)
@click.option(
    "--role",
    "-R",
    default=None,
    type=click.Choice(list(ROLE_PROFILES.keys()), case_sensitive=False),
    help="Filter stored jobs by role",
)
@click.option("--top", "-n", default=30, help="Number of top matches to show")
def rerank(resume, role, top):
    """Re-rank previously scraped jobs against a (possibly updated) resume."""
    click.echo("Loading stored jobs...")
    jobs_df = load_stored_jobs(role)
    if jobs_df.empty:
        click.echo("No stored jobs found. Run 'search' first.")
        sys.exit(0)

    click.echo(f"  Found {len(jobs_df)} stored jobs\n")

    resume_text = extract_text(resume)
    ranked = rank_jobs(resume_text, jobs_df, role or "pm", top_n=top)
    print_table(ranked, max_rows=top)


@cli.command()
def roles():
    """List available role profiles."""
    click.echo("\nAvailable role profiles:\n")
    for key, profile in ROLE_PROFILES.items():
        click.echo(f"  {key:<6} {profile['name']}")
        click.echo(f"         Keywords: {', '.join(profile['keywords'][:5])}...")
    click.echo()


def main():
    cli()


if __name__ == "__main__":
    main()
