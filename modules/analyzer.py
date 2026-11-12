"""Analyzer module for section evaluation, scoring, action verb analysis, and suggestion generation."""

import re
from typing import Dict, Any, List
from config import SECTION_WEIGHTS

STRONG_ACTION_VERBS = {
    "built", "developed", "architected", "engineered", "implemented", "designed",
    "optimized", "spearheaded", "accelerated", "scaled", "streamlined", "automated",
    "reduced", "increased", "generated", "created", "launched", "deployed", "orchestrated",
    "refactored", "migrated", "collaborated", "mentored", "achieved"
}

WEAK_PHRASES = [
    "responsible for", "worked on", "helped with", "assisted in", "duties included",
    "tasked with", "handled"
]

METRIC_REGEX = re.compile(r"\b\d+(?:\.\d+)?%|\b\d+x\b|[\$₹€£]\s?\d+(?:,\d+)*(?:\.\d+)?(?:k|m|b|lakh|cr)?|\b\d+(?:,\d+)*(?:\+)?\s*(?:users|clients|requests|ms|sec|hours|days|percent)\b", re.IGNORECASE)
YEAR_REGEX = re.compile(r"\b(19\d\d|20\d\d)\b")
DEGREE_REGEX = re.compile(r"\b(b\.?tech|b\.?e\.?|b\.?s\.?|bachelor|m\.?tech|m\.?s\.?|master|ph\.?d|diploma)\b", re.IGNORECASE)
GPA_REGEX = re.compile(r"\b(?:cgpa|gpa|percentage|%)\s*(?::|=|\s)?\s*([0-9]+(?:\.[0-9]+)?)\b", re.IGNORECASE)


def evaluate_contact(contact: Dict[str, Any]) -> Dict[str, Any]:
    score = 0
    findings = []
    suggestions = []

    if contact.get("email"):
        score += 35
        findings.append("Valid email address detected.")
    else:
        suggestions.append({"priority": "High", "message": "Add a professional email address to the contact section."})

    if contact.get("phone"):
        score += 25
        findings.append("Contact telephone number found.")
    else:
        suggestions.append({"priority": "High", "message": "Include your phone number so recruiters can reach you."})

    links = 0
    if contact.get("linkedin"):
        links += 1
        findings.append("LinkedIn profile link included.")
    if contact.get("github"):
        links += 1
        findings.append("GitHub repository profile included.")

    if links == 2:
        score += 40
    elif links == 1:
        score += 25
        if not contact.get("github"):
            suggestions.append({"priority": "Medium", "message": "Add your GitHub profile link to showcase technical code."})
        if not contact.get("linkedin"):
            suggestions.append({"priority": "Medium", "message": "Add your LinkedIn profile link to verify your career presence."})
    else:
        suggestions.append({"priority": "High", "message": "Add active links to your LinkedIn and GitHub profiles."})

    return {"score": min(100, score), "findings": findings, "suggestions": suggestions}


def evaluate_summary(text: str) -> Dict[str, Any]:
    if not text:
        return {
            "score": 0,
            "findings": ["No professional summary or objective section detected."],
            "suggestions": [{"priority": "Medium", "message": "Add a 2-4 sentence professional summary highlighting your core skills and career target."}]
        }

    words = text.split()
    word_count = len(words)
    score = 40
    findings = []
    suggestions = []

    if 30 <= word_count <= 120:
        score += 40
        findings.append(f"Summary length is optimal ({word_count} words).")
    elif word_count < 30:
        score += 20
        suggestions.append({"priority": "Medium", "message": "Summary is very short. Expand to 2-4 lines describing your focus areas and strengths."})
    else:
        score += 20
        suggestions.append({"priority": "Low", "message": "Summary is somewhat long. Condense to under 100 words for recruiter scannability."})

    # Check for target role or action keywords
    lower = text.lower()
    if any(k in lower for k in ["engineer", "developer", "analyst", "scientist", "specialist", "passionate", "seeking"]):
        score += 20
        findings.append("Summary mentions target career direction or role keywords.")
    else:
        suggestions.append({"priority": "Medium", "message": "Mention your specific target role (e.g. 'Software Engineer' or 'Data Analyst') in your summary."})

    return {"score": min(100, score), "findings": findings, "suggestions": suggestions}


