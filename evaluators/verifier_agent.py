# evaluators/verifier_agent.py

import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


ANSWER_TYPES = {
    "valid":     "valid technical answer",
    "partial":   "partial answer",
    "irrelevant": "irrelevant",
    "repeated":  "repeated question"
}


def classify_answer(question: str, answer: str) -> dict:
    """
    Returns:
        {
            "type": one of ANSWER_TYPES keys,
            "label": human-readable label,
            "pass": bool,
            "reason": str
        }
    """
    if not answer or len(answer.strip()) < 15:
        return _fail("partial", "Answer is too short to evaluate.")

    if _is_repetition(question, answer):
        return _fail("repeated", "Answer appears to repeat the question — no original content.")

    if not _is_relevant(question, answer):
        return _fail("irrelevant", "Answer does not address the question asked.")

    if _is_gibberish(answer):
        return _fail("partial", "Answer contains no meaningful technical content.")

    return {
        "type":   "valid",
        "label":  ANSWER_TYPES["valid"],
        "pass":   True,
        "reason": "Answer passed all validation checks."
    }


# ─── INTERNAL HELPERS ───────────────────────────────────────────

def _fail(answer_type: str, reason: str) -> dict:
    return {
        "type":   answer_type,
        "label":  ANSWER_TYPES[answer_type],
        "pass":   False,
        "reason": reason
    }


def _is_repetition(question: str, answer: str) -> bool:
    """Detects if answer is just the question echoed back."""
    q_clean = question.lower().strip()
    a_clean = answer.lower().strip()

    # Direct substring check
    if q_clean[:60] in a_clean:
        return True

    # High cosine similarity → likely copy-paste
    try:
        docs  = [q_clean, a_clean]
        tfidf = TfidfVectorizer().fit_transform(docs)
        sim   = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        if sim > 0.82:
            return True
    except Exception:
        pass

    return False


def _is_relevant(question: str, answer: str) -> bool:
    """Checks if answer is topically related to question."""
    try:
        docs  = [question, answer]
        tfidf = TfidfVectorizer().fit_transform(docs)
        sim   = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        return sim > 0.12
    except Exception:
        return True  # give benefit of doubt on vectorizer failure


def _is_gibberish(answer: str) -> bool:
    """Detects answers with no real words."""
    return bool(re.fullmatch(r"[.\s0-9!@#$%^&*()_+\-=\[\]{}|;':\",./<>?`~\\]+", answer))