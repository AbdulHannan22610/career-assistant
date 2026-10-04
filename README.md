# CareerAssist

CareerAssist is a student-focused, AI-powered resume analyzer and career guidance demonstration. Upload a text-based PDF to receive a grounded resume review, explainable comparisons with sample early-career roles, a personalized learning roadmap, and interview practice.

> The included job records are illustrative samples, not verified live vacancies. Semantic similarity is a measure of text alignment, not a probability of being hired.

## Objectives and problem statement

Students and new graduates often have difficulty translating their coursework and projects into a clear career plan. CareerAssist combines resume extraction, transparent job-profile matching, and focused language-model assistance in one workflow. It is an educational project and does not replace professional recruiting, legal advice, or a candidate's own judgment.

## Features

- Extract selectable text from uploaded PDFs with page-by-page PyPDF processing. Scanned-image PDFs need OCR, which is not included.
- Review education, technical and soft skills, projects, experience, certifications, strengths, gaps, and improvement ideas.
- Compare the resume with bundled sample jobs using a cached Sentence Transformers embedding model and scikit-learn cosine similarity.
- Show semantic similarity, exact required-skill overlap, and a combined recommendation score separately.
- Optionally compare a user-pasted job description; no job-board scraping or paid job API is used.
- Generate career pathways, a staged learning roadmap, project ideas, and tailored interview question practice.
- Download the result as Markdown.
- Keep Groq credentials in local environment configuration or Streamlit Secrets, never in source code.

## Four-agent architecture

The workflow is sequential:

1. **Resume Analyzer** extracts and explains evidence from the resume; absent details are reported as not found.
2. **Job Matching** explains match records and scores calculated by Python utilities. It cannot change the supplied scores.
3. **Career Guidance** uses resume and job context to recommend a small number of suitable paths and learning steps.
4. **Interview Preparation** creates technical, project/resume-based, and HR questions for the selected target role.

These are four custom-configured CrewAI agents sharing one configured Groq LLM. They are not four independently trained models. A CrewAI **Agent** has a role, goal, and behavior; a **Task** describes work and its expected output; a **Crew** coordinates agents and tasks; and a **Process** defines execution order. CareerAssist uses a sequential process and explicit task context. Sentence Transformers is a separate embedding model used only for semantic matching; it is not the Groq LLM.

## Technology stack

- Python 3.11 or a compatible version supported by the selected package releases
- Streamlit for the user interface
- CrewAI and its LiteLLM-backed Groq interface
- Groq API for shared language-model inference
- Sentence Transformers (`all-MiniLM-L6-v2`) and scikit-learn for similarity
- PyPDF for text-based PDF extraction
- Pandas and NumPy for data and embeddings
- python-dotenv for local settings

## Project structure

```text
CareerAssist/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
├── .streamlit/
│   └── config.toml
├── config/
│   ├── __init__.py
│   ├── settings.py
│   └── llm_config.py
├── agents/
│   ├── __init__.py
│   ├── resume_analyzer_agent.py
│   ├── job_matching_agent.py
│   ├── career_guidance_agent.py
│   └── interview_preparation_agent.py
├── tasks/
│   ├── __init__.py
│   ├── resume_analysis_task.py
│   ├── job_matching_task.py
│   ├── career_guidance_task.py
│   └── interview_preparation_task.py
├── crew/
│   ├── __init__.py
│   └── careerassist_crew.py
├── tools/
│   ├── __init__.py
│   ├── pdf_extractor.py
│   ├── text_processor.py
│   ├── semantic_matcher.py
│   └── job_dataset_tool.py
├── services/
│   ├── __init__.py
│   ├── resume_service.py
│   ├── job_service.py
│   └── report_service.py
├── data/
│   ├── jobs_dataset.csv
│   └── README.md
├── utils/
│   ├── __init__.py
│   ├── validators.py
│   ├── formatting.py
│   └── session_manager.py
└── assets/
    └── README.md
```

Each package's `__init__.py` identifies its responsibility. Service code keeps the UI thin; reusable parsing, text, dataset, and matching code lives in `tools/`.

## How it works

1. The user uploads a PDF and selects a field, target role, and optional dataset filters or custom description.
2. PyPDF extracts each page's selectable text; text normalization preserves useful resume structure.
3. The embedding model loads only when matching begins. Candidate and role text are embedded and compared with cosine similarity. Exact known-skill overlap is computed separately.
4. If the embedding model cannot load, CareerAssist ranks by exact skill overlap and shows semantic similarity as unavailable.
5. One shared Groq LLM serves four CrewAI agents in sequence. The resume and supplied context are sent only after the user submits the form.
6. The UI presents four report sections and a downloadable Markdown report.

