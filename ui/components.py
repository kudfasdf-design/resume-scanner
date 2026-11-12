"""UI components for Streamlit presentation styled with Stitch Design System tokens."""

from typing import Dict, Any, List
import streamlit as st
import plotly.graph_objects as go


def render_custom_css():
    """Inject customized CSS styling inspired by the Stitch design system."""
    st.markdown("""
        <style>
        /* Import JetBrains Mono */
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap');

        /* Theme tweaks */
        .metric-card {
            background: #102034;
            border: 1px solid #1E293B;
            border-radius: 6px;
            padding: 14px 18px;
            margin-bottom: 12px;
        }
        .metric-title {
            font-size: 11px;
            font-family: 'JetBrains Mono', monospace;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #94A3B8;
        }
        .metric-val {
            font-size: 26px;
            font-weight: 700;
            color: #F8FAFC;
            margin-top: 4px;
        }
        .skill-pill {
            display: inline-block;
            background: #0E1422;
            border: 1px solid #1E293B;
            color: #E2E8F0;
            padding: 3px 8px;
            font-size: 11px;
            border-radius: 4px;
            margin: 2px 4px 2px 0;
            font-family: 'JetBrains Mono', monospace;
        }
        .skill-pill-evidenced {
            border-color: #14B8A6;
            color: #2DD4BF;
            background: rgba(20, 184, 166, 0.12);
        }
        .role-card {
            background: #0B132B;
            border: 1px solid #1E293B;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 16px;
        }
        .job-card {
            background: #0E1A2D;
            border: 1px solid #1E293B;
            border-radius: 6px;
            padding: 14px;
            margin-bottom: 12px;
        }
        .badge-high {
            background: rgba(244, 63, 94, 0.15);
            border: 1px solid #F43F5E;
            color: #FDA4AF;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
        }
        .badge-medium {
            background: rgba(245, 158, 11, 0.15);
            border: 1px solid #F59E0B;
            color: #FCD34D;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
        }
        .badge-low {
            background: rgba(99, 102, 241, 0.15);
            border: 1px solid #6366F1;
            color: #C7D2FE;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
        }
        .missing-pill-req {
            background: rgba(244, 63, 94, 0.1);
            border: 1px dashed #F43F5E;
            color: #FDA4AF;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 11px;
            margin: 2px 4px 2px 0;
            display: inline-block;
        }
        .missing-pill-opt {
            background: rgba(245, 158, 11, 0.1);
            border: 1px dashed #F59E0B;
            color: #FCD34D;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 11px;
            margin: 2px 4px 2px 0;
            display: inline-block;
        }
        </style>
    """, unsafe_allow_html=True)


def render_score_gauge(score: float):
    """Plotly radial gauge chart for overall ATS score."""
    if score >= 75:
        bar_color = "#14B8A6"  # Emerald
    elif score >= 50:
        bar_color = "#F59E0B"  # Amber
    else:
        bar_color = "#F43F5E"  # Rose

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "ATS Readiness Score", 'font': {'size': 16, 'color': '#E2E8F0'}},
        number={'font': {'size': 44, 'color': '#FFFFFF'}, 'suffix': "/100"},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#475569"},
            'bar': {'color': bar_color, 'thickness': 0.75},
            'bgcolor': "#0B1426",
            'borderwidth': 1,
            'bordercolor': "#1E293B",
            'steps': [
                {'range': [0, 50], 'color': 'rgba(244, 63, 94, 0.08)'},
                {'range': [50, 75], 'color': 'rgba(245, 158, 11, 0.08)'},
                {'range': [75, 100], 'color': 'rgba(20, 184, 166, 0.08)'}
            ],
            'threshold': {
                'line': {'color': "#818CF8", 'width': 3},
                'thickness': 0.8,
                'value': score
            }
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=260,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)


