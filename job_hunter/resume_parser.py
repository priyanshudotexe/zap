"""Extract text and structured data from a PDF resume."""

from pathlib import Path

import pymupdf


def extract_text(pdf_path: str | Path) -> str:
    """Return the full plain-text content of a PDF resume."""
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"Resume not found: {pdf_path}")

    doc = pymupdf.open(str(pdf_path))
    pages = []
    for page in doc:
        text = page.get_text()
        if text:
            pages.append(text)
    doc.close()

    full_text = "\n".join(pages).strip()
    if not full_text:
        raise ValueError(f"No text could be extracted from {pdf_path}")
    return full_text


def extract_skills_section(resume_text: str) -> str:
    """Try to pull out a skills section if one exists, else return full text."""
    lines = resume_text.split("\n")
    capture = False
    skills_lines: list[str] = []
    for line in lines:
        lower = line.strip().lower()
        if any(
            heading in lower
            for heading in ["skills", "technical skills", "core competencies", "tools"]
        ):
            capture = True
            continue
        if capture:
            if line.strip() == "" and skills_lines:
                break
            if any(
                heading in lower
                for heading in [
                    "experience",
                    "education",
                    "projects",
                    "certifications",
                    "awards",
                ]
            ):
                break
            skills_lines.append(line.strip())

    return "\n".join(skills_lines) if skills_lines else resume_text
