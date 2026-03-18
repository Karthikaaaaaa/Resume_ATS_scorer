from typing import TypedDict, List
from transformers import pipeline
from prompts.templates import (
    KEYWORD_EXTRACTION_PROMPT,
    GAP_ANALYSIS_PROMPT,
    SUMMARY_REWRITE_PROMPT
)
from utils.embedder import cosine_similarity_score, chunk_and_store, retrieve_relevant
import re

# Load HuggingFace text generation pipeline (free, no API key)
generator = pipeline(
    "text2text-generation",
    model="google/flan-t5-large",
    max_new_tokens=512
)

def call_llm(prompt: str) -> str:
    """Call the HuggingFace LLM."""
    try:
        result = generator(prompt[:2048], max_new_tokens=512)
        return result[0]["generated_text"].strip()
    except Exception as e:
        return f"LLM Error: {str(e)}"


# ── State Definition ──────────────────────────────────────────────

class ATSState(TypedDict):
    resume_text: str
    jd_text: str
    jd_keywords: List[str]
    matched_keywords: List[str]
    missing_keywords: List[str]
    ats_score: int
    semantic_score: float
    final_score: int
    suggestions: List[str]
    improved_summary: str
    error: str


# ── Node 1: Extract JD Keywords ───────────────────────────────────

def extract_jd_keywords(state: ATSState) -> ATSState:
    """Extract key skills and requirements from the JD."""
    try:
        prompt = KEYWORD_EXTRACTION_PROMPT.format(jd_text=state["jd_text"][:1500])
        response = call_llm(prompt)
        keywords = [kw.strip() for kw in response.split(",") if kw.strip()]
        state["jd_keywords"] = keywords[:30]  # cap at 30
    except Exception as e:
        state["error"] = f"Keyword extraction failed: {str(e)}"
        state["jd_keywords"] = []
    return state


# ── Node 2: Gap Analysis ──────────────────────────────────────────

def analyze_gaps(state: ATSState) -> ATSState:
    """Compare resume against JD keywords and identify gaps."""
    try:
        resume_lower = state["resume_text"].lower()
        matched = []
        missing = []

        for keyword in state["jd_keywords"]:
            if keyword.lower() in resume_lower:
                matched.append(keyword)
            else:
                missing.append(keyword)

        state["matched_keywords"] = matched
        state["missing_keywords"] = missing

        # Keyword-based score
        total = len(state["jd_keywords"])
        keyword_score = int((len(matched) / total * 100)) if total > 0 else 0
        state["ats_score"] = keyword_score

    except Exception as e:
        state["error"] = f"Gap analysis failed: {str(e)}"
    return state


# ── Node 3: Semantic Similarity Score ────────────────────────────

def compute_semantic_score(state: ATSState) -> ATSState:
    """Compute semantic similarity between resume and JD."""
    try:
        score = cosine_similarity_score(
            state["resume_text"][:1000],
            state["jd_text"][:1000]
        )
        state["semantic_score"] = round(score * 100, 1)

        # Final score = 60% keyword match + 40% semantic similarity
        state["final_score"] = int(
            0.6 * state["ats_score"] + 0.4 * state["semantic_score"]
        )
    except Exception as e:
        state["error"] = f"Semantic scoring failed: {str(e)}"
        state["semantic_score"] = 0.0
        state["final_score"] = state.get("ats_score", 0)
    return state


# ── Node 4: Generate Suggestions ─────────────────────────────────

def generate_suggestions(state: ATSState) -> ATSState:
    """Generate actionable improvement suggestions."""
    try:
        missing_str = ", ".join(state["missing_keywords"][:10])
        prompt = GAP_ANALYSIS_PROMPT.format(
            resume_text=state["resume_text"][:1000],
            jd_keywords=", ".join(state["jd_keywords"][:20])
        )
        response = call_llm(prompt)

        # Parse suggestions from response
        suggestions = []
        lines = response.split("\n")
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith("-")):
                clean = re.sub(r"^[\d\.\-\*]\s*", "", line).strip()
                if clean and len(clean) > 10:
                    suggestions.append(clean)

        if not suggestions:
            # Fallback suggestions based on missing keywords
            missing = state["missing_keywords"][:5]
            suggestions = [
                f"Add '{missing[0]}' to your skills section — it's a key requirement" if len(missing) > 0 else "Align your summary more closely with the JD language",
                f"Incorporate '{missing[1]}' by reframing an existing project" if len(missing) > 1 else "Quantify your achievements with specific metrics",
                f"Mention '{missing[2]}' experience in your work bullets" if len(missing) > 2 else "Use exact terminology from the JD in your bullets",
            ]

        state["suggestions"] = suggestions[:4]

    except Exception as e:
        state["error"] = f"Suggestion generation failed: {str(e)}"
        state["suggestions"] = ["Review missing keywords and incorporate them naturally into your resume."]
    return state


# ── Node 5: Rewrite Summary ───────────────────────────────────────

def rewrite_summary(state: ATSState) -> ATSState:
    """Generate an improved professional summary."""
    try:
        # Extract current summary (first 3 sentences of resume)
        sentences = state["resume_text"].split(".")[:3]
        current_summary = ". ".join(sentences) + "."

        missing_str = ", ".join(state["missing_keywords"][:8])
        prompt = SUMMARY_REWRITE_PROMPT.format(
            current_summary=current_summary[:500],
            jd_text=state["jd_text"][:800],
            missing_keywords=missing_str
        )
        improved = call_llm(prompt)
        state["improved_summary"] = improved.strip()

    except Exception as e:
        state["error"] = f"Summary rewrite failed: {str(e)}"
        state["improved_summary"] = "Could not generate improved summary."
    return state
