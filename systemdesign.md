# System Design Document

## AI-Based Resume Screening and Job Recommendation System

| Field | Value |
|---|---|
| Version | 1.0 |
| Date | 12 November 2026 |
| Related documents | `PRD.md`, `requirements.txt` |

---

## 1. Design Goals

- **Simple**: single-process Python app, no database server, no paid APIs.
- **Modular**: each responsibility lives in its own module with a small interface.
- **Scalable (at project level)**: skills, roles, and jobs are data files; the job source is swappable; scoring weights live in configuration.
- **Explainable**: every output is traceable to a rule or a matched skill.

## 2. Architecture Overview

A layered architecture runs inside one Streamlit application.

```
┌──────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│              Streamlit UI (app.py, ui/ components)           │
│  Upload | Overview | Sections | Suggestions | Roles | Jobs   │
└───────────────────────────────┬──────────────────────────────┘
                                │ calls
┌───────────────────────────────▼──────────────────────────────┐
│                  Application / Service Layer                 │
│            pipeline.py  (orchestrates the workflow)          │
└───┬───────────┬─────────────┬──────────────┬─────────────┬───┘
    │           │             │              │             │
┌───▼────┐ ┌────▼─────┐ ┌─────▼──────┐ ┌─────▼─────┐ ┌─────▼────┐
│ Parser │ │ Section  │ │  Skill     │ │ Analyzer  │ │ Report   │
│ module │ │ Extractor│ │  Extractor │ │ & Scorer  │ │ Builder  │
└───┬────┘ └────┬─────┘ └─────┬──────┘ └─────┬─────┘ └──────────┘
    │           │             │              │
    │           │       ┌─────▼──────────────▼─────┐
    │           │       │  Role Matcher   Job      │
    │           │       │  (roles.json)   Matcher  │
    │           │       │            ┌─────────────┤
    │           │       │            │ JobProvider │
    │           │       └────────────┤  interface  │
    │           │                    └──┬───────┬──┘
┌───▼───────────▼───────────────────────▼──┐  ┌─▼──────────────┐
│               Data Layer                 │  │ Optional API   │
│ skills.json | roles.json | jobs.json    │  │ (Adzuna)       │
└──────────────────────────────────────────┘  └────────────────┘
```

## 3. Technology Stack

| Area | Technology | Purpose |
|---|---|---|
| Language | Python 3.10+ | Core implementation |
| UI | Streamlit | Web interface, file upload, tabs, downloads |
| PDF parsing | pdfplumber | Text extraction from PDFs |
| DOCX parsing | python-docx | Text extraction from Word files (paragraphs and tables) |
| Text matching | rapidfuzz | Fuzzy skill and heading matching |
| Similarity | scikit-learn | TF-IDF vectorization and cosine similarity |
| Data handling | pandas, numpy | Job tables, filtering, score arrays |
| Charts | plotly | Score gauge, skill charts |
| HTTP | requests | Optional job API calls |
| Config | python-dotenv | API keys and settings from `.env` |
| Testing | pytest | Unit tests |
| Storage | JSON files | Skills, roles, jobs (no database) |

All versions are pinned in `requirements.txt`.

## 4. Project Structure

```
resume_screener/
├── app.py                    # Streamlit entry point
├── config.py                 # Settings, weights, file limits
├── pipeline.py               # Orchestrates the full workflow
├── modules/
│   ├── __init__.py
│   ├── parser.py             # File validation + text extraction
│   ├── cleaner.py            # Text normalization
│   ├── section_extractor.py  # Heading detection, section splitting, contact info
│   ├── skill_extractor.py    # Taxonomy + fuzzy skill matching
│   ├── analyzer.py           # Section evaluation, scoring, suggestions
│   ├── role_matcher.py       # Role recommendation + skill gap
│   ├── job_matcher.py        # Ranking job openings
│   ├── job_providers.py      # JobProvider interface, LocalJobProvider, AdzunaJobProvider
│   └── report.py             # JSON / Markdown report builder
├── data/
│   ├── skills.json           # Skill taxonomy with categories and aliases
│   ├── roles.json            # Job roles with required / optional skills
│   └── jobs.json             # Curated sample job openings
├── ui/
│   └── components.py         # Reusable Streamlit render functions
├── tests/
│   ├── test_parser.py
│   ├── test_section_extractor.py
│   ├── test_skill_extractor.py
│   ├── test_analyzer.py
│   └── test_matchers.py
├── samples/                  # Sample resumes for testing
├── .env.example
├── requirements.txt
├── PRD.md
├── systemdesign.md
└── README.md
```

