"""Score and rank jobs by relevance to a resume."""

from __future__ import annotations

import logging
from dataclasses import dataclass

import pandas as pd

from .config import ROLE_PROFILES
from .matcher import compute_similarity

logger = logging.getLogger(__name__)


@dataclass
class ScoredJob:
    title: str
    company: str
    location: str
    job_url: str
    score: float
    tier: str
    date_posted: str
    site: str
    description_preview: str


def _title_boost(title: str, role: str) -> float:
    """Give a small bonus when the job title closely matches the target role."""
    profile = ROLE_PROFILES.get(role, {})
    boost_terms = profile.get("title_boost", [])
    title_lower = title.lower()
    for term in boost_terms:
        if term.lower() in title_lower:
            return 0.05
    return 0.0


def _tier(score: float) -> str:
    if score >= 0.20:
        return "Strong Match"
    if score >= 0.10:
        return "Worth Applying"
    return "Stretch"


def rank_jobs(
    resume_text: str,
    jobs_df: pd.DataFrame,
    role: str,
    top_n: int = 50,
) -> list[ScoredJob]:
    """Rank jobs by semantic similarity to the resume plus title bonuses."""
    if jobs_df.empty:
        return []

    jobs_df = jobs_df.copy()
    jobs_df["description"] = jobs_df["description"].fillna("").astype(str)
    jobs_df = jobs_df[jobs_df["description"].str.len() > 20]

    if jobs_df.empty:
        return []

    descriptions = jobs_df["description"].tolist()
    logger.info(f"Computing similarity for {len(descriptions)} jobs...")
    similarities = compute_similarity(resume_text, descriptions)

    results: list[ScoredJob] = []
    for i, (_, row) in enumerate(jobs_df.iterrows()):
        base_score = float(similarities[i])
        boost = _title_boost(str(row.get("title", "")), role)
        final_score = min(base_score + boost, 1.0)

        desc = str(row.get("description", ""))
        preview = desc[:200].replace("\n", " ") + ("..." if len(desc) > 200 else "")

        results.append(
            ScoredJob(
                title=str(row.get("title", "Unknown")),
                company=str(row.get("company", "Unknown")),
                location=str(row.get("location", "")),
                job_url=str(row.get("job_url", "")),
                score=round(final_score, 4),
                tier=_tier(final_score),
                date_posted=str(row.get("date_posted", "")),
                site=str(row.get("site", "")),
                description_preview=preview,
            )
        )

    results.sort(key=lambda j: j.score, reverse=True)
    return results[:top_n]