The combined recommendation score uses 70% semantic similarity and 30% required-skill overlap when embeddings are available. Without embeddings, the ordering uses exact skill overlap only. These are text-comparison aids, not validated hiring predictions.

## Installation and local configuration

Use Python 3.11 or a compatible supported release. From the directory containing this project, open PowerShell on Windows or a terminal on macOS/Linux.

### Windows PowerShell

```powershell
cd CareerAssist
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

If PowerShell blocks activation, use Command Prompt instead:

```bat
cd CareerAssist
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
```

### macOS / Linux

```bash
cd CareerAssist
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

If your terminal is already at the project root, omit `cd CareerAssist`. After copying `.env.example`, edit `.env` and replace the placeholder `GROQ_API_KEY` with your own key. Never commit `.env`. `GROQ_MODEL` defaults to `openai/gpt-oss-120b`; confirm the model is available to your Groq account. `EMBEDDING_MODEL` defaults to `sentence-transformers/all-MiniLM-L6-v2`.

The first time matching is requested, Sentence Transformers may download the embedding model. This happens at runtime on user request, not during application startup. Groq free-tier usage limits apply.

### Start the application manually

With the virtual environment activated, from the project root run:

```bash
streamlit run app.py
```

CareerAssist does not analyze a resume on startup. Upload a PDF and submit the form to begin. This project was created without running the application, installing packages, downloading models, or calling Groq; the commands above are for you to run manually.

## Groq API key and Streamlit Cloud

For local use, the app loads `.env` through python-dotenv. Streamlit Secrets take precedence when available; environment variables are the local fallback. The app displays only whether a key is configured, never its contents.

For Streamlit Community Cloud:

1. Push the project to a GitHub repository that you control.
2. Sign in to Streamlit Community Cloud and choose **Create app**.
3. Connect the GitHub repository, select the branch, and set the main file to `app.py`.
4. Open the app's **Settings / Secrets** panel and add:

```toml
GROQ_API_KEY = "your_real_key"
GROQ_MODEL = "openai/gpt-oss-120b"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
```

5. Save the secrets and deploy. Do not put real keys in GitHub, README files, screenshots, or source files. The app's `.gitignore` excludes `.streamlit/secrets.toml` for local testing.

## GitHub setup

Create an empty repository on GitHub, then run these commands from the project root (replace the URL with your repository URL):

```bash
git init
git add .
git commit -m "Create CareerAssist project"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/CareerAssist.git
git push -u origin main
```

Check that `.env` and `.streamlit/secrets.toml` are not included before pushing. If GitHub asks you to authenticate, use its supported sign-in flow; do not put credentials in the remote URL.

## Dataset

`data/jobs_dataset.csv` contains 20 educational sample records with the schema described in `data/README.md`. The records are explicitly labeled `sample_dataset`, and no company or vacancy is represented as verified. Add only accurate sources and links if you replace the sample data. A user-provided job description can be compared without changing the CSV.

## Limitations

- The PDF reader extracts text layers only; scanned/image-only documents require OCR.
- Resume parsing and LLM-generated recommendations can be incomplete or wrong; review results before using them.
- Sample records are not live jobs, and matching scores are not hiring probabilities.
- Sentence Transformers may need internet access for the first model download; model-load failure disables semantic scoring but retains exact-skill matching.
- Groq rate limits and model availability depend on the user's account and current provider offerings.
- The app does not persist resumes to disk, but the resume text is sent to Groq for analysis after submission. Review the provider's data policy before uploading sensitive information.

## Security and privacy

Never commit API credentials. Use `.env` locally and Streamlit Secrets in deployment. CareerAssist does not display or log the key and does not write uploaded resume contents to disk. Resume text is included in the user-requested Groq analysis request; avoid uploading highly sensitive data. This student project is not a regulated document storage system.

## Future improvements

- Add optional OCR with clear user consent and privacy controls.
- Add a user-managed verified job dataset and source freshness metadata.
- Add configurable career-interest questions and editable report sections.
- Add focused unit tests for document validation, data schema, scoring, and report rendering.
- Add privacy-preserving deletion and retention controls if persistent accounts are introduced.
