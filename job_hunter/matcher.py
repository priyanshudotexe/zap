"""Text similarity matching between resume and job descriptions using TF-IDF."""

from __future__ import annotations

import logging

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


def compute_similarity(resume_text: str, descriptions: list[str]) -> np.ndarray:
    """Compute cosine similarity between a resume and each job description using TF-IDF."""
    if not descriptions:
        return np.array([])

    all_texts = [resume_text] + descriptions

    vectorizer = TfidfVectorizer(
        max_features=10000,
        stop_words="english",
        ngram_range=(1, 2),
        sublinear_tf=True,
    )
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    resume_vec = tfidf_matrix[0:1]
    job_vecs = tfidf_matrix[1:]

    similarities = cosine_similarity(resume_vec, job_vecs).flatten()
    return similarities