def evaluate_skills(skills: Dict[str, Any]) -> Dict[str, Any]:
    count = len(skills)
    findings = []
    suggestions = []
    score = 0

    if count == 0:
        return {
            "score": 0,
            "findings": ["No technical skills could be extracted."],
            "suggestions": [{"priority": "High", "message": "Add a dedicated Skills section with specific technical tools, languages, and frameworks."}]
        }

    # Count categories
    categories = {v["category"] for v in skills.values()}
    evidenced_count = sum(1 for v in skills.values() if v.get("evidenced", False))

    if count >= 10:
        score += 40
        findings.append(f"Strong skill breadth: {count} technical competencies extracted.")
    elif count >= 6:
        score += 30
        findings.append(f"Moderate skill count: {count} skills detected.")
        suggestions.append({"priority": "Medium", "message": "Consider adding more technical proficiencies relevant to your target role."})
    else:
        score += 15
        suggestions.append({"priority": "High", "message": f"Only {count} skills detected. Include at least 8-12 core tools and frameworks."})

    if len(categories) >= 3:
        score += 30
        findings.append(f"Well-rounded skillset across {len(categories)} domains ({', '.join(sorted(categories)[:3])}).")
    else:
        score += 15
        suggestions.append({"priority": "Medium", "message": "Diversify your skills to cover languages, frameworks, databases, and development tools."})

    if evidenced_count >= 3:
        score += 30
        findings.append(f"{evidenced_count} skills are evidenced directly in your Projects and Work Experience.")
    else:
        score += 10
        suggestions.append({"priority": "High", "message": "Demonstrate your skills by explicitly naming the tech stack used inside your Project bullets."})

    return {"score": min(100, score), "findings": findings, "suggestions": suggestions}


def evaluate_experience(text: str, is_fresher: bool = False) -> Dict[str, Any]:
    if not text:
        if is_fresher:
            return {
                "score": 60,
                "findings": ["No formal work experience detected (acceptable for entry-level / fresher)."],
                "suggestions": [{"priority": "Low", "message": "If you have completed internships, freelance gigs, or campus leadership roles, add them under Experience."}]
            }
        return {
            "score": 20,
            "findings": ["No work experience or internship section detected."],
            "suggestions": [{"priority": "High", "message": "Add an Experience section detailing internships, full-time roles, or client work."}]
        }

    score = 30
    findings = ["Work experience / internship section is present."]
    suggestions = []

    # Dates present
    if YEAR_REGEX.search(text):
        score += 20
        findings.append("Timeline dates detected.")
    else:
        suggestions.append({"priority": "Medium", "message": "Include employment start and end dates (e.g. 'Jun 2023 - Present') for each role."})

    # Action verbs
    words = text.lower().split()
    matched_verbs = STRONG_ACTION_VERBS.intersection(set(words))
    if len(matched_verbs) >= 3:
        score += 25
        findings.append(f"Strong action verbs used ({', '.join(sorted(list(matched_verbs))[:4])}).")
    else:
        score += 10
        suggestions.append({"priority": "Medium", "message": "Start bullet points with strong action verbs (e.g. 'Architected', 'Optimized', 'Deployed') instead of passive phrasing."})

    # Weak phrasing check
    lower = text.lower()
    found_weak = [p for p in WEAK_PHRASES if p in lower]
    if found_weak:
        suggestions.append({"priority": "Low", "message": f"Replace weak phrases like '{found_weak[0]}' with impact-oriented verbs."})

    # Quantified metrics
    metrics = METRIC_REGEX.findall(text)
    if metrics:
        score += 25
        findings.append(f"Measurable achievements detected ({len(metrics)} quantitative metric instances).")
    else:
        suggestions.append({"priority": "High", "message": "Quantify your achievements with numbers, percentages, or scale (e.g., 'Reduced load time by 30%', 'Served 10k users')."})

    return {"score": min(100, score), "findings": findings, "suggestions": suggestions}


def evaluate_projects(text: str) -> Dict[str, Any]:
    if not text:
        return {
            "score": 0,
            "findings": ["No projects section detected."],
            "suggestions": [{"priority": "High", "message": "Add at least 2 significant projects with tech stacks and measurable outcomes."}]
        }

    score = 35
    findings = ["Projects section detected."]
    suggestions = []

    # Count bullet points / project blocks
    bullets = [line.strip() for line in text.splitlines() if line.strip().startswith("-") or line.strip().startswith("•")]
    line_count = len([line for line in text.splitlines() if line.strip()])

    if len(bullets) >= 4 or line_count >= 8:
        score += 25
        findings.append("Good project detail with multiple bullet points.")
    else:
        score += 10
        suggestions.append({"priority": "Medium", "message": "Detail your projects using 2-4 bullet points per project."})

    # Metrics check
    metrics = METRIC_REGEX.findall(text)
    if metrics:
        score += 20
        findings.append("Projects include quantitative results and metrics.")
    else:
        suggestions.append({"priority": "Medium", "message": "Include measurable results in projects (e.g. 'achieved 95% accuracy', 'reduced API response by 120ms')."})

    # Tech stack mention
    lower = text.lower()
    if any(k in lower for k in ["built with", "tech stack", "technologies", "tools used", "using"]):
        score += 20
        findings.append("Project descriptions explicitly state the technology stack.")
    else:
        score += 10
        suggestions.append({"priority": "Low", "message": "Explicitly mention the tech stack (e.g. 'Tech: React, FastAPI, Docker') for each project."})

    return {"score": min(100, score), "findings": findings, "suggestions": suggestions}


