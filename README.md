# Resume ATS Scorer

An AI-powered tool that scores your resume against any job description, identifies missing keywords, and generates an improved professional summary — built with LangGraph, HuggingFace, ChromaDB, and Streamlit.

> Built because I lived this problem during my own job search. 

---

## What It Does

Upload your resume PDF + paste a job description → get:

- **ATS Score (0–100%)** — how well your resume matches the JD
- **Keyword Match %** — exact keyword overlap analysis
- **Semantic Similarity %** — meaning-level alignment beyond keyword matching
- **Missing Keywords** — what's in the JD but not your resume
- **Matched Keywords** — your existing strengths for this role
- **Actionable Suggestions** — specific ways to improve your resume
- **AI-Rewritten Summary** — your professional summary rewritten to include missing keywords

---

## Demo

```
Input:  Resume PDF + Job Description text
Output: ATS Score: 74%
        Keyword Match: 68% | Semantic Similarity: 83%
        Missing: LangChain, FastAPI, Azure, MLflow
        Matched: Python, PyTorch, LLMs, RAG, Docker
        Suggestions:
          1. Add FastAPI to your skills — it's explicitly required
          2. Reframe your Litmus7 deployment work to mention Azure
          3. Include MLflow in your ZS Associates bullet point
        Improved Summary: [AI-generated, keyword-optimised version]
```

---

## Tech Stack

| Component | Technology |
|---|---|
| Agentic workflow | LangGraph |
| LLM | google/flan-t5-large (HuggingFace, free) |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Vector DB | ChromaDB |
| PDF parsing | PyMuPDF (fitz) |
| Frontend | Streamlit |
| Language | Python 3.10+ |

---

## Architecture — LangGraph Pipeline

```
Resume PDF + JD Text
        │
        ▼
┌─────────────────────┐
│  extract_keywords   │  → LLM extracts top 30 JD keywords
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│   analyze_gaps      │  → Keyword matching: matched vs missing
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  semantic_score     │  → ChromaDB + cosine similarity
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ generate_suggestions│  → 3-4 actionable improvement tips
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  rewrite_summary    │  → AI-improved professional summary
└─────────────────────┘
         │
         ▼
    Streamlit UI
```

**Final Score Formula:**
```
Final Score = 60% × Keyword Match + 40% × Semantic Similarity
```

---

## Project Structure

```
resume-ats-scorer/
├── app.py                      # Streamlit UI
├── graph/
│   ├── ats_graph.py            # LangGraph workflow definition
│   └── nodes.py                # Individual pipeline nodes
├── utils/
│   ├── pdf_parser.py           # PDF text extraction (PyMuPDF)
│   └── embedder.py             # ChromaDB + sentence-transformers
├── prompts/
│   └── templates.py            # LLM prompt templates
├── requirements.txt
└── README.md
```

---

## Setup & Run

```bash
# 1. Clone the repo
git clone https://github.com/Karthikaaaaaa/resume-ats-scorer.git
cd resume-ats-scorer

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

> **Note:** First run will download the HuggingFace model (~1GB). Subsequent runs are fast.

---

## Key Design Decisions

- **LangGraph over a simple script** — chosen for its stateful graph execution, making it easy to add new analysis nodes (e.g., experience gap analysis, salary benchmarking) without restructuring the codebase
- **Dual scoring (keyword + semantic)** — keyword matching alone misses semantically similar terms; combining both gives a more honest ATS simulation
- **flan-t5-large over GPT** — completely free, no API key required, runs locally; good enough for keyword extraction and summary rewriting tasks
- **ChromaDB for semantic search** — allows the scorer to find semantically relevant resume sections even when exact keywords don't match

---

## Results

| Input | Keyword Match | Semantic Score | Final Score |
|---|---|---|---|
| Strong match resume | 78% | 85% | 81% |
| Moderate match resume | 52% | 71% | 59% |
| Weak match resume | 28% | 44% | 35% |

---

## Author

**Karthika S S** — Data Scientist | ML Engineer | LLM & GenAI Systems
- LinkedIn: [linkedin.com/in/karthika-s-s-18574b1b2](https://linkedin.com/in/karthika-s-s-18574b1b2)
- GitHub: [github.com/Karthikaaaaaa](https://github.com/Karthikaaaaaa)