## 5. Module Descriptions

### 5.1 `parser.py`: File Validation and Text Extraction
- **Input**: uploaded file (bytes, filename).
- **Checks**: extension in `{.pdf, .docx}`, size at most `MAX_FILE_MB`, file not corrupted.
- **PDF**: `pdfplumber` extracts text page by page. If total text length is below a threshold (about 50 characters), raise `ScannedPdfError`.
- **DOCX**: `python-docx` reads paragraphs and table cells.
- **Output**: raw text string.
- **Errors**: `UnsupportedFormatError`, `FileTooLargeError`, `ScannedPdfError`, `ParseError`, all shown as friendly UI messages.

### 5.2 `cleaner.py`: Text Normalization
Normalizes unicode, bullet characters, repeated whitespace, hyphenated line breaks, and page-break artifacts. Preserves line breaks because section detection depends on them.

### 5.3 `section_extractor.py`: Sections and Contact Info
- A heading is a short line (under 40 characters) that fuzzy-matches a heading synonym list, usually in caps or title case with no trailing punctuation.
- Synonym map example: `Education: [education, academic background, qualifications]`, `Projects: [projects, academic projects, personal projects]`, `Experience: [experience, work experience, internships, employment]`, `Skills: [skills, technical skills, core competencies]`, `Certifications: [certifications, licenses, courses]`, `Summary: [summary, objective, profile, about me]`.
- Text between headings is assigned to the preceding section.
- **Fallback**: if no headings are detected, keyword scanning classifies lines (e.g., "B.Tech", "University" go to Education).
- **Contact extraction**: regex for email, phone, LinkedIn, GitHub; the first non-empty line is the name candidate.
- **Output**: `dict` with `contact` and `sections` (`{section_name: text}`).

### 5.4 `skill_extractor.py`: Skill Extraction
- Loads `skills.json` (canonical name, category, aliases).
- Exact word-boundary matching on normalized text, then `rapidfuzz` partial matching for near-misses (threshold 90) on short tokens.
- Records where each skill was found (Skills section, Projects, Experience), since skills evidenced in projects or experience carry more weight.
- **Output**: `{canonical_skill: {category, sources[], count}}`.

### 5.5 `analyzer.py`: Evaluation, Scoring, and Suggestions
Runs rule-based checks per section and returns a section score (0-100), findings, and suggestions.

| Section | Example checks |
|---|---|
| Contact | Email present, phone present, LinkedIn/GitHub present |
| Summary | Present, 2-4 lines, mentions target role or skills |
| Skills | At least 8 skills, multiple categories, skills also evidenced in projects/experience |
| Education | Degree, institution, year, CGPA/percentage present |
| Projects | At least 2 projects, tech stack mentioned, measurable outcomes, links |
| Experience | Dates present, action verbs, quantified results, internships counted for freshers |
| Certifications | At least 1 relevant certification |
| Formatting | Length between 300 and 900 words, bullet usage, no excessive long paragraphs |

- **Action verb check**: bullets starting with strong verbs (built, developed, optimized) versus weak phrases ("responsible for", "worked on").
- **Metric check**: regex for numbers, percentages, and currency in bullets.
- **Overall score** = sum(section_score x weight) / 100, with weights from `config.py` (see PRD section 7.4). A missing section scores 0 for that component.
- **Suggestions**: each is `{section, priority, message}`; High priority is assigned to missing sections and missing core skills.
- **Strengths/weaknesses**: sections scoring at least 75 become strengths and sections below 50 become weaknesses, with specific supporting findings.

