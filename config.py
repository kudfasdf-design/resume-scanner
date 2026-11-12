"""Configuration settings for the AI-Based Resume Screening and Job Recommendation System."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SAMPLES_DIR = BASE_DIR / "samples"

# Load environment variables
load_dotenv(BASE_DIR / ".env")

# File upload constraints
MAX_FILE_MB = int(os.getenv("MAX_FILE_MB", "5"))
MAX_FILE_BYTES = MAX_FILE_MB * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".docx"}

# Scoring weights (sum to 100)
SECTION_WEIGHTS = {
    "skills": 25,
    "experience": 20,
    "projects": 20,
    "education": 15,
    "certifications": 5,
    "contact": 5,
    "summary": 5,
    "formatting": 5,
}

# Fuzzy matching thresholds
FUZZY_SKILL_THRESHOLD = int(os.getenv("FUZZY_SKILL_THRESHOLD", "90"))
FUZZY_HEADING_THRESHOLD = int(os.getenv("FUZZY_HEADING_THRESHOLD", "85"))

# Recommendation settings
DEFAULT_TOP_N_ROLES = int(os.getenv("TOP_N_ROLES", "5"))

# Job Provider configuration
JOB_PROVIDER = os.getenv("JOB_PROVIDER", "local").lower()
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID", "")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY", "")

# Gemini AI configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

# Data file paths
SKILLS_FILE = DATA_DIR / "skills.json"
ROLES_FILE = DATA_DIR / "roles.json"
JOBS_FILE = DATA_DIR / "jobs.json"

