"""CareerAssist Streamlit dashboard for resume analysis and career guidance."""

from __future__ import annotations

import streamlit as st

from config.llm_config import explain_llm_error
from config.settings import get_settings
from crew.careerassist_crew import CareerAssistCrew
from services.job_service import prepare_job_matches
from services.report_service import build_report
from services.resume_service import prepare_resume, run_resume_analysis
from tools.pdf_extractor import ResumeExtractionError
from utils.formatting import format_percentage
from utils.session_manager import initialize_session_state

st.set_page_config(
    page_title="CareerAssist | Resume & Career Guidance",
    page_icon="CA",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root { --ca-ink: #172b3a; --ca-muted: #60717c; --ca-teal: #0f766e;
            --ca-coral: #d16a4a; --ca-line: #dce5e2; --ca-paper: #fbfcfa; }
    .stApp { background: var(--ca-paper); color: var(--ca-ink); }
    [data-testid="stSidebar"] { background: #edf3f0; border-right: 1px solid var(--ca-line); }
    [data-testid="stSidebar"] h1 { color: var(--ca-ink); font-size: 1.45rem; }
    .ca-kicker { color: var(--ca-teal); font-size: .76rem; font-weight: 700;
                 text-transform: uppercase; letter-spacing: .08em; }
    .ca-title { color: var(--ca-ink); font-size: 2.25rem; line-height: 1.12;
                font-weight: 750; margin: .15rem 0 .5rem; }
    .ca-subtitle { color: var(--ca-muted); max-width: 760px; font-size: 1rem; }
    .ca-rule { height: 3px; width: 54px; background: var(--ca-coral); margin: 1rem 0 1.4rem; }
    div[data-testid="stForm"] { border: 1px solid var(--ca-line); border-radius: 8px;
                                  background: white; padding: 1.2rem 1.3rem; }
    div.stButton > button[kind="primary"] { background: var(--ca-teal); border-color: var(--ca-teal); }
    div.stButton > button[kind="primary"]:hover { background: #095e58; border-color: #095e58; }
    [data-testid="stMetric"] { background: white; border: 1px solid var(--ca-line);
                                border-radius: 7px; padding: .8rem 1rem; }
    .ca-note { border-left: 3px solid var(--ca-coral); padding: .6rem .9rem;
               background: #fff5f0; color: var(--ca-ink); }
    </style>
    """,
    unsafe_allow_html=True,
)

initialize_session_state(st.session_state)
settings = get_settings()

with st.sidebar:
    st.markdown("# CareerAssist")
    st.caption("Resume insight · career direction · interview practice")
    page = st.radio("Navigation", ["Dashboard", "About"], label_visibility="collapsed")
    st.divider()
    st.markdown("**Configuration**")
    if settings.has_api_key:
        st.success("Groq API key configured", icon="✅")
    else:
        st.warning("Groq API key not configured", icon="⚙️")
    st.markdown("**Technology**")
    st.caption("Streamlit · CrewAI · Groq · Sentence Transformers · scikit-learn")
    st.markdown("**About**")
    st.caption("A student-focused career analysis demonstration. Sample roles are illustrative, not live vacancies.")

if page == "About":
    st.markdown('<p class="ca-kicker">Project overview</p>', unsafe_allow_html=True)
    st.markdown('<h1 class="ca-title">CareerAssist</h1>', unsafe_allow_html=True)
    st.markdown(
        "A resume-based career guidance project for students, new graduates, and job seekers. "
        "The application combines deterministic document and matching utilities with four "
        "specialized CrewAI agents.",
    )
    st.markdown("### The four-agent sequence")
    st.markdown(
        "1. **Resume Analyzer** identifies evidence and gaps in the uploaded document.\n"
        "2. **Job Matching** explains the programmatically calculated skill and semantic scores.\n"
        "3. **Career Guidance** turns the resume and match context into a learning roadmap.\n"
        "4. **Interview Preparation** creates role- and resume-specific practice questions."
    )
    st.info(
        "These are four custom-configured CrewAI agents using one shared Groq LLM, not four independently trained models. "
        "Sentence Transformers supplies embeddings for matching and is separate from the Groq LLM."
    )
    st.markdown("### Privacy and limitations")
    st.markdown(
        "The resume is sent to Groq only after you submit an analysis. Do not upload information you are not comfortable "
        "sharing with the configured provider. Resume files and extracted text are not written to disk by this app. "
        "Scanned-image PDFs are not OCR-processed. The bundled job records are sample data, not verified vacancies."
    )
else:
    st.markdown('<p class="ca-kicker">Your next career step</p>', unsafe_allow_html=True)
    st.markdown('<h1 class="ca-title">Make your resume work harder.</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="ca-subtitle">Turn a PDF resume into a grounded profile review, explainable early-career job matches, '
        'a learning roadmap, and focused interview practice.</p>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="ca-rule"></div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="ca-note">Job records in the bundled dataset are illustrative samples, not live vacancies. '
        'Similarity scores describe text alignment, not the chance of being hired.</p>',
        unsafe_allow_html=True,
    )

    with st.form("career_analysis_form"):
        st.subheader("Build your career analysis")
        uploaded_file = st.file_uploader("Resume PDF", type=["pdf"], help="Text-based PDFs are supported. Scanned PDFs require OCR, which is not included.")
        file_col, preference_col, role_col = st.columns([1.1, 1, 1])
        with file_col:
            if uploaded_file:
                st.caption(f"Selected: {uploaded_file.name} · {uploaded_file.size:,} bytes")
        with preference_col:
            preferred_field = st.selectbox(
                "Preferred career field",
                ["Data Science", "Artificial Intelligence", "Machine Learning", "Software Development", "Data Analytics"],
            )
        with role_col:
            target_role = st.selectbox(
                "Target job role",
                ["Any role", "Data Analyst", "Python Developer", "Machine Learning", "AI Engineer", "Business Intelligence Analyst", "Software Engineer"],
            )
        filter_col, location_col, experience_col = st.columns(3)
        with filter_col:
            job_type = st.selectbox("Job type filter", ["All", "Internship", "Entry-level", "Graduate program"])
        with location_col:
            location = st.selectbox("Location filter", ["All", "Remote", "Hybrid", "On-site"])
        with experience_col:
            experience_level = st.selectbox("Experience filter", ["All", "Internship", "Entry-level", "Fresh graduate"])
        custom_job_description = st.text_area(
            "Optional: paste a job description to compare",
            placeholder="Paste the role requirements here. It will be compared alongside available sample roles.",
            height=110,
        )
        submitted = st.form_submit_button("Analyze resume", type="primary", use_container_width=True)

    if submitted:
        st.session_state.analysis_error = ""
        st.session_state.analysis_result = None
        st.session_state.analysis_report = ""
        if not settings.has_api_key:
            st.session_state.analysis_error = "Add GROQ_API_KEY to your local .env file or Streamlit Cloud Secrets before analyzing."
        else:
            progress = st.progress(0, text="Validating and reading the resume...")
            resume_text = ""
            try:
                resume_text = prepare_resume(uploaded_file)
                progress.progress(25, text="Resume text extracted. Preparing job comparisons...")
                job_matches, dataset_notice = prepare_job_matches(
                    resume_text=resume_text,
                    target_role=target_role,
                    custom_job_description=custom_job_description,
                    job_type=job_type,
                    location=location,
                    experience_level=experience_level,
                )
                progress.progress(50, text="Job comparisons ready. Running the four-agent analysis...")
                with st.spinner("CareerAssist agents are preparing your report..."):
                    crew = CareerAssistCrew()
                    agent_outputs = run_resume_analysis(
                        crew, resume_text, job_matches, preferred_field, target_role
                    )
                progress.progress(100, text="Analysis complete")
                st.session_state.analysis_result = {
                    "agent_outputs": agent_outputs,
                    "job_matches": job_matches,
                    "dataset_notice": dataset_notice,
                    "preferred_field": preferred_field,
                    "target_role": target_role,
                }
                st.session_state.analysis_report = build_report(
                    agent_outputs, job_matches, preferred_field, target_role
                )
            except (ResumeExtractionError, ValueError) as error:
                st.session_state.analysis_error = str(error)
            except Exception as error:
                st.session_state.analysis_error = explain_llm_error(
                    error, settings.groq_api_key, resume_text
                )
            finally:
                progress.empty()

    if st.session_state.analysis_error:
        st.error(st.session_state.analysis_error)

    result = st.session_state.analysis_result
    if result:
        st.markdown("## Career analysis")
        st.caption(f"Preferred field: {result['preferred_field']} · Target role: {result['target_role']}")
        if result.get("dataset_notice"):
            st.warning(result["dataset_notice"])
        matches = result["job_matches"]
        if matches and matches[0].get("matching_notice"):
            st.info(matches[0]["matching_notice"])
        resume_tab, jobs_tab, career_tab, interview_tab = st.tabs(
            ["Resume Analysis", "Job Matching", "Career Guidance", "Interview Preparation"]
        )
        with resume_tab:
            st.markdown(result["agent_outputs"].get("resume_analysis", "No resume analysis was returned."))
        with jobs_tab:
            st.markdown("#### Ranked opportunities")
            st.caption("Sample dataset records are illustrative only. Scores are text-alignment indicators, not hiring probabilities.")
            if not matches:
                st.info("No jobs were available to compare. You can paste a custom job description above.")
            for job in matches:
                title = job.get("job_title", "Untitled role")
                company = job.get("company", "Organization not specified")
                with st.expander(f"{title} · {company}", expanded=len(matches) == 1):
                    if job.get("source_type") == "sample_dataset":
                        st.caption("SAMPLE OPPORTUNITY · not a verified live vacancy")
                    elif job.get("source_type") == "user_provided_description":
                        st.caption("USER-PROVIDED JOB DESCRIPTION")
                    metric_a, metric_b, metric_c = st.columns(3)
                    metric_a.metric("Semantic similarity", format_percentage(job.get("semantic_similarity")))
                    metric_b.metric("Exact skill overlap", format_percentage(job.get("skill_overlap")))
                    metric_c.metric("Recommendation score", format_percentage(job.get("recommendation_score")))
                    st.progress(float(job.get("recommendation_score", 0)))
                    st.write(f"**Type:** {job.get('job_type', 'Not specified')}  ·  **Level:** {job.get('experience_level', 'Not specified')}  ·  **Location:** {job.get('location', 'Not specified')}")
                    st.write("**Matching skills:** " + (", ".join(job.get("matching_skills", [])) or "None identified"))
                    st.write("**Missing required skills:** " + (", ".join(job.get("missing_skills", [])) or "None identified"))
                    st.write(job.get("job_description", ""))
            st.divider()
            st.markdown(result["agent_outputs"].get("job_matching", "No job explanation was returned."))
        with career_tab:
            st.markdown(result["agent_outputs"].get("career_guidance", "No career guidance was returned."))
        with interview_tab:
            st.markdown(result["agent_outputs"].get("interview_preparation", "No interview preparation was returned."))

        st.download_button(
            "Download career report (.md)",
            data=st.session_state.analysis_report,
            file_name="careerassist_report.md",
            mime="text/markdown",
            type="primary",
        )
        st.caption("Your resume text is sent to the configured Groq provider for this analysis. It is not stored by CareerAssist.")