### 5.6 `role_matcher.py`: Role Recommendation and Skill Gap
- `roles.json` entry: `{role, description, required_skills[], optional_skills[]}`.
- **Role score** = 0.6 x required-skill coverage + 0.2 x optional-skill coverage + 0.2 x TF-IDF cosine similarity (resume text versus role description plus skill list).
- Returns the top N roles with `match_percent`, `matched_skills`, `missing_required`, `missing_optional`.
- **Learning priorities**: missing skills ranked by how many top roles require them.

### 5.7 `job_providers.py`: Job Source Abstraction
```python
class JobProvider(Protocol):
    def search(self, keywords: list[str], location: str | None) -> list[Job]: ...
```
- `LocalJobProvider` reads `jobs.json` (default, offline).
- `AdzunaJobProvider` calls the Adzuna API using keys from `.env`. It sends search keywords only, never resume text. On any failure or missing keys it falls back to `LocalJobProvider`.
- `Job` fields: `id, title, company, location, job_type, description, required_skills[], url`.

### 5.8 `job_matcher.py`: Ranking Openings
- Candidate jobs are fetched using the top roles' titles as keywords.
- **Job score** = 0.6 x required-skill coverage + 0.4 x TF-IDF cosine similarity (resume text versus job description).
- Each job returns `match_percent`, `matched_skills`, and `skill_gap`.
- Supports filtering by role, location, and job type (pandas DataFrame).
- Optional pasted job description is treated as one ad-hoc `Job` and scored the same way.

### 5.9 `report.py`: Report Builder
Builds a structured `dict` (JSON export) and a Markdown report (score, strengths, weaknesses, suggestions, roles, jobs, learning priorities).

### 5.10 `pipeline.py`: Orchestrator
```python
def analyze_resume(file_bytes, filename, target_jd=None, location=None) -> AnalysisResult
```
Calls modules in order and returns a single `AnalysisResult` dataclass consumed by the UI and report builder.

### 5.11 `app.py` and `ui/components.py`: Presentation
Streamlit page with sidebar settings (number of roles, location filter, optional JD) and result tabs. Results are cached in `st.session_state` so filter changes do not re-parse the file.

## 6. Data Design

### 6.1 `skills.json`
```json
{
  "Python": {"category": "Programming", "aliases": ["python3", "py"]},
  "JavaScript": {"category": "Web", "aliases": ["js", "ecmascript"]},
  "Machine Learning": {"category": "Data/ML", "aliases": ["ml"]}
}
```

### 6.2 `roles.json`
```json
{
  "role": "Data Analyst",
  "description": "Analyses data to produce insights and dashboards.",
  "required_skills": ["SQL", "Excel", "Python", "Data Visualization"],
  "optional_skills": ["Power BI", "Tableau", "Statistics"]
}
```

### 6.3 `jobs.json`
```json
{
  "id": "J001",
  "title": "Junior Data Analyst",
  "company": "Example Corp",
  "location": "Bengaluru",
  "job_type": "Full-time",
  "description": "Work with SQL and Python to build dashboards...",
  "required_skills": ["SQL", "Python", "Excel"],
  "url": "https://example.com/jobs/J001"
}
```

### 6.4 Core In-Memory Objects (dataclasses)
`ParsedResume`, `SkillHit`, `SectionReport`, `Suggestion`, `RoleMatch`, `JobMatch`, `AnalysisResult`.

## 7. Data Flow

```
Upload (PDF/DOCX)
   │
   ▼
parser.validate_and_extract()  ──► raw text
   │
   ▼
cleaner.normalize()            ──► clean text
   │
   ▼
section_extractor              ──► contact + sections
   │
   ├──────────────► skill_extractor ──► skills (with sources)
   │                        │
   ▼                        ▼
analyzer.evaluate()  ◄──────┘   ──► section scores, overall score,
   │                                  strengths, weaknesses, suggestions
   ▼
role_matcher  (uses skills + text) ──► top roles + skill gaps
   │
   ▼
job_providers ──► candidate jobs
   │
   ▼
job_matcher   ──► ranked jobs + per-job skill gap
   │
   ▼
AnalysisResult ──► UI tabs  /  report.py (JSON, Markdown download)
```

