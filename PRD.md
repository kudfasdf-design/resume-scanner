# Product Requirements Document (PRD)

## AI-Based Resume Screening and Job Recommendation System

| Field | Value |
|---|---|
| Version | 1.0 |
| Date | 12 November 2026 |
| Project type | College-level mini project |
| Primary language | Python 3.10+ |
| UI framework | Streamlit |

---

## 1. Project Overview

Many job seekers, especially students and fresh graduates, submit resumes without knowing whether the content is strong, complete, or relevant to the roles they want. Recruiters and applicant tracking systems (ATS) screen resumes quickly and reject those that lack clear skills, measurable achievements, or standard structure.

This project is a web application where a user uploads a resume (PDF or DOCX). The system extracts the text, identifies the main sections, evaluates quality, and reports strengths, weaknesses, and concrete improvement suggestions. It then infers suitable job roles from the extracted skills and experience, matches the resume against available job openings, and tells the user which skills they still need for each recommended role.

The analysis is **rule-based and NLP-based** (keyword/skill taxonomy, fuzzy matching, TF-IDF cosine similarity). It does not depend on a paid LLM API, so it is simple to run, explain, and demonstrate in a college setting. A pluggable design leaves room to add ML or LLM-based scoring later.

## 2. Objectives

1. Let users upload a resume in PDF or DOCX format and extract its text reliably.
2. Detect and evaluate the key sections: Contact info, Summary, Skills, Education, Projects, Experience, Certifications.
3. Identify missing or weak sections and give actionable, specific suggestions.
4. Produce an overall resume score (0-100) with a per-section breakdown.
5. Extract skills and map them to a skill taxonomy.
6. Recommend the top suitable job roles with a match percentage.
7. Display matching job openings and rank them against the resume.
8. For each recommended role or job, show matched skills and the skills required to become eligible (skill gap).
9. Keep the codebase modular, readable, and easy to extend.

## 3. Target Users

| User | Need |
|---|---|
| Students and fresh graduates (primary) | Know how to improve a first resume and which roles to target |
| Early-career professionals | Check resume strength and find roles that fit their skills |
| Career-switchers | See which skills are missing for a new role |
| College placement cells / faculty (secondary) | Demonstrate a simple resume-screening tool |

## 4. Scope

### 4.1 In Scope
- Single-user, session-based web app (no login required).
- Upload of one resume at a time (PDF, DOCX).
- Text extraction, section detection, skill extraction.
- Resume quality analysis, scoring, and suggestions.
- Job role recommendation from a curated role taxonomy.
- Job opening matching from a local curated dataset (`jobs.json`), with an optional live job API adapter.
- Skill-gap analysis per role/job.
- Downloadable analysis report (JSON and text/Markdown).
- Basic unit tests for core modules.

### 4.2 Out of Scope
- User accounts, authentication, and persistent user profiles.
- OCR for scanned/image-only resumes (a clear error message is shown instead).
- Resume rewriting or generation using generative AI.
- Applying to jobs directly or employer-side dashboards.
- Multi-language resumes (English only).
- Production-grade deployment, payments, and email notifications.

## 5. Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-1 | The system shall accept PDF and DOCX uploads and reject other formats with a clear message. | Must |
| FR-2 | The system shall enforce a maximum file size (default 5 MB). | Must |
| FR-3 | The system shall extract plain text from PDF (text-based) and DOCX files. | Must |
| FR-4 | The system shall detect a scanned/empty PDF and tell the user that no text could be extracted. | Must |
| FR-5 | The system shall extract contact details (name guess, email, phone, LinkedIn, GitHub). | Must |
| FR-6 | The system shall segment the resume into sections using heading detection (Summary, Skills, Education, Projects, Experience, Certifications). | Must |
| FR-7 | The system shall extract skills by matching text against a skill taxonomy, including aliases (e.g., "JS" = "JavaScript") with fuzzy matching. | Must |
| FR-8 | The system shall evaluate each section for presence and quality and assign a section score. | Must |
| FR-9 | The system shall compute an overall score from 0 to 100 using weighted section scores and global checks. | Must |
| FR-10 | The system shall list strengths and weaknesses in plain language. | Must |
| FR-11 | The system shall generate actionable suggestions, each tied to a section and a priority (High / Medium / Low). | Must |
| FR-12 | The system shall flag missing sections and weak content (no metrics, weak verbs, too short, no links, no dates). | Must |
| FR-13 | The system shall recommend the top N (default 5) job roles with a match percentage. | Must |
| FR-14 | The system shall show matched skills and missing skills for each recommended role. | Must |
| FR-15 | The system shall display job openings relevant to the recommended roles, ranked by match score. | Must |
| FR-16 | The system shall allow filtering job openings by role, location, and job type. | Should |
| FR-17 | For each job opening, the system shall show required skills the user lacks (skill gap). | Must |
| FR-18 | The system shall suggest learning priorities (most frequently required missing skills first). | Should |
| FR-19 | The system shall let the user paste an optional target job description and score the resume against it. | Should |
| FR-20 | The system shall let the user download the analysis report (JSON and Markdown). | Should |
| FR-21 | The system shall allow job data to come from a local dataset or an optional external API through a common provider interface. | Could |

