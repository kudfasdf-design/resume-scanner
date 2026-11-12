"""Job source abstraction providing local curated openings, real-time live job feeds, and Adzuna API integration."""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Protocol, Dict, Any
import requests
from config import JOBS_FILE, ADZUNA_APP_ID, ADZUNA_APP_KEY


@dataclass
class Job:
    id: str
    title: str
    company: str
    location: str
    job_type: str
    description: str
    required_skills: List[str] = field(default_factory=list)
    url: str = ""
    is_live: bool = False


class JobProvider(Protocol):
    def search(self, keywords: List[str], location: Optional[str] = None) -> List[Job]:
        ...


class LocalJobProvider:
    """Reads curated offline job listings from data/jobs.json."""

    def __init__(self, jobs_path: Path = JOBS_FILE):
        self.jobs_path = jobs_path
        self.jobs: List[Job] = []
        self.load_jobs()

    def load_jobs(self) -> None:
        if self.jobs_path.exists():
            with open(self.jobs_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.jobs = [
                    Job(
                        id=item.get("id", f"J{i:03d}"),
                        title=item.get("title", "Untitled Role"),
                        company=item.get("company", "Company"),
                        location=item.get("location", "Remote"),
                        job_type=item.get("job_type", "Full-time"),
                        description=item.get("description", ""),
                        required_skills=item.get("required_skills", []),
                        url=item.get("url", "#"),
                        is_live=False,
                    )
                    for i, item in enumerate(data)
                ]
        else:
            self.jobs = []

    def search(self, keywords: List[str], location: Optional[str] = None) -> List[Job]:
        """Search jobs matching keywords and optional location."""
        if not keywords and not location:
            return self.jobs

        filtered = []
        keywords_lower = [k.lower() for k in keywords]
        loc_lower = location.lower() if location and location.lower() != "all" else None

        for job in self.jobs:
            # Check location
            if loc_lower and loc_lower not in job.location.lower() and "remote" not in job.location.lower():
                continue

            # Check keyword relevance
            text_corpus = f"{job.title} {job.description} {' '.join(job.required_skills)}".lower()
            if not keywords_lower or any(kw in text_corpus for kw in keywords_lower):
                filtered.append(job)

        return filtered if filtered else self.jobs


class RealtimeJobProvider:
    """Fetches real-time active job postings from live tech job feeds, seamlessly falling back to local."""

    def __init__(self, fallback: Optional[JobProvider] = None):
        self.fallback = fallback or LocalJobProvider()
        self._cache: List[Job] = []
        self._fetched = False

    def _fetch_live_jobs(self) -> List[Job]:
        if self._fetched and self._cache:
            return self._cache

        live_jobs = []
        try:
            resp = requests.get("https://www.arbeitnow.com/api/job-board-api", timeout=6)
            if resp.status_code == 200:
                data = resp.json().get("data", [])
                for item in data[:40]:
                    raw_desc = item.get("description", "")
                    clean_desc = re.sub(r"<[^>]+>", " ", raw_desc)
                    clean_desc = re.sub(r"\s+", " ", clean_desc).strip()[:240] + "..."

                    tags = item.get("tags", [])
                    job_type = "Remote" if item.get("remote") else "Full-time"
                    loc = "Remote" if item.get("remote") else item.get("location", "Global")

                    live_jobs.append(
                        Job(
                            id=item.get("slug", f"RT-{len(live_jobs)}"),
                            title=item.get("title", "Software Engineer"),
                            company=item.get("company_name", "Tech Startup"),
                            location=loc,
                            job_type=job_type,
                            description=clean_desc,
                            required_skills=tags[:6] if tags else ["Software Development", "Python", "Cloud"],
                            url=item.get("url", "#"),
                            is_live=True
                        )
                    )
                self._cache = live_jobs
                self._fetched = True
        except Exception:
            pass

        return self._cache

    def search(self, keywords: List[str], location: Optional[str] = None) -> List[Job]:
        live_openings = self._fetch_live_jobs()
        local_openings = self.fallback.search(keywords, location)

        if not live_openings:
            return local_openings

        # Filter live openings
        matched_live = []
        keywords_lower = [k.lower() for k in keywords]
        loc_lower = location.lower() if location and location.lower() != "all" else None

        for job in live_openings:
            if loc_lower and loc_lower not in job.location.lower() and "remote" not in job.location.lower():
                continue

            text_corpus = f"{job.title} {job.description} {' '.join(job.required_skills)}".lower()
            if not keywords_lower or any(kw in text_corpus for kw in keywords_lower):
                matched_live.append(job)

        # Merge live matches with local openings for rich coverage
        combined = matched_live + local_openings
        return combined if combined else local_openings


class AdzunaJobProvider:
    """Fetches job listings from Adzuna API with transparent fallback to LocalJobProvider."""

    def __init__(self, app_id: str = ADZUNA_APP_ID, app_key: str = ADZUNA_APP_KEY, fallback: Optional[JobProvider] = None):
        self.app_id = app_id
        self.app_key = app_key
        self.fallback = fallback or LocalJobProvider()

    def search(self, keywords: List[str], location: Optional[str] = None) -> List[Job]:
        if not self.app_id or not self.app_key:
            return self.fallback.search(keywords, location)

        query = " ".join(keywords[:3])
        country = "in"  # default country India
        url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "what": query,
            "content-type": "application/json",
            "results_per_page": 20,
        }
        if location and location.lower() != "all":
            params["where"] = location

        try:
            resp = requests.get(url, params=params, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("results", [])
                adzuna_jobs = []
                for item in results:
                    adzuna_jobs.append(
                        Job(
                            id=str(item.get("id")),
                            title=item.get("title", "Job Title"),
                            company=item.get("company", {}).get("display_name", "Company"),
                            location=item.get("location", {}).get("display_name", "India"),
                            job_type="Full-time",
                            description=item.get("description", ""),
                            required_skills=keywords[:4],
                            url=item.get("redirect_url", "#"),
                            is_live=True
                        )
                    )
                if adzuna_jobs:
                    return adzuna_jobs
        except Exception:
            pass

        return self.fallback.search(keywords, location)