def evaluate_education(text: str) -> Dict[str, Any]:
    if not text:
        return {
            "score": 0,
            "findings": ["No education section detected."],
            "suggestions": [{"priority": "High", "message": "Add your Education background with degree, institution, and graduation year."}]
        }

    score = 40
    findings = ["Education section is present."]
    suggestions = []

    if DEGREE_REGEX.search(text):
        score += 20
        findings.append("Degree name or academic qualification detected.")
    else:
        suggestions.append({"priority": "Medium", "message": "Specify your exact degree (e.g., B.Tech in Computer Science, B.S., M.S.)."})

    if YEAR_REGEX.search(text):
        score += 20
        findings.append("Graduation year or dates detected.")
    else:
        suggestions.append({"priority": "Medium", "message": "Add your graduation year or expected completion date."})

    if GPA_REGEX.search(text):
        score += 20
        findings.append("GPA, CGPA, or academic percentage included.")
    else:
        score += 10
        suggestions.append({"priority": "Low", "message": "Consider adding your CGPA/percentage if it is strong (above 7.5 CGPA or 70%)."})

    return {"score": min(100, score), "findings": findings, "suggestions": suggestions}


def evaluate_certifications(text: str) -> Dict[str, Any]:
    if not text:
        return {
            "score": 40,
            "findings": ["No certifications section detected."],
            "suggestions": [{"priority": "Low", "message": "Add recognized online certifications (e.g. AWS, Coursera, Meta, Google) to validate your skills."}]
        }

    score = 75
    findings = ["Certifications section present."]
    suggestions = []

    if YEAR_REGEX.search(text):
        score += 25
        findings.append("Certification completion dates detected.")
    else:
        score += 10
        suggestions.append({"priority": "Low", "message": "Include the issue year or credential ID for your certifications."})

    return {"score": min(100, score), "findings": findings, "suggestions": suggestions}


def evaluate_formatting(text: str) -> Dict[str, Any]:
    words = text.split()
    word_count = len(words)
    score = 50
    findings = []
    suggestions = []

    if 350 <= word_count <= 900:
        score += 30
        findings.append(f"Resume word count is in the ideal range ({word_count} words).")
    elif word_count < 350:
        score += 10
        suggestions.append({"priority": "Medium", "message": f"Resume is quite brief ({word_count} words). Expand on your projects, skills, and coursework."})
    else:
        score += 10
        suggestions.append({"priority": "Medium", "message": f"Resume is long ({word_count} words). Keep it concise and within 1-2 pages."})

    bullet_count = text.count("\n-") + text.count("\n•")
    if bullet_count >= 6:
        score += 20
        findings.append(f"Consistent bullet structure detected ({bullet_count} bullet points).")
    else:
        score += 5
        suggestions.append({"priority": "Medium", "message": "Use bullet points rather than paragraphs for better ATS parsing and visual scannability."})

    return {"score": min(100, score), "findings": findings, "suggestions": suggestions}


def analyze_resume_content(sections: Dict[str, str], contact: Dict[str, Any], skills: Dict[str, Any], full_text: str) -> Dict[str, Any]:
    """Perform comprehensive section analysis, compute weighted ATS scores, and generate findings."""
    is_fresher = ("Experience" not in sections or len(sections.get("Experience", "").split()) < 30)

    section_reports = {
        "contact": evaluate_contact(contact),
        "summary": evaluate_summary(sections.get("Summary", "")),
        "skills": evaluate_skills(skills),
        "experience": evaluate_experience(sections.get("Experience", ""), is_fresher=is_fresher),
        "projects": evaluate_projects(sections.get("Projects", "")),
        "education": evaluate_education(sections.get("Education", "")),
        "certifications": evaluate_certifications(sections.get("Certifications", "")),
        "formatting": evaluate_formatting(full_text),
    }

    # Calculate weighted overall score
    overall_score = 0.0
    for key, weight in SECTION_WEIGHTS.items():
        sec_score = section_reports[key]["score"]
        overall_score += (sec_score * weight) / 100.0

    overall_score = round(min(100.0, max(0.0, overall_score)), 1)

    # Compile strengths, weaknesses, and suggestions
    strengths = []
    weaknesses = []
    all_suggestions = []

    for sec_key, report in section_reports.items():
        sec_name = sec_key.capitalize()
        sec_score = report["score"]

        if sec_score >= 75:
            for f in report["findings"][:2]:
                strengths.append(f"**{sec_name}**: {f}")
        elif sec_score < 50:
            for f in report["findings"][:2]:
                weaknesses.append(f"**{sec_name}**: {f}")

        for s in report["suggestions"]:
            all_suggestions.append({
                "section": sec_name,
                "priority": s["priority"],
                "message": s["message"]
            })

    # Sort suggestions: High first, then Medium, then Low
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    all_suggestions.sort(key=lambda s: priority_order.get(s["priority"], 3))

    return {
        "overall_score": overall_score,
        "section_reports": section_reports,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestions": all_suggestions
    }

