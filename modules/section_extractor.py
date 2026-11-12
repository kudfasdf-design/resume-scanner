"""Section extractor module for segmenting resume sections and extracting contact info."""

import re
from typing import Dict, Any, List, Optional
from rapidfuzz import fuzz
from config import FUZZY_HEADING_THRESHOLD

# Canonical section names and their common synonyms
SECTION_SYNONYMS = {
    "Summary": [
        "summary", "professional summary", "career summary", "executive summary",
        "objective", "career objective", "profile", "professional profile", "about me"
    ],
    "Skills": [
        "skills", "technical skills", "core competencies", "technical competencies",
        "technologies", "tools & technologies", "technical expertise", "skills & tools",
        "key skills", "proficiencies", "areas of expertise"
    ],
    "Experience": [
        "experience", "work experience", "professional experience", "employment history",
        "work history", "internships", "internship experience", "industry experience",
        "relevant experience"
    ],
    "Projects": [
        "projects", "academic projects", "personal projects", "key projects",
        "technical projects", "selected projects", "notable projects"
    ],
    "Education": [
        "education", "academic background", "academics", "qualifications",
        "academic qualifications", "educational background", "academic credentials",
        "degrees"
    ],
    "Certifications": [
        "certifications", "certificates", "licenses", "licenses & certifications",
        "certifications & licenses", "courses", "professional credentials",
        "accreditations"
    ]
}

# Regex patterns for contact information
EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")
PHONE_REGEX = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b|\b(?:\+91[-\s]?)?[6-9]\d{9}\b")
LINKEDIN_REGEX = re.compile(r"(?:https?://)?(?:www\.)?linkedin\.com/(?:in|profile)/[A-Za-z0-9_-]+", re.IGNORECASE)
GITHUB_REGEX = re.compile(r"(?:https?://)?(?:www\.)?github\.com/[A-Za-z0-9_-]+", re.IGNORECASE)


def extract_contact_info(text: str) -> Dict[str, Optional[str]]:
    """Extract candidate name candidate, email, phone, LinkedIn, and GitHub."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # Guess candidate name from the top non-contact, non-header lines
    name_guess = None
    for line in lines[:5]:
        # Skip lines that look like email, phone, url, or section headers
        if (EMAIL_REGEX.search(line) or PHONE_REGEX.search(line) or
            "linkedin.com" in line.lower() or "github.com" in line.lower() or
            len(line) > 50 or is_potential_heading(line)):
            continue
        # Clean potential title or symbols from name
        clean_name = re.sub(r"[^A-Za-z\s.'-]", "", line).strip()
        if 2 <= len(clean_name.split()) <= 4:
            name_guess = clean_name
            break

    if not name_guess and lines:
        name_guess = lines[0][:40]

    email_match = EMAIL_REGEX.search(text)
    phone_match = PHONE_REGEX.search(text)
    linkedin_match = LINKEDIN_REGEX.search(text)
    github_match = GITHUB_REGEX.search(text)

    return {
        "name": name_guess or "Candidate",
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0) if phone_match else None,
        "linkedin": linkedin_match.group(0) if linkedin_match else None,
        "github": github_match.group(0) if github_match else None,
    }


def is_potential_heading(line: str) -> bool:
    """Heuristic check whether a line could be a section header."""
    line_clean = line.strip(" :-\t#*").strip()
    if not line_clean or len(line_clean) > 40:
        return False
    # Check if mostly alphanumeric and short
    words = line_clean.split()
    return len(words) <= 5


def match_heading(line: str) -> Optional[str]:
    """Match line against canonical section names using fuzzy matching."""
    cleaned = line.strip(" :-\t#*").lower()
    if not cleaned or len(cleaned) > 40:
        return None

    best_match = None
    highest_score = 0

    for canonical, synonyms in SECTION_SYNONYMS.items():
        for syn in synonyms:
            # Exact match
            if cleaned == syn:
                return canonical
            # Partial/ratio match
            score = fuzz.ratio(cleaned, syn)
            if score > highest_score and score >= FUZZY_HEADING_THRESHOLD:
                highest_score = score
                best_match = canonical

    return best_match


def extract_sections(text: str) -> Dict[str, str]:
    """Segment resume text into canonical sections using heading detection with keyword fallback."""
    lines = text.splitlines()
    sections: Dict[str, List[str]] = {canonical: [] for canonical in SECTION_SYNONYMS}
    sections["Uncategorized"] = []

    current_section = "Uncategorized"

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        matched_section = match_heading(stripped)
        if matched_section:
            current_section = matched_section
        else:
            sections[current_section].append(stripped)

    # Flatten list of lines to strings
    result: Dict[str, str] = {
        name: "\n".join(content_lines).strip()
        for name, content_lines in sections.items()
        if content_lines
    }

    # If all sections ended up in Uncategorized, apply fallback keyword heuristic
    if len(result) <= 1 and "Uncategorized" in result:
        result = fallback_keyword_segmentation(text)

    return result


def fallback_keyword_segmentation(text: str) -> Dict[str, str]:
    """Fallback segmenter that groups lines by keywords if explicit headings were absent."""
    lines = text.splitlines()
    sections: Dict[str, List[str]] = {
        "Summary": [],
        "Skills": [],
        "Education": [],
        "Projects": [],
        "Experience": [],
        "Certifications": [],
        "Uncategorized": []
    }

    edu_keywords = {"university", "college", "institute", "b.tech", "b.e", "bachelor", "master", "m.tech", "gpa", "cgpa", "degree"}
    exp_keywords = {"responsible for", "developed", "worked", "intern", "engineer", "lead", "team", "client", "company"}
    proj_keywords = {"project", "github.com", "built", "implemented", "application", "system"}
    skill_keywords = {"python", "java", "sql", "html", "css", "javascript", "react", "docker", "aws"}
    cert_keywords = {"certified", "certification", "credential", "coursera", "udemy", "aws certified"}

    for line in lines:
        lower = line.lower()
        if any(k in lower for k in cert_keywords):
            sections["Certifications"].append(line)
        elif any(k in lower for k in edu_keywords):
            sections["Education"].append(line)
        elif any(k in lower for k in skill_keywords) and len(line.split()) < 15:
            sections["Skills"].append(line)
        elif any(k in lower for k in proj_keywords):
            sections["Projects"].append(line)
        elif any(k in lower for k in exp_keywords):
            sections["Experience"].append(line)
        else:
            sections["Uncategorized"].append(line)

    return {k: "\n".join(v).strip() for k, v in sections.items() if v}

