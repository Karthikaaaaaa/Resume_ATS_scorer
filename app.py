import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from utils.pdf_parser import extract_text_from_pdf
from graph.ats_graph import run_ats_scorer

# ── Page Config ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Resume ATS Scorer",
    page_icon="📄",
    layout="wide"
)

# ── Custom CSS ────────────────────────────────────────────────────
st.markdown("""
<style>
    .score-card {
        background: linear-gradient(135deg, #1B3A6B, #2C5F9E);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        color: white;
        margin-bottom: 20px;
    }
    .score-number {
        font-size: 64px;
        font-weight: 700;
        line-height: 1;
    }
    .score-label {
        font-size: 16px;
        opacity: 0.85;
        margin-top: 6px;
    }
    .metric-card {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        border: 1px solid #e0e0e0;
    }
    .keyword-chip-matched {
        display: inline-block;
        background: #E1F5EE;
        color: #085041;
        padding: 3px 10px;
        border-radius: 99px;
        font-size: 12px;
        margin: 3px;
        font-weight: 500;
    }
    .keyword-chip-missing {
        display: inline-block;
        background: #FCEBEB;
        color: #A32D2D;
        padding: 3px 10px;
        border-radius: 99px;
        font-size: 12px;
        margin: 3px;
        font-weight: 500;
    }
    .suggestion-box {
        background: #E6F1FB;
        border-left: 4px solid #185FA5;
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        margin-bottom: 10px;
        color: #0C447C;
        font-size: 14px;
    }
    .summary-box {
        background: #f0f7ff;
        border: 1px solid #b5d4f4;
        border-radius: 12px;
        padding: 16px;
        font-size: 14px;
        line-height: 1.7;
        color: #1a1a1a;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────
st.title("📄 Resume ATS Scorer")
st.markdown("*Upload your resume and paste a job description — get your ATS match score, gap analysis, and an AI-improved summary instantly.*")
st.divider()

# ── Input Section ─────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Your Resume")
    uploaded_file = st.file_uploader(
        "Upload your resume (PDF)",
        type=["pdf"],
        help="Upload your resume as a PDF file"
    )
    if uploaded_file:
        st.success(f"✅ {uploaded_file.name} uploaded successfully")

with col2:
    st.subheader("💼 Job Description")
    jd_text = st.text_area(
        "Paste the job description here",
        height=250,
        placeholder="Paste the full job description here...\n\nInclude responsibilities, requirements, and preferred qualifications for the best analysis.",
        help="Paste the complete job description for accurate ATS scoring"
    )

st.divider()

# ── Analyse Button ─────────────────────────────────────────────────
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
with col_btn2:
    analyse_btn = st.button(
        "🔍 Analyse My Resume",
        use_container_width=True,
        type="primary"
    )

# ── Results ───────────────────────────────────────────────────────
if analyse_btn:
    if not uploaded_file:
        st.error("Please upload your resume PDF first.")
    elif not jd_text.strip():
        st.error("Please paste the job description.")
    else:
        with st.spinner("🤖 Analysing your resume... This may take 30–60 seconds on first run (model loading)"):

            # Extract resume text
            resume_text = extract_text_from_pdf(uploaded_file)

            if resume_text.startswith("Error"):
                st.error(f"Could not read PDF: {resume_text}")
            else:
                # Run ATS pipeline
                result = run_ats_scorer(resume_text, jd_text)

                st.success("✅ Analysis complete!")
                st.divider()

                # ── Score Cards ──────────────────────────────────────
                st.subheader("📊 Your ATS Score")
                c1, c2, c3 = st.columns(3)

                with c1:
                    score = result["final_score"]
                    color = "#1D9E75" if score >= 70 else "#BA7517" if score >= 50 else "#A32D2D"
                    st.markdown(f"""
                    <div class="score-card" style="background: {color};">
                        <div class="score-number">{score}%</div>
                        <div class="score-label">Overall ATS Score</div>
                    </div>
                    """, unsafe_allow_html=True)

                with c2:
                    kw_score = result["ats_score"]
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="font-size:36px; font-weight:700; color:#1B3A6B;">{kw_score}%</div>
                        <div style="font-size:13px; color:#555; margin-top:4px;">Keyword Match</div>
                    </div>
                    """, unsafe_allow_html=True)

                with c3:
                    sem_score = result["semantic_score"]
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="font-size:36px; font-weight:700; color:#1B3A6B;">{sem_score}%</div>
                        <div style="font-size:13px; color:#555; margin-top:4px;">Semantic Similarity</div>
                    </div>
                    """, unsafe_allow_html=True)

                # Score interpretation
                if score >= 75:
                    st.success("🎉 Strong match! Your resume is well-aligned with this job description.")
                elif score >= 55:
                    st.warning("⚡ Good match with room to improve. Apply the suggestions below for a stronger application.")
                else:
                    st.error("⚠️ Low match. Review the missing keywords and suggestions carefully before applying.")

                st.divider()

                # ── Keywords Analysis ────────────────────────────────
                st.subheader("🔑 Keyword Analysis")
                kw_col1, kw_col2 = st.columns(2)

                with kw_col1:
                    st.markdown(f"**✅ Matched Keywords** ({len(result['matched_keywords'])})")
                    if result["matched_keywords"]:
                        chips = "".join([
                            f'<span class="keyword-chip-matched">{kw}</span>'
                            for kw in result["matched_keywords"]
                        ])
                        st.markdown(chips, unsafe_allow_html=True)
                    else:
                        st.info("No keyword matches found.")

                with kw_col2:
                    st.markdown(f"**❌ Missing Keywords** ({len(result['missing_keywords'])})")
                    if result["missing_keywords"]:
                        chips = "".join([
                            f'<span class="keyword-chip-missing">{kw}</span>'
                            for kw in result["missing_keywords"]
                        ])
                        st.markdown(chips, unsafe_allow_html=True)
                    else:
                        st.success("No critical keywords missing!")

                st.divider()

                # ── Suggestions ──────────────────────────────────────
                st.subheader("💡 How to Improve Your Resume")
                for i, suggestion in enumerate(result["suggestions"], 1):
                    st.markdown(f'<div class="suggestion-box">💡 {suggestion}</div>', unsafe_allow_html=True)

                st.divider()

                # ── Improved Summary ─────────────────────────────────
                st.subheader("✍️ AI-Improved Professional Summary")
                st.markdown("*Rewritten to include missing keywords and better match this specific JD:*")
                st.markdown(f'<div class="summary-box">{result["improved_summary"]}</div>', unsafe_allow_html=True)

                col_copy1, col_copy2 = st.columns([1, 3])
                with col_copy1:
                    st.download_button(
                        "📋 Copy Summary",
                        data=result["improved_summary"],
                        file_name="improved_summary.txt",
                        mime="text/plain"
                    )

                # ── Error Display (dev mode) ──────────────────────────
                if result.get("error"):
                    with st.expander("⚠️ Debug info"):
                        st.warning(result["error"])

# ── Footer ────────────────────────────────────────────────────────
st.divider()
st.markdown("""
<div style="text-align: center; color: #888; font-size: 12px;">
    Built with LangGraph · HuggingFace · ChromaDB · Streamlit<br>
    <a href="https://github.com/Karthikaaaaaa" style="color: #1B3A6B;">github.com/Karthikaaaaaa</a>
</div>
""", unsafe_allow_html=True)
