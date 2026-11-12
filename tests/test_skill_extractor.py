"""Unit tests for modules/skill_extractor.py"""

from modules.skill_extractor import SkillExtractor


def test_skill_extraction_and_alias():
    extractor = SkillExtractor()
    text = "We built a web service using Python, JS, React, and postgresql database hosted on AWS."
    sections = {
        "Projects": "Built a system using Python and React.",
        "Skills": "JS, PostgreSQL, AWS"
    }

    skills = extractor.extract_skills(text, sections)

    assert "Python" in skills
    assert "React" in skills
    assert "JavaScript" in skills  # mapped from 'JS' alias
    assert "PostgreSQL" in skills
    assert "AWS" in skills

    # Check source tracking
    assert "Projects" in skills["Python"]["sources"]
    assert skills["Python"]["evidenced"] is True

