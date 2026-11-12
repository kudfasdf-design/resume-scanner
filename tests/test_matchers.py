"""Unit tests for modules/role_matcher.py and modules/job_matcher.py"""

from modules.role_matcher import RoleMatcher
from modules.job_matcher import JobMatcher


def test_role_matcher():
    matcher = RoleMatcher()
    candidate_skills = {
        "Python": {"category": "Programming Languages"},
        "React": {"category": "Web"},
        "JavaScript": {"category": "Programming Languages"},
        "Node.js": {"category": "Web"},
        "SQL": {"category": "Programming Languages"},
        "Git": {"category": "Tools"},
        "REST API": {"category": "Web"},
        "HTML": {"category": "Web"},
        "CSS": {"category": "Web"},
    }
    resume_text = "Full stack engineer experienced in React, Node.js, Python, SQL, REST APIs and Git."

    roles, priorities = matcher.match_roles(candidate_skills, resume_text, top_n=3)
    assert len(roles) == 3
    # Full Stack Developer should rank near or at the top
    top_role_names = [r["role"] for r in roles]
    assert "Full Stack Developer" in top_role_names
    assert roles[0]["match_percent"] > 50


def test_job_matcher():
    matcher = JobMatcher()
    candidate_skills = {
        "React": {"category": "Web"},
        "Node.js": {"category": "Web"},
        "JavaScript": {"category": "Programming Languages"},
        "SQL": {"category": "Programming Languages"}
    }
    resume_text = "Developer with React, Node.js, SQL experience."

    jobs = matcher.rank_jobs(candidate_skills, resume_text, ["Full Stack Developer"])
    assert len(jobs) > 0
    assert jobs[0]["match_percent"] > 0
    assert "matched_skills" in jobs[0]
    assert "skill_gap" in jobs[0]


def test_target_jd_matching():
    matcher = JobMatcher()
    candidate_skills = {"Python": {}, "FastAPI": {}, "Docker": {}}
    resume_text = "Backend Python developer using FastAPI and Docker."
    target_jd = "Looking for a Python Backend Engineer with FastAPI, Docker, and AWS."

    res = matcher.match_target_jd(target_jd, candidate_skills, resume_text)
    assert res["match_percent"] > 0
    assert "Python" in res["matched_skills"]
    assert "FastAPI" in res["matched_skills"]

