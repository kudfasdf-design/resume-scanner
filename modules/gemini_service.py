"""Gemini AI Service module for deep resume analysis, bullet rewrites, and realtime job intelligence."""

import json
import logging
from typing import Dict, Any, List, Optional
import requests
from config import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)


class GeminiService:
    """Connects to Google Gemini REST API without requiring native C++ DLLs."""

    def __init__(self, api_key: str = GEMINI_API_KEY, model: str = GEMINI_MODEL):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    def is_available(self) -> bool:
        """Check if Gemini API key is configured."""
        return bool(self.api_key and len(self.api_key) > 20)

    def _call_gemini_json(self, prompt: str, timeout: int = 25) -> Optional[Dict[str, Any]]:
        """Call Gemini generateContent endpoint requesting pure JSON response."""
        if not self.is_available():
            return None

        # Prefer fast flash models
        models_to_try = [self.model, "gemini-3.5-flash-lite", "gemini-3.8-flash"]
        # Deduplicate while preserving order
        models_to_try = list(dict.fromkeys(models_to_try))

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.3,
            }
        }

        for m in models_to_try:
            url = f"{self.base_url}/models/{m}:generateContent?key={self.api_key}"
            try:
                resp = requests.post(url, json=payload, timeout=timeout)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        text_content = candidates[0]["content"]["parts"][0]["text"]
                        return json.loads(text_content)
                elif resp.status_code == 429:
                    logger.warning(f"Gemini API rate limit exceeded on model {m}.")
                    continue
                else:
                    logger.warning(f"Gemini API error {resp.status_code} on model {m}: {resp.text[:200]}")
            except Exception as e:
                logger.warning(f"Gemini request exception on model {m}: {str(e)}")
                continue

        return None

    def analyze_resume_ai(
        self,
        resume_text: str,
        extracted_skills: List[str],
        top_role: str = "Software Engineer"
    ) -> Dict[str, Any]:
        """Perform deep LLM resume critique, bullet point rewrites, and senior recruiter advice."""
        # Truncate resume text if very long to keep under token limits
        trimmed_resume = resume_text[:3500]

        prompt = f"""
You are a Principal Technical Recruiter and Staff Engineering Hiring Manager at a top tech company.
Analyze this resume for a candidate targeting the role of '{top_role}'.

Candidate Extracted Skills: {', '.join(extracted_skills[:20])}

Resume Content:
\"\"\"
{trimmed_resume}
\"\"\"

Produce a comprehensive, rigorous ATS critique and coaching plan formatted as a JSON object with EXACTLY this structure:
{{
  "ai_overall_feedback": "A concise 2-3 sentence executive assessment of candidate marketability and resume punch.",
  "market_fit_rating": "Strong / Moderate / Needs Development",
  "executive_summary_critique": {{
    "current_critique": "Analysis of existing summary or note if missing",
    "proposed_rewrite": "A punchy, recruiter-grade 3-4 sentence professional summary explicitly tailored for {top_role}"
  }},
  "bullet_point_improvements": [
    {{
      "original": "A representative bullet point from the resume that sounds passive or weak",
      "improved": "Rewritten bullet using Google's X-Y-Z formula ('Accomplished [X] as measured by [Y], by doing [Z]') with strong action verbs and metrics",
      "why_better": "Specific explanation of why recruiters prefer this framing"
    }},
    {{
      "original": "Another representative bullet point from projects or experience",
      "improved": "Rewritten high-impact version with technical specifics and business outcome",
      "why_better": "Explanation of clarity and impact"
    }}
  ],
  "missing_high_impact_keywords": [
    "Crucial technical keyword 1",
    "Crucial technical keyword 2",
    "Crucial technical keyword 3",
    "Crucial technical keyword 4"
  ],
  "recruiter_interview_tips": [
    "Strategic tip on how to discuss project trade-offs in interviews",
    "Tip on highlighting technical leadership and system architecture",
    "Tip on addressing potential resume gaps or positioning achievements"
  ]
}}
"""

        result = self._call_gemini_json(prompt)
        if result:
            return result

        # Fallback heuristic if API quota or network issue occurs
        return {
            "ai_overall_feedback": f"Resume exhibits solid technical foundations for {top_role}. Strengthening quantified business impact and adding targeted domain keywords will noticeably enhance ATS ranking.",
            "market_fit_rating": "Moderate",
            "executive_summary_critique": {
                "current_critique": "Summary can be more targeted to highlight enterprise scale and specific technical proficiencies.",
                "proposed_rewrite": f"Accomplished {top_role} specializing in scalable systems, clean architecture, and modern cloud deployment. Proven track record of optimizing application performance and delivering resilient software solutions."
            },
            "bullet_point_improvements": [
                {
                    "original": "Responsible for developing web applications and database integration.",
                    "improved": "Architected and delivered full-stack web applications with high-throughput database queries, reducing average API response latency by 30%.",
                    "why_better": "Swaps passive 'responsible for' with 'architected' and provides a quantified latency metric."
                }
            ],
            "missing_high_impact_keywords": ["Microservices", "CI/CD Automation", "System Design", "Cloud Infrastructure"],
            "recruiter_interview_tips": [
                "Be ready to explain the architectural trade-offs behind your chosen tech stack.",
                "Structure your behavioral stories using the STAR (Situation, Task, Action, Result) framework.",
                "Highlight how you tested, monitored, and maintained uptime for your projects in production."
            ]
        }

