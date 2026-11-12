"""Orchestrator pipeline that executes parsing, NLP cleaning, taxonomy mapping, scoring, and matching."""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
from modules.parser import extract_text
from modules.cleaner import normalize_text
from modules.section_extractor import extract_contact_info, extract_sections
from modules.skill_extractor import SkillExtractor
from modules.analyzer import analyze_resume_content
from modules.role_matcher import RoleMatcher
from modules.job_matcher import JobMatcher
from modules.gemini_service import GeminiService
from config import DEFAULT_TOP_N_ROLES


@dataclass
class ContactInfo:
    name: str = "Candidate"
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None


@dataclass
class SkillHit:
    category: str
    sources: List[str]
    count: int
    evidenced: bool


@dataclass
class Suggestion:
    section: str
    priority: str
    message: str


@dataclass
class RoleMatch:
    role: str
    description: str
    match_percent: float
    matched_skills: List[str]
    missing_required: List[str]
    missing_optional: List[str]
    required_count: int
    matched_required_count: int


@dataclass
class JobMatch:
    id: str
    title: str
    company: str
    location: str
    job_type: str
    description: str
    required_skills: List[str]
    matched_skills: List[str]
    skill_gap: List[str]
    match_percent: float
    url: str


@dataclass
class AnalysisResult:
    contact: Dict[str, Any]
    sections: Dict[str, str]
    skills: Dict[str, Any]
    overall_score: float
    section_reports: Dict[str, Any]
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[Dict[str, Any]]
    roles: List[Dict[str, Any]]
    jobs: List[Dict[str, Any]]
    learning_priorities: List[Dict[str, Any]]
    target_jd_match: Optional[Dict[str, Any]] = None
    ai_analysis: Optional[Dict[str, Any]] = None
    raw_text: str = ""
    clean_text: str = ""
    word_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contact": self.contact,
            "sections": self.sections,
            "skills": self.skills,
            "overall_score": self.overall_score,
            "section_reports": self.section_reports,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "suggestions": self.suggestions,
            "roles": self.roles,
            "jobs": self.jobs,
            "learning_priorities": self.learning_priorities,
            "target_jd_match": self.target_jd_match,
            "ai_analysis": self.ai_analysis,
            "word_count": self.word_count,
        }


# Singletons for extractor, matchers and AI service
_skill_extractor = SkillExtractor()
_role_matcher = RoleMatcher()
_job_matcher = JobMatcher()
_gemini_service = GeminiService()


def analyze_resume(
    file_bytes: bytes,
    filename: str,
    target_jd: Optional[str] = None,
    location: Optional[str] = None,
    top_n_roles: int = DEFAULT_TOP_N_ROLES,
    enable_ai: bool = True
) -> AnalysisResult:
    """Execute end-to-end resume screening and job recommendation pipeline."""
    # 1. Parse file
    raw_text = extract_text(file_bytes, filename)

    # 2. Clean and normalize
    clean_text = normalize_text(raw_text)

    # 3. Extract contact info and segment sections
    contact = extract_contact_info(clean_text)
    sections = extract_sections(clean_text)

    # 4. Extract canonical skills
    skills = _skill_extractor.extract_skills(clean_text, sections)

    # 5. Analyze content and score
    analysis = analyze_resume_content(sections, contact, skills, clean_text)

    # 6. Recommend roles and compute skill gaps
    roles, learning_priorities = _role_matcher.match_roles(skills, clean_text, top_n=top_n_roles)

    # 7. Match and rank job openings
    role_titles = [r["role"] for r in roles]
    jobs = _job_matcher.rank_jobs(skills, clean_text, role_titles, location=location)

    # 8. Evaluate optional target JD
    target_jd_match = None
    if target_jd and target_jd.strip():
        target_jd_match = _job_matcher.match_target_jd(target_jd, skills, clean_text)

    # 9. Perform deep Gemini AI analysis if enabled
    ai_analysis = None
    if enable_ai and _gemini_service.is_available():
        top_role_name = roles[0]["role"] if roles else "Software Engineer"
        try:
            ai_analysis = _gemini_service.analyze_resume_ai(
                clean_text, list(skills.keys()), top_role=top_role_name
            )
        except Exception:
            pass

    word_count = len(clean_text.split())

    return AnalysisResult(
        contact=contact,
        sections=sections,
        skills=skills,
        overall_score=analysis["overall_score"],
        section_reports=analysis["section_reports"],
        strengths=analysis["strengths"],
        weaknesses=analysis["weaknesses"],
        suggestions=analysis["suggestions"],
        roles=roles,
        jobs=jobs,
        learning_priorities=learning_priorities,
        target_jd_match=target_jd_match,
        ai_analysis=ai_analysis,
        raw_text=raw_text,
        clean_text=clean_text,
        word_count=word_count,
    )

