"""Role matcher module for recommending career pathways and calculating skill gaps."""

import json
from pathlib import Path
from typing import Dict, Any, List, Tuple
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from config import ROLES_FILE, DEFAULT_TOP_N_ROLES


class RoleMatcher:
    def __init__(self, roles_path: Path = ROLES_FILE):
        self.roles_path = roles_path
        self.roles: List[Dict[str, Any]] = []
        self.load_roles()

    def load_roles(self) -> None:
        """Load role definitions from JSON file."""
        if self.roles_path.exists():
            with open(self.roles_path, "r", encoding="utf-8") as f:
                self.roles = json.load(f)
        else:
            self.roles = []

    def match_roles(self, extracted_skills: Dict[str, Any], resume_text: str, top_n: int = DEFAULT_TOP_N_ROLES) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Rank roles against extracted skills and resume content, computing skill gaps and learning priorities."""
        if not self.roles:
            return [], []

        candidate_skills_set = set(extracted_skills.keys())
        results = []

        # Prepare corpus for TF-IDF cosine similarity
        role_texts = [
            f"{r['role']} {r['description']} {' '.join(r.get('required_skills', []))} {' '.join(r.get('optional_skills', []))}"
            for r in self.roles
        ]
        corpus = [resume_text] + role_texts

        vectorizer = TfidfVectorizer(stop_words="english", max_features=1000)
        tfidf_matrix = vectorizer.fit_transform(corpus)
        resume_vec = tfidf_matrix[0:1]
        role_vecs = tfidf_matrix[1:]
        sim_scores = cosine_similarity(resume_vec, role_vecs)[0]

        for idx, role_data in enumerate(self.roles):
            role_name = role_data["role"]
            req_skills = set(role_data.get("required_skills", []))
            opt_skills = set(role_data.get("optional_skills", []))

            # Coverage computations
            matched_req = req_skills.intersection(candidate_skills_set)
            matched_opt = opt_skills.intersection(candidate_skills_set)
            all_matched = matched_req.union(matched_opt)

            req_coverage = len(matched_req) / len(req_skills) if req_skills else 1.0
            opt_coverage = len(matched_opt) / len(opt_skills) if opt_skills else 0.5
            text_sim = float(sim_scores[idx])

            # Formula: 0.6 * req_coverage + 0.2 * opt_coverage + 0.2 * text_sim
            composite_score = (0.6 * req_coverage) + (0.2 * opt_coverage) + (0.2 * text_sim)
            match_percent = round(composite_score * 100, 1)

            missing_req = sorted(list(req_skills - candidate_skills_set))
            missing_opt = sorted(list(opt_skills - candidate_skills_set))

            results.append({
                "role": role_name,
                "description": role_data.get("description", ""),
                "match_percent": match_percent,
                "matched_skills": sorted(list(all_matched)),
                "missing_required": missing_req,
                "missing_optional": missing_opt,
                "required_count": len(req_skills),
                "matched_required_count": len(matched_req),
            })

        # Sort by match_percent descending
        results.sort(key=lambda x: x["match_percent"], reverse=True)
        top_roles = results[:top_n]

        # Calculate learning priorities across top roles
        missing_skills_counter = Counter()
        for r in top_roles:
            for skill in r["missing_required"]:
                missing_skills_counter[skill] += 2  # higher weight for required
            for skill in r["missing_optional"]:
                missing_skills_counter[skill] += 1

        learning_priorities = [
            {"skill": skill, "relevance_count": count}
            for skill, count in missing_skills_counter.most_common(8)
        ]

        return top_roles, learning_priorities

