"""Search profiles and configuration for job hunting."""

ROLE_PROFILES = {
    "pm": {
        "name": "Product Management",
        "keywords": [
            "product manager",
            "senior product manager",
            "product lead",
            "head of product",
            "director of product",
            "group product manager",
            "principal product manager",
            "product owner",
            "technical product manager",
            "AI product manager",
        ],
        "title_boost": [
            "product manager",
            "product lead",
            "head of product",
            "director of product",
        ],
    },
    "vc": {
        "name": "Venture Capital",
        "keywords": [
            "venture capital analyst",
            "VC associate",
            "venture associate",
            "investment analyst",
            "venture partner",
            "principal venture capital",
            "investor relations",
            "venture capital associate",
            "portfolio analyst",
            "startup investor",
        ],
        "title_boost": [
            "venture",
            "vc",
            "investment",
            "analyst",
            "associate",
            "partner",
        ],
    },
}

DEFAULT_LOCATIONS = ["United States", "Remote"]

SEARCH_SITES = ["linkedin", "indeed", "glassdoor", "zip_recruiter"]

RESULTS_PER_KEYWORD = 25

DB_PATH = "output/jobs.db"