## 6. Non-Functional Requirements

| ID | Category | Requirement |
|---|---|---|
| NFR-1 | Performance | Analysis of a typical 1-3 page resume completes in under 5 seconds on a standard laptop. |
| NFR-2 | Usability | A first-time user can upload and read results without instructions; results are grouped into clear tabs. |
| NFR-3 | Modularity | Parsing, analysis, matching, and UI are separate modules with defined interfaces. |
| NFR-4 | Scalability | The skill taxonomy, role definitions, and job data are stored in editable data files, so new roles and jobs are added without code changes. The job source can be swapped via the provider interface. |
| NFR-5 | Privacy | Uploaded resumes are processed in memory/temporary storage and deleted after the session; nothing is sent to third parties unless the optional job API is enabled, and then only search keywords are sent, never resume text. |
| NFR-6 | Reliability | The system handles corrupted files, empty files, and unsupported formats without crashing. |
| NFR-7 | Portability | Runs on Windows, macOS, and Linux with `pip install -r requirements.txt` and no external services required. |
| NFR-8 | Maintainability | Code follows PEP 8, has docstrings and type hints, and core modules have unit tests. |
| NFR-9 | Explainability | Every score and recommendation can be traced to visible rules (matched skills, missing sections). |

## 7. Features

### 7.1 Resume Upload and Parsing
Drag-and-drop uploader for PDF/DOCX with format and size validation, text extraction, and cleaning (whitespace, bullets, hyphenation).

### 7.2 Section Detection
Heading-based segmentation with synonym lists (e.g., "Academic Background" = Education, "Technical Skills" = Skills).

### 7.3 Skill Extraction
Taxonomy-based matching by category (Programming Languages, Web, Data/ML, Databases, Cloud/DevOps, Tools, Soft Skills) with alias handling and fuzzy matching.

### 7.4 Resume Evaluation and Scoring
Weighted scoring across sections plus global checks:

| Component | Weight |
|---|---|
| Skills | 25 |
| Experience | 20 |
| Projects | 20 |
| Education | 15 |
| Certifications | 5 |
| Contact and links | 5 |
| Summary | 5 |
| Formatting and length | 5 |

### 7.5 Strengths, Weaknesses, and Suggestions
Rule-driven feedback such as "Add measurable results to your project bullets (e.g., 'reduced load time by 30%')" or "Add a GitHub link".

### 7.6 Job Role Recommendation
Each role in `roles.json` has required and optional skills. Role match = weighted combination of skill coverage and TF-IDF text similarity. The top roles are shown with a match percentage.

### 7.7 Job Opening Mapping
Job openings from `jobs.json` (or an optional API) are ranked by cosine similarity and skill overlap with the resume. Each card shows title, company, location, type, match %, matched skills, and missing skills.

### 7.8 Skill-Gap Analysis
For each role/job: matched skills, missing required skills, missing nice-to-have skills, and a prioritized learning list.

### 7.9 Report Export
Download results as JSON or Markdown.

## 8. User Flow

1. Open the app and upload a resume.
2. The system parses and analyses the resume.
3. User views the **Overview** tab (score, strengths, weaknesses).
4. User views **Section Analysis** and **Suggestions**.
5. User views **Recommended Roles** with skill gaps.
6. User browses **Job Openings** with filters.
7. User downloads the report.

## 9. Success Metrics (for evaluation)

- Parsing succeeds on at least 95% of text-based test resumes (target set of 20 sample resumes).
- Skill extraction recall of at least 80% against manually tagged samples.
- Top-3 role recommendations judged relevant in at least 80% of test cases.
- Full analysis time under 5 seconds.
- All core module unit tests pass.

## 10. Assumptions and Constraints

- Resumes are in English and text-based (not scanned images).
- Job data is a curated sample dataset of 40-60 openings unless the optional API is configured.
- Scores are heuristic indicators, not a hiring decision.
- The project must run on a typical student laptop without GPU or paid services.

## 11. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Varied resume layouts break section detection | Use a broad heading synonym list and a fallback that scans for keywords when headings are absent |
| Multi-column PDFs produce jumbled text | Use pdfplumber layout-aware extraction and show a warning when extracted text looks irregular |
| Skill taxonomy is incomplete | Store the taxonomy in an editable JSON file |
| Live job API unavailable or rate-limited | Default to the local dataset; API is optional with automatic fallback |

## 12. Future Enhancements

- OCR support for scanned resumes.
- Sentence-embedding semantic matching.
- LLM-generated rewrite suggestions.
- Multiple resume comparison and recruiter-side bulk screening.
- User accounts with saved history.

## 13. Deliverables

1. `PRD.md` (this document)
2. `systemdesign.md`
3. `requirements.txt`
4. Working Streamlit application and data files
5. Unit tests and sample resumes
6. README with setup and usage instructions

