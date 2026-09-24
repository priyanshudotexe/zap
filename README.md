# Zap Job Hunter

Scrapes job postings from LinkedIn, Indeed, Glassdoor, and ZipRecruiter, then ranks them against your resume using semantic similarity.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

Drop your resume PDF into the `resumes/` folder, then:

```bash
# Search for Product Management jobs
python -m job_hunter search --resume resumes/my_resume.pdf --role pm

# Search for Venture Capital jobs
python -m job_hunter search --resume resumes/my_resume.pdf --role vc

# Remote-only jobs
python -m job_hunter search --resume resumes/my_resume.pdf --role pm --remote

# Specific location
python -m job_hunter search --resume resumes/my_resume.pdf --role vc --location "San Francisco"

# Export to CSV
python -m job_hunter search --resume resumes/my_resume.pdf --role pm --export-csv my_jobs.csv

# Re-rank stored jobs with an updated resume
python -m job_hunter rerank --resume resumes/updated_resume.pdf --role pm

# List available role profiles
python -m job_hunter roles
```

## How It Works

1. **Scrape** — Uses [python-jobspy](https://github.com/speedyapply/JobSpy) to pull job listings from multiple boards
2. **Parse** — Extracts text from your PDF resume using pdfplumber
3. **Match** — Compares your resume against each job description using TF-IDF vectorization (bigrams, sublinear TF)
4. **Rank** — Scores jobs by cosine similarity plus title-relevance bonuses
5. **Output** — Displays a ranked table and saves results to CSV/JSON

## Scoring Tiers

| Tier | Score | Meaning |
|------|-------|---------|
| Strong Match | >= 0.20 | Your resume aligns well with this job |
| Worth Applying | >= 0.10 | Reasonable fit, worth a look |
| Stretch | < 0.10 | Looser match, may need to tailor resume |

## Project Structure

```
job_hunter/
├── cli.py            # CLI entry point (click)
├── config.py         # Role profiles, search keywords, settings
├── scraper.py        # Job scraping via python-jobspy
├── resume_parser.py  # PDF text extraction
├── matcher.py        # Sentence-BERT embeddings + cosine similarity
├── ranker.py         # Scoring and ranking logic
└── export.py         # CSV, JSON, and terminal table output
```

## Notes

- LinkedIn rate-limits aggressively (~10 pages per IP). Use proxies or stick to Indeed/Glassdoor for higher volume.
- Scraped jobs are cached in `output/jobs.db` (SQLite) to avoid redundant scraping.
- The `rerank` command lets you re-score stored jobs after updating your resume without re-scraping.