def render_section_scores_bar(section_reports: Dict[str, Any]):
    """Horizontal bar chart showing scores per section."""
    sections = [s.capitalize() for s in section_reports.keys()]
    scores = [rep["score"] for rep in section_reports.values()]
    colors = [
        "#14B8A6" if sc >= 75 else "#F59E0B" if sc >= 50 else "#F43F5E"
        for sc in scores
    ]

    fig = go.Figure(go.Bar(
        x=scores,
        y=sections,
        orientation='h',
        marker=dict(color=colors, line=dict(color='#1E293B', width=1)),
        text=[f"{sc}/100" for sc in scores],
        textposition='outside',
        textfont=dict(color='#CBD5E1', size=11, family='JetBrains Mono')
    ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(range=[0, 115], showgrid=True, gridcolor='#1E293B', tickfont=dict(color='#94A3B8')),
        yaxis=dict(autorange="reversed", tickfont=dict(color='#E2E8F0', size=12)),
        height=280,
        margin=dict(l=10, r=20, t=10, b=10)
    )
    st.plotly_chart(fig, use_container_width=True)


def render_contact_header(contact: Dict[str, Any]):
    """Display extracted candidate identity and contact badges."""
    name = contact.get("name", "Candidate")
    email = contact.get("email") or "Not detected"
    phone = contact.get("phone") or "Not detected"
    linkedin = contact.get("linkedin") or "Not detected"
    github = contact.get("github") or "Not detected"

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown(f"### 👤 {name}")
        st.markdown(f"📧 **Email:** `{email}` &nbsp;&nbsp;|&nbsp;&nbsp; 📱 **Phone:** `{phone}`")
    with col2:
        st.markdown("#### Career Presence")
        li_link = f"[{linkedin}]({linkedin})" if contact.get("linkedin") else "`Not found`"
        gh_link = f"[{github}]({github})" if contact.get("github") else "`Not found`"
        st.markdown(f"🔗 **LinkedIn:** {li_link}")
        st.markdown(f"💻 **GitHub:** {gh_link}")


def render_skill_chips(skills: Dict[str, Any]):
    """Render categorized skill badges with occurrence counts and project evidence."""
    categories: Dict[str, List[Dict[str, Any]]] = {}
    for name, data in skills.items():
        cat = data.get("category", "General")
        categories.setdefault(cat, []).append({"name": name, **data})

    for cat_name in sorted(categories.keys()):
        st.markdown(f"**{cat_name}** ({len(categories[cat_name])})")
        chips_html = ""
        for item in sorted(categories[cat_name], key=lambda x: x["name"]):
            name = item["name"]
            count = item.get("count", 1)
            evidenced = item.get("evidenced", False)
            class_name = "skill-pill skill-pill-evidenced" if evidenced else "skill-pill"
            check = "✓ " if evidenced else ""
            chips_html += f'<span class="{class_name}" title="Found in {", ".join(item.get("sources", []))}">{check}{name} <small style="opacity:0.7">({count}x)</small></span>'
        st.markdown(chips_html, unsafe_allow_html=True)
        st.write("")


def render_suggestions(suggestions: List[Dict[str, Any]]):
    """Render prioritized suggestions with color-coded priority badges."""
    if not suggestions:
        st.success("No critical issues found! Your resume adheres to standard structure and formatting.")
        return

    for s in suggestions:
        priority = s.get("priority", "Medium")
        badge_class = f"badge-{priority.lower()}"
        section = s.get("section", "General")
        msg = s.get("message", "")

        st.markdown(f"""
            <div style="background: #0E1626; border-left: 3px solid {'#F43F5E' if priority=='High' else '#F59E0B' if priority=='Medium' else '#6366F1'}; border-radius: 4px; padding: 10px 14px; margin-bottom: 8px;">
                <span class="{badge_class}">{priority}</span>
                <strong style="color: #F1F5F9; margin-left: 8px;">{section}:</strong>
                <span style="color: #CBD5E1; margin-left: 4px;">{msg}</span>
            </div>
        """, unsafe_allow_html=True)


def render_role_cards(roles: List[Dict[str, Any]]):
    """Render top recommended role cards with match %, matched and missing skill tags."""
    for idx, r in enumerate(roles, 1):
        role_name = r.get("role")
        pct = r.get("match_percent", 0)
        desc = r.get("description", "")
        matched = r.get("matched_skills", [])
        missing_req = r.get("missing_required", [])
        missing_opt = r.get("missing_optional", [])

        color = "#14B8A6" if pct >= 75 else "#8083FF" if pct >= 55 else "#F59E0B"

        st.markdown(f"""
            <div class="role-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <h4 style="margin: 0; color: #FFFFFF; font-size: 18px;">#{idx} {role_name}</h4>
                    <span style="background: rgba(20, 184, 166, 0.15); border: 1px solid {color}; color: {color}; padding: 4px 10px; border-radius: 4px; font-weight: 700; font-family: 'JetBrains Mono'; font-size: 14px;">
                        {pct}% Match
                    </span>
                </div>
                <p style="color: #94A3B8; font-size: 13px; margin-bottom: 12px;">{desc}</p>
                <div>
                    <strong style="color: #2DD4BF; font-size: 12px;">Matched Skills ({len(matched)}):</strong><br>
                    {''.join([f'<span class="skill-pill skill-pill-evidenced">{s}</span>' for s in matched]) if matched else '<span style="color:#64748B; font-size:12px;">None detected</span>'}
                </div>
                <div style="margin-top: 8px;">
                    <strong style="color: #FDA4AF; font-size: 12px;">Missing Required Skills ({len(missing_req)}):</strong><br>
                    {''.join([f'<span class="missing-pill-req">⚠️ {s}</span>' for s in missing_req]) if missing_req else '<span style="color:#2DD4BF; font-size:12px;">All core requirements met!</span>'}
                </div>
                {f'<div style="margin-top: 8px;"><strong style="color: #FCD34D; font-size: 12px;">Missing Nice-to-Have Skills:</strong><br>' + ''.join([f'<span class="missing-pill-opt">{s}</span>' for s in missing_opt]) + '</div>' if missing_opt else ''}
            </div>
        """, unsafe_allow_html=True)


def render_job_cards(jobs: List[Dict[str, Any]]):
    """Render curated and realtime job openings cards."""
    for j in jobs:
        pct = j.get("match_percent", 0)
        title = j.get("title", "")
        company = j.get("company", "")
        loc = j.get("location", "")
        jtype = j.get("job_type", "")
        desc = j.get("description", "")
        matched = j.get("matched_skills", [])
        gap = j.get("skill_gap", [])
        url = j.get("url", "#")
        is_live = j.get("is_live", False)

        fit_color = "#14B8A6" if pct >= 75 else "#8083FF" if pct >= 55 else "#94A3B8"
        live_badge = '<span style="background: rgba(16, 185, 129, 0.2); border: 1px solid #10B981; color: #34D399; font-size: 10px; font-weight: 700; padding: 2px 6px; border-radius: 4px; margin-left: 6px; font-family: monospace;">● LIVE REALTIME</span>' if is_live else ''

        st.markdown(f"""
            <div class="job-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <div style="display: flex; align-items: center;">
                            <h4 style="margin: 0; color: #FFFFFF; font-size: 16px;">{title}</h4>
                            {live_badge}
                        </div>
                        <div style="color: #94A3B8; font-size: 13px; margin-top: 2px;">
                            <strong>{company}</strong> • 📍 {loc} • 💼 {jtype}
                        </div>
                    </div>
                    <span style="background: rgba(99, 102, 241, 0.15); border: 1px solid {fit_color}; color: {fit_color}; padding: 3px 8px; border-radius: 4px; font-weight: 700; font-family: 'JetBrains Mono'; font-size: 13px;">
                        {pct}% Fit
                    </span>
                </div>
                <p style="color: #CBD5E1; font-size: 12.5px; margin: 8px 0; line-height: 1.4;">{desc}</p>
                <div style="margin-bottom: 6px;">
                    <span style="color: #2DD4BF; font-size: 11px; font-weight: 600;">Matched:</span>
                    {' '.join([f'<span class="skill-pill">{s}</span>' for s in matched]) if matched else '<span style="color:#64748B; font-size:11px;">None</span>'}
                </div>
                {f'<div style="margin-bottom: 8px;"><span style="color: #FDA4AF; font-size: 11px; font-weight: 600;">Skill Gap:</span> ' + ' '.join([f'<span class="missing-pill-req">{s}</span>' for s in gap]) + '</div>' if gap else ''}
                <div style="margin-top: 8px;">
                    <a href="{url}" target="_blank" style="display: inline-block; background: #6366F1; color: #FFFFFF; padding: 4px 12px; border-radius: 4px; text-decoration: none; font-size: 12px; font-weight: 600;">
                        Apply Now ↗
                    </a>
                </div>
            </div>
        """, unsafe_allow_html=True)


def render_ai_analysis(ai_data: Dict[str, Any]):
    """Render Gemini AI deep resume analysis, executive rewrite, and interview tips."""
    if not ai_data:
        st.info("Gemini AI analysis is loading or key is not set. Toggle AI analysis in the sidebar.")
        return

    # 1. Executive assessment banner
    feedback = ai_data.get("ai_overall_feedback", "")
    rating = ai_data.get("market_fit_rating", "Solid")
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.12), rgba(168, 85, 247, 0.12)); border: 1px solid #8083FF; border-radius: 8px; padding: 16px 20px; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 20px;">✨</span>
                    <strong style="color: #E0E7FF; font-size: 16px;">Gemini Senior Recruiter Appraisal</strong>
                </div>
                <span style="background: rgba(20, 184, 166, 0.2); border: 1px solid #14B8A6; color: #2DD4BF; padding: 3px 10px; border-radius: 4px; font-size: 12px; font-weight: 700; font-family: 'JetBrains Mono';">
                    Market Fit: {rating}
                </span>
            </div>
            <p style="color: #F1F5F9; font-size: 14px; margin: 0; line-height: 1.5;">{feedback}</p>
        </div>
    """, unsafe_allow_html=True)

    # 2. Executive Summary Proposed Rewrite
    summary_data = ai_data.get("executive_summary_critique", {})
    if summary_data:
        st.markdown("#### ✍️ Executive Summary Rewrite Recommendation")
        c_left, c_right = st.columns(2)
        with c_left:
            st.markdown("""
                <div style="background: #0E1626; border: 1px solid #1E293B; border-radius: 6px; padding: 14px; height: 100%;">
                    <div style="color: #FDA4AF; font-size: 11px; font-weight: 700; text-transform: uppercase; margin-bottom: 6px;">
                        Current Summary Critique
                    </div>
                    <p style="color: #94A3B8; font-size: 13px; line-height: 1.5;">
            """ + str(summary_data.get("current_critique", "Summary could be sharper.")) + """
                    </p>
                </div>
            """, unsafe_allow_html=True)
        with c_right:
            st.markdown("""
                <div style="background: rgba(20, 184, 166, 0.08); border: 1px solid #14B8A6; border-radius: 6px; padding: 14px; height: 100%;">
                    <div style="color: #2DD4BF; font-size: 11px; font-weight: 700; text-transform: uppercase; margin-bottom: 6px;">
                        ✨ Gemini Proposed High-Impact Rewrite
                    </div>
                    <p style="color: #F8FAFC; font-size: 13px; line-height: 1.5; font-style: italic;">
                        " """ + str(summary_data.get("proposed_rewrite", "")) + """ "
                    </p>
                </div>
            """, unsafe_allow_html=True)

    st.write("")

    # 3. Bullet Point Improvements (XYZ Formula)
    bullets = ai_data.get("bullet_point_improvements", [])
    if bullets:
        st.markdown("#### 🎯 Bullet Point Optimization (Google X-Y-Z Formula)")
        st.caption("Google's Formula: 'Accomplished [X], as measured by [Y], by doing [Z]'")
        for b in bullets:
            st.markdown(f"""
                <div style="background: #0E1A2D; border: 1px solid #1E293B; border-radius: 6px; padding: 14px; margin-bottom: 12px;">
                    <div style="margin-bottom: 8px;">
                        <span style="background: rgba(244, 63, 94, 0.15); border: 1px solid #F43F5E; color: #FDA4AF; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 700;">BEFORE (PASSIVE)</span>
                        <div style="color: #94A3B8; font-size: 13px; margin-top: 4px; padding-left: 8px; border-left: 2px solid #334155;">{b.get('original', '')}</div>
                    </div>
                    <div style="margin-bottom: 8px;">
                        <span style="background: rgba(20, 184, 166, 0.15); border: 1px solid #14B8A6; color: #2DD4BF; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 700;">AFTER (IMPACT DRIVEN)</span>
                        <div style="color: #F8FAFC; font-size: 13px; font-weight: 500; margin-top: 4px; padding-left: 8px; border-left: 2px solid #14B8A6;">{b.get('improved', '')}</div>
                    </div>
                    <div style="color: #8083FF; font-size: 11px; margin-top: 4px;">
                        💡 <strong>Why recruiters prefer this:</strong> {b.get('why_better', '')}
                    </div>
                </div>
            """, unsafe_allow_html=True)

    # 4. Missing Keywords & Recruiter Tips
    col_k, col_t = st.columns([1, 1.2])
    with col_k:
        keywords = ai_data.get("missing_high_impact_keywords", [])
        st.markdown("#### 🔑 Missing High-Impact Keywords")
        st.caption("Keywords that automated ATS filters scan for:")
        for kw in keywords:
            st.markdown(f"""
                <span class="skill-pill" style="border-color: #8083FF; color: #C7D2FE;">+ {kw}</span>
            """, unsafe_allow_html=True)

    with col_t:
        tips = ai_data.get("recruiter_interview_tips", [])
        st.markdown("#### 🎙️ Senior Recruiter Interview Coaching")
        for tip in tips:
            st.markdown(f"""
                <div style="background: #102034; border-left: 3px solid #8083FF; padding: 8px 12px; margin-bottom: 6px; border-radius: 4px; font-size: 12.5px; color: #E2E8F0;">
                    {tip}
                </div>
            """, unsafe_allow_html=True)


