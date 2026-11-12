"""Job matcher module for ranking job openings and evaluating target job descriptions."""

from typing import Dict, Any, List, Optional
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from modules.job_providers import Job, JobProvider, LocalJobProvider, AdzunaJobProvider, RealtimeJobProvider
from config import JOB_PROVIDER


class JobMatcher:
    def __init__(self, provider: Optional[JobProvider] = None):
        if provider:
            self.provider = provider
        elif JOB_PROVIDER == "adzuna":
            self.provider = AdzunaJobProvider()
        elif JOB_PROVIDER == "realtime":
            self.provider = RealtimeJobProvider()
        else:
            self.provider = RealtimeJobProvider()

    def rank_jobs(
        self,
        candidate_skills: Dict[str, Any],
        resume_text: str,
        role_keywords: List[str],
        location: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Fetch candidate jobs, compute cosine similarity and skill coverage, and return ranked matches."""
        jobs = self.provider.search(role_keywords, location=location)
        if not jobs:
            return []

        candidate_skills_set = set(candidate_skills.keys())

        # Build TF-IDF matrix for similarity
        job_texts = [f"{j.title} {j.description} {' '.join(j.required_skills)}" for j in jobs]
        corpus = [resume_text] + job_texts

        vectorizer = TfidfVectorizer(stop_words="english", max_features=1000)
        tfidf_matrix = vectorizer.fit_transform(corpus)
        resume_vec = tfidf_matrix[0:1]
        job_vecs = tfidf_matrix[1:]
        sim_scores = cosine_similarity(resume_vec, job_vecs)[0]

        ranked = []
        for idx, job in enumerate(jobs):
            req_set = set(job.required_skills)
            matched = req_set.intersection(candidate_skills_set)
            skill_gap = sorted(list(req_set - candidate_skills_set))

            skill_coverage = len(matched) / len(req_set) if req_set else 0.8
            text_sim = float(sim_scores[idx])

            # Formula: 0.6 * skill_coverage + 0.4 * text_sim
            composite_score = (0.6 * skill_coverage) + (0.4 * text_sim)
            match_percent = round(composite_score * 100, 1)

            ranked.append({
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "job_type": job.job_type,
                "description": job.description,
                "required_skills": job.required_skills,
                "matched_skills": sorted(list(matched)),
                "skill_gap": skill_gap,
                "match_percent": match_percent,
                "url": job.url,
                "is_live": getattr(job, "is_live", False),
            })

        ranked.sort(key=lambda x: x["match_percent"], reverse=True)
        return ranked

    def match_target_jd(self, target_jd_text: str, candidate_skills: Dict[str, Any], resume_text: str) -> Dict[str, Any]:
        """Score resume against a custom user-pasted job description."""
        if not target_jd_text.strip():
            return {}

        candidate_skills_set = set(candidate_skills.keys())

        # Extract potential required skills mentioned in JD
        corpus = [resume_text, target_jd_text]
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(corpus)
        text_sim = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0])

        # Find which of the candidate skills appear in target JD
        target_lower = target_jd_text.lower()
        matched_in_jd = [s for s in candidate_skills_set if s.lower() in target_lower]

        match_percent = round(min(100.0, (text_sim * 0.7 + (len(matched_in_jd) / max(1, len(candidate_skills_set)) * 0.3)) * 100), 1)

        return {
            "title": "Custom Target Job Description",
            "match_percent": match_percent,
            "text_similarity": round(text_sim * 100, 1),
            "matched_skills": sorted(matched_in_jd),
            "jd_word_count": len(target_jd_text.split()),
        }

