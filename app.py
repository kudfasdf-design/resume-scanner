"""Streamlit Web Application: AI-Based Resume Screening and Job Recommendation System."""

import streamlit as st
import pandas as pd
from pipeline import analyze_resume, AnalysisResult
from modules.report import generate_json_report, generate_markdown_report
from ui.components import (
    render_custom_css,
    render_score_gauge,
    render_section_scores_bar,
    render_contact_header,
    render_skill_chips,
    render_suggestions,
    render_role_cards,
    render_job_cards,
    render_ai_analysis
)
from config import DEFAULT_TOP_N_ROLES, SECTION_WEIGHTS, SAMPLES_DIR

# Set page config
st.set_page_config(
    page_title="ResumeAI — Intelligent ATS Screening & Job Matcher",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Render customized styling
render_custom_css()

# Initialize session state
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "current_filename" not in st.session_state:
    st.session_state.current_filename = None

# Sidebar
st.sidebar.markdown("### ⚙️ Analysis Settings")
top_n = st.sidebar.slider("Top Roles Count", min_value=1, max_value=10, value=DEFAULT_TOP_N_ROLES)
location_filter = st.sidebar.selectbox(
    "Preferred Job Location",
    ["All", "Remote", "Bengaluru", "Hyderabad", "Pune", "Mumbai", "Delhi-NCR"]
)
enable_ai = st.sidebar.checkbox("✨ Enable Gemini AI Deep Recruiter Critique", value=True, help="Uses Google Gemini Flash to generate deep executive summary rewrites and Google XYZ bullet improvements.")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 Target Job Fit (Optional)")
target_jd = st.sidebar.text_area(
    "Target Job Description",
    placeholder="Paste a job description here to calculate semantic fit score and keyword gaps...",
    height=120
)

st.sidebar.markdown("---")
with st.sidebar.expander("⚖️ ATS Scoring Calibration", expanded=False):
    for sec, w in SECTION_WEIGHTS.items():
        st.write(f"• **{sec.capitalize()}:** {w}%")
    st.caption("Weights are calibrated to 100% total according to PRD specifications.")

# Pre-loaded sample resumes in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 📂 Pre-Loaded Samples")
col_s1, col_s2 = st.sidebar.columns(2)

sample_se_path = SAMPLES_DIR / "sample_software_engineer.docx"
sample_da_path = SAMPLES_DIR / "sample_data_analyst.pdf"
sample_fr_path = SAMPLES_DIR / "sample_fresher.docx"

if col_s1.button("Dev Sample", use_container_width=True):
    if sample_se_path.exists():
        with open(sample_se_path, "rb") as f:
            st.session_state.analysis_result = analyze_resume(
                f.read(), "sample_software_engineer.docx",
                target_jd=target_jd, location=location_filter, top_n_roles=top_n,
                enable_ai=enable_ai
            )
            st.session_state.current_filename = "sample_software_engineer.docx"

if col_s2.button("Analyst Sample", use_container_width=True):
    if sample_da_path.exists():
        with open(sample_da_path, "rb") as f:
            st.session_state.analysis_result = analyze_resume(
                f.read(), "sample_data_analyst.pdf",
                target_jd=target_jd, location=location_filter, top_n_roles=top_n,
                enable_ai=enable_ai
            )
            st.session_state.current_filename = "sample_data_analyst.pdf"


# Main Header
st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1E293B; padding-bottom: 12px; margin-bottom: 20px;">
        <div>
            <h1 style="margin: 0; font-size: 26px; color: #FFFFFF; font-weight: 700;">
                ResumeAI <span style="font-size: 14px; color: #8083FF; font-weight: 500; border: 1px solid #1E293B; padding: 2px 8px; border-radius: 4px; margin-left: 8px;">v1.0 • Stitch Enhanced</span>
            </h1>
            <p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 13px;">
                Intelligent ATS Screening, Canonical Taxonomy Extraction & Career Pathway Recommendation
            </p>
        </div>
        <div style="background: rgba(20, 184, 166, 0.12); border: 1px solid #14B8A6; border-radius: 20px; padding: 4px 12px; color: #2DD4BF; font-size: 12px; font-family: monospace;">
            ● Engine: Rule-Based & NLP Offline Ready
        </div>
    </div>
""", unsafe_allow_html=True)

# Upload Area
uploaded_file = st.file_uploader(
    "Upload your resume (PDF or DOCX)",
    type=["pdf", "docx"],
    help="Supported formats: PDF (text-based) or DOCX up to 5 MB"
)

if uploaded_file is not None:
    if st.session_state.current_filename != uploaded_file.name:
        with st.spinner("Analyzing document structure, querying Gemini AI recruiter & fetching real-time jobs..."):
            try:
                file_bytes = uploaded_file.read()
                result = analyze_resume(
                    file_bytes=file_bytes,
                    filename=uploaded_file.name,
                    target_jd=target_jd,
                    location=location_filter,
                    top_n_roles=top_n,
                    enable_ai=enable_ai
                )
                st.session_state.analysis_result = result
                st.session_state.current_filename = uploaded_file.name
                st.success("Resume processed successfully!")
            except Exception as e:
                st.error(f"Analysis Error: {str(e)}")

# Display Analysis if available
result: AnalysisResult = st.session_state.analysis_result

if result:
    # Top Identity strip
    render_contact_header(result.contact)
    st.markdown("---")

    # Tabs
    tab1, tab_ai, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Overview",
        "✨ Gemini AI Recruiter Deep Dive",
        "📑 Section Analysis",
        "💡 Skill Taxonomy",
        "🎯 Actionable Suggestions",
        "🧭 Recommended Roles",
        "💼 Real-Time & Curated Jobs",
        "📥 Export Report"
    ])

    with tab1:
        # Overview tab
        col_g, col_b = st.columns([1, 1.2])
        with col_g:
            render_score_gauge(result.overall_score)
        with col_b:
            st.markdown("#### Section Scoring Breakdown")
            render_section_scores_bar(result.section_reports)

        # Quick stats row
        st.markdown(f"""
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 16px 0;">
                <div class="metric-card">
                    <div class="metric-title">Word Count</div>
                    <div class="metric-val">{result.word_count}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">Skills Extracted</div>
                    <div class="metric-val">{len(result.skills)}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">Sections Detected</div>
                    <div class="metric-val">{len(result.sections)}/7</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">Matched Roles</div>
                    <div class="metric-val">{len(result.roles)}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Strengths & Weaknesses
        col_str, col_weak = st.columns(2)
        with col_str:
            st.markdown("### ✅ Key Strengths")
            if result.strengths:
                for s in result.strengths:
                    st.markdown(f"- {s}")
            else:
                st.info("No standout strengths detected. Review the suggestions tab.")

        with col_weak:
            st.markdown("### ⚠️ Areas for Improvement")
            if result.weaknesses:
                for w in result.weaknesses:
                    st.markdown(f"- {w}")
            else:
                st.success("No critical weaknesses detected!")

    with tab_ai:
        st.markdown("### ✨ Gemini AI Recruiter Deep Dive")
        st.caption("AI-powered resume critique, Google X-Y-Z formula rewrites, missing ATS keywords, and executive coaching powered by Gemini.")
        render_ai_analysis(result.ai_analysis)

    with tab2:
        st.markdown("### 📑 Detailed Section Analysis")
        for sec_name, rep in result.section_reports.items():
            title = sec_name.capitalize()
            score = rep["score"]
            score_badge = "🟢" if score >= 75 else "🟡" if score >= 50 else "🔴"
            with st.expander(f"{score_badge} {title} (Score: {score}/100)"):
                st.markdown(f"**Section Score:** `{score}/100`")
                st.markdown("**Findings:**")
                for f in rep.get("findings", []):
                    st.markdown(f"- {f}")
                if rep.get("suggestions"):
                    st.markdown("**Suggestions:**")
                    for s in rep.get("suggestions", []):
                        st.markdown(f"- *[{s['priority']}]* {s['message']}")
                # Show detected section text if available
                detected_text = result.sections.get(title)
                if detected_text:
                    st.markdown("**Extracted Content:**")
                    st.code(detected_text, language="text")

    with tab3:
        st.markdown("### 💡 Extracted Technical Skills")
        st.caption("Skills mapped to our canonical 7-domain tech taxonomy. Skills marked with ✓ are evidenced in your Projects or Experience.")
        render_skill_chips(result.skills)

    with tab4:
        st.markdown("### 🎯 Actionable Improvement Suggestions")
        st.caption("Prioritized recommendations to boost your ATS pass rate and recruiter interest.")
        render_suggestions(result.suggestions)

    with tab5:
        st.markdown("### 🧭 Recommended Career Pathways")
        st.caption("Roles ranked by required skill overlap and NLP TF-IDF cosine similarity.")

        # Learning priorities alert box
        if result.learning_priorities:
            st.markdown("""
                <div style="background: rgba(168, 85, 247, 0.1); border: 1px solid #A855F7; border-radius: 6px; padding: 12px 16px; margin-bottom: 16px;">
                    <strong style="color: #D8B4FE;">🚀 High-Leverage Skills to Learn First:</strong>
                    <div style="color: #E2E8F0; font-size: 13px; margin-top: 4px;">
                        Acquiring these skills will increase your eligibility across multiple top target roles:
                    </div>
                </div>
            """, unsafe_allow_html=True)
            cols = st.columns(min(4, len(result.learning_priorities)))
            for idx, item in enumerate(result.learning_priorities[:4]):
                with cols[idx]:
                    st.markdown(f"""
                        <div style="background: #102034; border: 1px solid #334155; border-radius: 4px; padding: 8px; text-align: center;">
                            <div style="color: #6366F1; font-weight: 700; font-size: 14px;">#{idx+1} {item['skill']}</div>
                            <div style="color: #94A3B8; font-size: 11px;">Needed in {item['relevance_count']} roles</div>
                        </div>
                    """, unsafe_allow_html=True)
            st.write("")

        render_role_cards(result.roles)

    with tab6:
        st.markdown("### 💼 Curated Job Openings")

        # Custom JD Match card if provided
        if result.target_jd_match:
            jd_res = result.target_jd_match
            st.markdown(f"""
                <div style="background: #0E1626; border: 1px solid #14B8A6; border-radius: 6px; padding: 14px 18px; margin-bottom: 20px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h4 style="margin:0; color:#FFFFFF;">🎯 Custom Job Description Fit Score</h4>
                        <span style="background:rgba(20,184,166,0.2); border:1px solid #14B8A6; color:#2DD4BF; font-size:16px; font-weight:700; padding:4px 10px; border-radius:4px; font-family:monospace;">
                            {jd_res['match_percent']}% Overall Fit
                        </span>
                    </div>
                    <p style="color:#94A3B8; font-size:13px; margin:6px 0;">Text Similarity: {jd_res['text_similarity']}% • Matched Skills in JD: {len(jd_res['matched_skills'])}</p>
                    <div>
                        <strong style="color:#2DD4BF; font-size:12px;">Matched Skills in Target JD:</strong><br>
                        {' '.join([f'<span class="skill-pill skill-pill-evidenced">{s}</span>' for s in jd_res['matched_skills']]) if jd_res['matched_skills'] else '<span>None detected</span>'}
                    </div>
                </div>
            """, unsafe_allow_html=True)

        # Filters
        c_search, c_type = st.columns([2, 1])
        with c_search:
            search_query = st.text_input("Search openings by keyword, title, or company", placeholder="e.g. React, Swiggy, Python...")
        with c_type:
            type_filter = st.selectbox("Job Type", ["All Types", "Full-time", "Internship"])

        filtered_jobs = result.jobs
        if search_query:
            q = search_query.lower()
            filtered_jobs = [
                j for j in filtered_jobs
                if q in j["title"].lower() or q in j["company"].lower() or any(q in s.lower() for s in j["required_skills"])
            ]
        if type_filter != "All Types":
            filtered_jobs = [j for j in filtered_jobs if j["job_type"].lower() == type_filter.lower()]

        st.caption(f"Showing {len(filtered_jobs)} matching job openings")
        render_job_cards(filtered_jobs)

    with tab7:
        st.markdown("### 📥 Download Analysis Report")
        st.markdown("Export your resume evaluation, skill breakdown, recommendations, and job matching report.")

        json_report = generate_json_report(result.to_dict())
        md_report = generate_markdown_report(result.to_dict())

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.download_button(
                label="📄 Download Markdown Report (.md)",
                data=md_report,
                file_name="resume_analysis_report.md",
                mime="text/markdown",
                use_container_width=True
            )
        with col_d2:
            st.download_button(
                label="📦 Download JSON Report (.json)",
                data=json_report,
                file_name="resume_analysis_report.json",
                mime="application/json",
                use_container_width=True
            )

        st.markdown("#### Preview Markdown Report")
        st.code(md_report[:1200] + "\n\n... (truncated for preview)", language="markdown")

else:
    # Empty State - Landing Welcome with Stitch layout cues
    st.info("👆 Please upload a PDF or DOCX resume above, or click on a pre-loaded sample resume in the sidebar to get started.")

    st.markdown("""
        <div style="background: #0B132B; border: 1px solid #1E293B; border-radius: 8px; padding: 24px; margin-top: 16px;">
            <h3 style="color: #FFFFFF; margin-top: 0;">What ResumeAI Analyzes:</h3>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-top: 16px;">
                <div style="background: #102034; padding: 14px; border-radius: 6px; border: 1px solid #1E293B;">
                    <strong style="color: #6366F1;">1. Structural ATS Completeness</strong>
                    <p style="color: #94A3B8; font-size: 13px; margin: 4px 0 0 0;">Evaluates 7 core resume sections: Summary, Skills, Experience, Projects, Education, Certifications, and Contact presence.</p>
                </div>
                <div style="background: #102034; padding: 14px; border-radius: 6px; border: 1px solid #1E293B;">
                    <strong style="color: #14B8A6;">2. Canonical Skill Extraction</strong>
                    <p style="color: #94A3B8; font-size: 13px; margin: 4px 0 0 0;">Fuzzy-matches your proficiencies against an extensive taxonomy with source tracking across projects and work history.</p>
                </div>
                <div style="background: #102034; padding: 14px; border-radius: 6px; border: 1px solid #1E293B;">
                    <strong style="color: #A855F7;">3. Content Impact & Action Verbs</strong>
                    <p style="color: #94A3B8; font-size: 13px; margin: 4px 0 0 0;">Identifies strong action verbs, flags weak passive phrasing, and checks for quantified metrics (numbers, % and scale).</p>
                </div>
                <div style="background: #102034; padding: 14px; border-radius: 6px; border: 1px solid #1E293B;">
                    <strong style="color: #8083FF;">4. Career Pathway & Job Openings</strong>
                    <p style="color: #94A3B8; font-size: 13px; margin: 4px 0 0 0;">Ranks suitable roles, generates a prioritized learning roadmap, and matches live openings with skill gaps.</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

