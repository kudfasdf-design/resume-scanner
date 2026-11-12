# ResumeAI: AI-Based Resume Screening and Job Recommendation System

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.39-FF4B4B.svg)](https://streamlit.io/)
[![Stitch Enhanced](https://img.shields.io/badge/Design-Google%20Stitch-6366F1.svg)](https://stitch.withgoogle.com/)
[![Tests](https://img.shields.io/badge/Tests-17%20Passed-2DD4BF.svg)](https://pytest.org/)

An intelligent, rule-based and NLP-powered resume screening and career recommendation platform. It parses resumes (PDF/DOCX), segments core structural sections, maps technical proficiencies against a canonical 7-domain taxonomy with source tracking, quantifies content impact (action verbs, metrics, and completeness), matches optimal career pathways with prioritized learning roadmaps, and ranks relevant job openings with transparent skill gaps.

---

## 🚀 Key Features

1. **Robust Multi-Format Parsing & Text Cleaning**:
   - Supports `.pdf` (text-based) and `.docx` (paragraphs and tables) with size constraints (up to 5 MB).
   - Scanned PDF detection alerting users when OCR/text is unextractable.
   - Normalization of bullets, unicode, hyphenated line breaks, and page-break artifacts while preserving paragraph lines.

2. **Automated Section & Contact Segmentation**:
   - Heuristic and fuzzy synonym heading matching for `Summary`, `Skills`, `Experience`, `Projects`, `Education`, and `Certifications`.
   - Contact info extraction: Candidate Name, Email, Phone Number, LinkedIn, and GitHub profile links.
   - Fallback keyword segmenter for unheaded resumes.

3. **Canonical Skill Taxonomy & Source Tracking**:
   - Comprehensive taxonomy across 7 categories: *Programming Languages*, *Web*, *Data/ML*, *Databases*, *Cloud/DevOps*, *Tools*, and *Soft Skills*.
   - Exact word-boundary regex and fuzzy partial-ratio alias matching (e.g. `JS` ➔ `JavaScript`, `K8s` ➔ `Kubernetes`).
   - Tracks where skills appear (Skills section, Projects, or Work Experience) to prioritize evidenced skills.

4. **Weighted ATS Evaluation Engine**:
   - Section quality scoring across calibrated weights: Skills (25%), Experience (20%), Projects (20%), Education (15%), Certifications (5%), Contact (5%), Summary (5%), and Formatting (5%).
   - Action verb quantification (e.g., *architected*, *optimized*, *streamlined*) vs. weak passive phrases (*responsible for*, *worked on*).
   - Metrics verification: scans for numbers, percentages, currency, and scale.
   - Actionable recommendations categorized by priority: **HIGH** (critical fixes), **MEDIUM**, and **LOW**.

5. **Career Pathway Matching & Skill-Gap Roadmap**:
   - Inferred role recommendations combining required/optional skill coverage with TF-IDF cosine text similarity.
   - Clear identification of matched skills, missing required skills, and missing nice-to-have skills.
   - **Prioritized Learning Roadmap**: Ranks highest-leverage skills to acquire based on multi-role demand.

6. **Curated Job Openings Marketplace & Ad-Hoc JD Matching**:
   - 25+ curated real-world job openings across top companies (Swiggy, Razorpay, Amazon, Flipkart, Infosys, Zomato, etc.).
   - Interactive search and filters by Location (Bengaluru, Remote, Hyderabad, Pune, Mumbai, Delhi-NCR) and Job Type (Full-time, Internship).
   - Custom Target Job Description input: paste any job posting to calculate custom fit score, semantic similarity, and skill gaps.

7. **Exportable Reports**:
   - One-click downloads for formatted **Markdown** (`.md`) and structured **JSON** (`.json`) evaluation summaries.

---

## 🎨 UI & Stitch Design System Integration

This application's UI was designed using **Google Stitch** (`projects/17581744796650278518`):
- **Theme**: Deep obsidian/dark indigo workspace (`#031427` / `#0B0F19`) with indigo primary accents (`#6366F1` / `#8083FF`) and emerald secondary highlights (`#14B8A6` / `#2DD4BF`).
- **Typography**: Geometric UI chrome with **Geist** paired with monospace numerical metrics in **JetBrains Mono**.
- **Interactive Visualizations**: Plotly ATS score gauge and horizontal section score distribution.

---

## 📁 Project Structure

```
ujwals_portfolio_website/
├── app.py                      # Main Streamlit application
├── config.py                   # Configuration constants, weights, and file limits
├── pipeline.py                 # Core analysis orchestrator
├── run_app.bat                 # One-click Windows application launcher
├── run_tests.bat               # One-click Windows test suite runner
├── requirements.txt            # Pinned dependencies
├── PRD.md                      # Product Requirements Document
├── systemdesign.md             # System Design Document
├── README.md                   # Project documentation
│
├── modules/                    # Modular service components
│   ├── parser.py               # File validation & text extraction (pdfplumber, docx)
│   ├── cleaner.py              # Text cleaning & unicode normalization
│   ├── section_extractor.py    # Heading segmentation & contact regex
│   ├── skill_extractor.py      # Taxonomy lookup & fuzzy alias matching
│   ├── analyzer.py             # Section scoring, metrics, & suggestions
│   ├── role_matcher.py         # Role ranking & skill-gap analysis
│   ├── job_providers.py        # Local & Adzuna job source providers
│   ├── job_matcher.py          # Job ranking & target JD fit scorer
│   └── report.py               # JSON & Markdown report generator
│
├── data/                       # Configurable data definitions
│   ├── skills.json             # Canonical skill taxonomy with aliases
│   ├── roles.json              # Job role definitions with required/optional skills
│   └── jobs.json               # Curated sample job openings
│
├── ui/                         # Presentation components
│   └── components.py           # Gauge chart, score bars, chips, & cards
│
├── samples/                    # Pre-loaded test resumes
│   ├── sample_software_engineer.docx
│   ├── sample_data_analyst.pdf
│   └── sample_fresher.docx
│
└── tests/                      # Pytest unit & integration test suite
    ├── test_parser.py
    ├── test_cleaner.py
    ├── test_section_extractor.py
    ├── test_skill_extractor.py
    ├── test_analyzer.py
    ├── test_matchers.py
    └── test_pipeline.py
```

---

## 🛠️ Installation & Quick Start

### 1. Prerequisites
- Python 3.10 or 3.11 installed.

### 2. Run with One-Click Batch Script (Windows)
Double-click `run_app.bat` or execute in PowerShell:
```powershell
.\run_app.bat
```

### 3. Or Run Manually via CLI
```powershell
# Set PYTHONPATH to include virtualenv packages
$env:PYTHONPATH = "$PWD;$PWD\.venv\Lib\site-packages"

# Launch Streamlit
python -m streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 Running Tests

Execute the full unit and integration test suite:
```powershell
.\run_tests.bat
```
Output:
```
============================= test session starts =============================
tests/test_analyzer.py::test_evaluate_contact PASSED                     [  5%]
tests/test_analyzer.py::test_analyze_resume_content_scoring_bounds PASSED [ 11%]
tests/test_cleaner.py::test_normalize_bullets_and_whitespace PASSED      [ 17%]
tests/test_cleaner.py::test_normalize_hyphenated_line_breaks PASSED      [ 23%]
tests/test_matchers.py::test_role_matcher PASSED                         [ 29%]
tests/test_matchers.py::test_job_matcher PASSED                          [ 35%]
tests/test_matchers.py::test_target_jd_matching PASSED                   [ 41%]
tests/test_parser.py::test_validate_file_unsupported_format PASSED       [ 47%]
tests/test_parser.py::test_validate_file_too_large PASSED                [ 52%]
tests/test_parser.py::test_validate_file_empty PASSED                    [ 58%]
tests/test_parser.py::test_extract_text_docx PASSED                      [ 64%]
tests/test_pipeline.py::test_pipeline_on_software_engineer_sample PASSED [ 70%]
tests/test_pipeline.py::test_pipeline_on_data_analyst_sample PASSED      [ 76%]
tests/test_section_extractor.py::test_contact_extraction PASSED          [ 82%]
tests/test_section_extractor.py::test_heading_matcher PASSED             [ 88%]
tests/test_section_extractor.py::test_section_segmentation PASSED        [ 94%]
tests/test_skill_extractor.py::test_skill_extraction_and_alias PASSED    [100%]

============================= 17 passed in 10.46s =============================
```

---

## 🔒 Security & Privacy
- **100% In-Memory Processing**: Resumes are parsed and analyzed in transient memory. No user documents or sensitive personal data are persisted or uploaded to external servers.
- **Offline Capable**: Works entirely offline with the curated local dataset and scikit-learn TF-IDF engine.

