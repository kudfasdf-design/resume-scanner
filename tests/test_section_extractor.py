"""Unit tests for modules/section_extractor.py"""

from modules.section_extractor import extract_contact_info, extract_sections, match_heading


def test_contact_extraction():
    text = """
    Alex Morgan
    alex.morgan@email.com | +1-555-234-5678 | Bengaluru
    https://linkedin.com/in/alexmorgan
    https://github.com/alexmorgan-dev
    """
    contact = extract_contact_info(text)
    assert contact["email"] == "alex.morgan@email.com"
    assert "555-234-5678" in contact["phone"]
    assert "linkedin.com/in/alexmorgan" in contact["linkedin"]
    assert "github.com/alexmorgan-dev" in contact["github"]
    assert contact["name"] == "Alex Morgan"


def test_heading_matcher():
    assert match_heading("TECHNICAL SKILLS") == "Skills"
    assert match_heading("Professional Summary") == "Summary"
    assert match_heading("Work Experience") == "Experience"
    assert match_heading("Academic Background") == "Education"
    assert match_heading("Key Projects") == "Projects"
    assert match_heading("Licenses & Certifications") == "Certifications"


def test_section_segmentation():
    sample_text = """
    Professional Summary
    Experienced developer passionate about building scalable web apps.

    Technical Skills
    Python, React, Node.js, SQL, Docker

    Work Experience
    Software Engineer at Tech Corp (2022-Present)
    - Developed backend services using FastAPI.

    Education
    B.Tech in Computer Science, 2022
    """
    sections = extract_sections(sample_text)
    assert "Summary" in sections
    assert "Skills" in sections
    assert "Experience" in sections
    assert "Education" in sections
    assert "FastAPI" in sections["Experience"]

