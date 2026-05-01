import streamlit as st
from interview.knowledge_graph import KnowledgeGraph
from interview.adaptive_engine import AdaptiveEngine

def init_state():
    defaults = {
        "questions": [], "index": 0, "scores": [], "answers": [],
        "eval_results": [], "interview_started": False,
        "interview_phase": "main", "follow_up_question": "",
        "follow_up_questions_list": [], "follow_up_answers": [],
        "follow_up_scores": [], "follow_up_evals": [],
        "last_eval": None, "knowledge_graph": None,
        "adaptive_engine": None, "hiring_mode": "google",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val
    if st.session_state.knowledge_graph is None:
        st.session_state.knowledge_graph = KnowledgeGraph()
    if st.session_state.adaptive_engine is None:
        st.session_state.adaptive_engine = AdaptiveEngine(mode=st.session_state.hiring_mode)

def reset_state():
    st.session_state.clear()
    init_state()
