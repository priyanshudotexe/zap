"""Scrape jobs from multiple boards using python-jobspy."""

from __future__ import annotations

import logging
import sqlite3
import time
from pathlib import Path

import pandas as pd
from jobspy import scrape_jobs

from .config import DB_PATH, RESULTS_PER_KEYWORD, SEARCH_SITES

logger = logging.getLogger(__name__)


def _ensure_db(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Create the jobs table if it doesn't exist."""
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            site TEXT,
            title TEXT,
            company TEXT,
            location TEXT,
            date_posted TEXT,
            job_url TEXT,
            description TEXT,
            job_type TEXT,
            is_remote INTEGER,
            search_keyword TEXT,
            search_role TEXT,
            scraped_at TEXT DEFAULT (datetime('now'))
        )
        """
    )
    conn.commit()
    return conn


def _store_jobs(df: pd.DataFrame, keyword: str, role: str, db_path: str = DB_PATH):
    """Insert scraped jobs into SQLite, skipping duplicates."""
    conn = _ensure_db(db_path)
    inserted = 0
    for _, row in df.iterrows():
        job_id = str(row.get("id", f"{row.get('title', '')}-{row.get('company', '')}"))
        try:
            conn.execute(
                """
                INSERT OR IGNORE INTO jobs
                    (id, site, title, company, location, date_posted,
                     job_url, description, job_type, is_remote,
                     search_keyword, search_role)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job_id,
                    str(row.get("site", "")),
                    str(row.get("title", "")),
                    str(row.get("company", "")),
                    str(row.get("location", "")),
                    str(row.get("date_posted", "")),
                    str(row.get("job_url", "")),
                    str(row.get("description", "")),
                    str(row.get("job_type", "")),
                    1 if row.get("is_remote") else 0,
                    keyword,
                    role,
                ),
            )
            inserted += 1
        except sqlite3.IntegrityError:
            pass
    conn.commit()
    conn.close()
    return inserted


def scrape_role(
    keywords: list[str],
    role: str,
    location: str = "United States",
    sites: list[str] | None = None,
    results_wanted: int = RESULTS_PER_KEYWORD,
    is_remote: bool | None = None,
) -> pd.DataFrame:
    """Scrape jobs for a list of keywords and store them."""
    sites = sites or SEARCH_SITES
    all_frames: list[pd.DataFrame] = []

    for kw in keywords:
        logger.info(f"Scraping '{kw}' on {sites} in {location}...")
        try:
            df = scrape_jobs(
                site_name=sites,
                search_term=kw,
                location=location,
                results_wanted=results_wanted,
                is_remote=is_remote,
                description_format="markdown",
            )
            if df is not None and not df.empty:
                logger.info(f"  Found {len(df)} jobs for '{kw}'")
                _store_jobs(df, kw, role)
                all_frames.append(df)
            else:
                logger.info(f"  No results for '{kw}'")
        except Exception as e:
            logger.warning(f"  Error scraping '{kw}': {e}")
        time.sleep(2)

    if all_frames:
        return pd.concat(all_frames, ignore_index=True)
    return pd.DataFrame()


def load_stored_jobs(role: str | None = None, db_path: str = DB_PATH) -> pd.DataFrame:
    """Load previously scraped jobs from the database."""
    conn = _ensure_db(db_path)
    query = "SELECT * FROM jobs"
    params: tuple = ()
    if role:
        query += " WHERE search_role = ?"
        params = (role,)
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df
