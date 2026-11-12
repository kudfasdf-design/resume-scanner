"""Unit tests for modules/analyzer.py"""

from modules.analyzer import analyze_resume_content, evaluate_contact, evaluate_skills


def test_evaluate_contact():
    full_contact = {
        "email": "test@example.com",
        "phone": "+91 9876543210",
        "linkedin": "https://linkedin.com/in/test",
        "github": "https://github.com/test"
    }
    report = evaluate_contact(full_contact)
    assert report["score"] == 100
    assert len(report["suggestions"]) == 0

    empty_contact = {"email": None, "phone": None, "linkedin": None, "github": None}
    empty_report = evaluate_contact(empty_contact)
    assert empty_report["score"] == 0
    assert len(empty_report["suggestions"]) >= 2


def test_analyze_resume_content_scoring_bounds():
    sections = {
        "Summary": "Experienced software developer seeking full stack roles with expertise in Python.",
        "Skills": "Python, React, SQL, Docker, AWS, Git, Node.js, Linux",
        "Experience": "Senior Developer (2022-2024)\n- Architected microservices and reduced latency by 35%.\n- Optimized SQL queries.",
        "Projects": "Project Alpha (Tech: React, Python)\n- Built interactive UI with 99.9% uptime for 50k users.",
        "Education": "B.Tech in Computer Science, 2022, CGPA: 8.5",
        "Certifications": "AWS Certified Developer (2023)"
    }
    contact = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "phone": "+1 555 123 4567",
        "linkedin": "linkedin.com/in/janedoe",
        "github": "github.com/janedoe"
    }
    skills = {
        "Python": {"category": "Programming Languages", "evidenced": True, "count": 2, "sources": ["Experience", "Projects"]},
        "React": {"category": "Web", "evidenced": True, "count": 1, "sources": ["Projects"]},
        "SQL": {"category": "Programming Languages", "evidenced": True, "count": 1, "sources": ["Experience"]},
        "Docker": {"category": "Cloud/DevOps", "evidenced": False, "count": 1, "sources": ["Skills"]},
        "AWS": {"category": "Cloud/DevOps", "evidenced": False, "count": 1, "sources": ["Skills"]},
        "Git": {"category": "Tools", "evidenced": False, "count": 1, "sources": ["Skills"]},
        "Node.js": {"category": "Web", "evidenced": False, "count": 1, "sources": ["Skills"]},
        "Linux": {"category": "Cloud/DevOps", "evidenced": False, "count": 1, "sources": ["Skills"]}
    }
    full_text = "Jane Doe\n" + "\n".join(sections.values())

    result = analyze_resume_content(sections, contact, skills, full_text)
    assert 0 <= result["overall_score"] <= 100
    assert result["overall_score"] >= 75  # Strong resume should score high
    assert len(result["strengths"]) > 0