## 8. Overall Workflow

1. **Upload**: user selects a file; the UI sends bytes and filename to the pipeline.
2. **Validate and parse**: type, size, and readability are checked and text is extracted.
3. **Clean**: text is normalized.
4. **Segment**: contact info and sections are extracted.
5. **Extract skills**: taxonomy matching with source tracking.
6. **Analyse**: per-section scoring, overall score, strengths, weaknesses, suggestions.
7. **Recommend roles**: scoring against `roles.json`, with skill gaps.
8. **Match jobs**: fetch candidates, rank, compute per-job gaps.
9. **Present**: render tabs (Overview, Sections, Suggestions, Roles, Jobs).
10. **Export**: download JSON or Markdown report.
11. **Cleanup**: temporary data is dropped when the session ends.

## 9. UI Layout

| Tab | Content |
|---|---|
| Overview | Overall score gauge, section score bar chart, top strengths and weaknesses, extracted skills by category |
| Section Analysis | Expandable panel per section with findings and the detected text |
| Suggestions | Prioritized list (High / Medium / Low) grouped by section |
| Recommended Roles | Role cards with match %, matched skills, missing skills, learning priorities |
| Job Openings | Filterable table and cards with match %, location, type, skill gap, link |
| Report | Download buttons for JSON and Markdown |

## 10. Configuration (`config.py` / `.env`)

| Setting | Default |
|---|---|
| `MAX_FILE_MB` | 5 |
| `ALLOWED_EXTENSIONS` | `.pdf`, `.docx` |
| `TOP_N_ROLES` | 5 |
| `SECTION_WEIGHTS` | Skills 25, Experience 20, Projects 20, Education 15, Certifications 5, Contact 5, Summary 5, Formatting 5 |
| `FUZZY_THRESHOLD` | 90 |
| `JOB_PROVIDER` | `local` (or `adzuna`) |
| `ADZUNA_APP_ID`, `ADZUNA_APP_KEY` | empty (only needed for the Adzuna provider) |

## 11. Error Handling

| Situation | Behaviour |
|---|---|
| Unsupported file type | Message listing allowed types |
| File too large | Message with size limit |
| Scanned/image PDF | Message explaining text could not be extracted and suggesting a text-based PDF or DOCX |
| Corrupted file | Generic parse error, no stack trace shown |
| No sections detected | Fallback keyword classification, plus a warning |
| Job API failure | Silent fallback to local dataset with a small notice |

## 12. Security and Privacy

- Files are validated by extension and size, and opened only by parsing libraries (never executed).
- Resume content stays in memory for the session; no database persistence.
- The optional job API receives only keywords and location.
- Secrets are loaded from `.env`, which is excluded from version control.

## 13. Testing Strategy

| Level | Coverage |
|---|---|
| Unit tests | Parser errors, section detection, contact regexes, skill extraction with aliases, scoring bounds, role and job ranking |
| Integration test | Run the pipeline on sample resumes in `samples/` and assert structure of `AnalysisResult` |
| Manual UI test | Upload each sample, check tabs, filters, and downloads |

## 14. Scalability and Extensibility

- Add roles, skills, or jobs by editing JSON files.
- Add a new job source by implementing `JobProvider`.
- Replace TF-IDF with sentence embeddings by swapping the similarity function behind a single `similarity(a, b)` interface.
- Scoring weights and thresholds are configuration, not code.
- The pipeline returns a plain data object, so the Streamlit UI can later be replaced by a FastAPI backend with a separate frontend.

## 15. Implementation Plan

| Phase | Work |
|---|---|
| 1 | Project skeleton, config, data files (skills, roles, jobs) |
| 2 | Parser, cleaner, section extractor with tests |
| 3 | Skill extractor and analyzer with tests |
| 4 | Role matcher, job providers, job matcher with tests |
| 5 | Pipeline, Streamlit UI, report export |
| 6 | Sample resumes, testing, README, polish |

