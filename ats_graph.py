from langgraph.graph import StateGraph, END
from graph.nodes import (
    ATSState,
    extract_jd_keywords,
    analyze_gaps,
    compute_semantic_score,
    generate_suggestions,
    rewrite_summary
)

def build_ats_graph():
    """Build and compile the ATS scoring LangGraph workflow."""

    workflow = StateGraph(ATSState)

    # Add nodes
    workflow.add_node("extract_keywords", extract_jd_keywords)
    workflow.add_node("analyze_gaps", analyze_gaps)
    workflow.add_node("semantic_score", compute_semantic_score)
    workflow.add_node("generate_suggestions", generate_suggestions)
    workflow.add_node("rewrite_summary", rewrite_summary)

    # Define edges — linear pipeline
    workflow.set_entry_point("extract_keywords")
    workflow.add_edge("extract_keywords", "analyze_gaps")
    workflow.add_edge("analyze_gaps", "semantic_score")
    workflow.add_edge("semantic_score", "generate_suggestions")
    workflow.add_edge("generate_suggestions", "rewrite_summary")
    workflow.add_edge("rewrite_summary", END)

    return workflow.compile()


def run_ats_scorer(resume_text: str, jd_text: str) -> ATSState:
    """Run the full ATS scoring pipeline."""
    graph = build_ats_graph()

    initial_state: ATSState = {
        "resume_text": resume_text,
        "jd_text": jd_text,
        "jd_keywords": [],
        "matched_keywords": [],
        "missing_keywords": [],
        "ats_score": 0,
        "semantic_score": 0.0,
        "final_score": 0,
        "suggestions": [],
        "improved_summary": "",
        "error": ""
    }

    result = graph.invoke(initial_state)
    return result
