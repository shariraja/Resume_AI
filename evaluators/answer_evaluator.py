# evaluators/answer_evaluator.py

from groq import Groq
import os
from dotenv import load_dotenv

from evaluators.verifier_agent import classify_answer
from evaluators.score_rubric   import parse_rubric_scores, normalize_to_10, weighted_final_score
from config import JUDGE_MODEL

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Load evaluation prompt template
with open("prompts/evaluation_prompt.txt", "r") as f:
    EVAL_PROMPT_TEMPLATE = f.read()


AGENT_CONFIGS = {
    "technical": {
        "role":        "Technical Judge Agent — Senior Software Engineer",
        "instruction": "Focus ONLY on technical correctness and algorithm/system accuracy. Be strict but fair.",
        "temperature": 0.2,
    },
    "depth": {
        "role":        "Depth Judge Agent — Principal Engineer",
        "instruction": "Focus ONLY on reasoning depth, trade-offs, WHY decisions, and edge case coverage.",
        "temperature": 0.2,
    },
    "bar_raiser": {
        "role":        "FAANG Bar Raiser — Hiring Committee Member",
        "instruction": (
            "You are the hardest judge. Ask: would this answer pass a Google/Meta hiring committee? "
            "Be honest and consistent. Score based purely on technical substance — not style. "
            "Most answers should score 5–7, only exceptional answers get 8+."
        ),
        "temperature": 0.3,   # slightly higher → more consistent, less randomly harsh
    },
}


def _call_judge(agent_key: str, question: str, answer: str) -> dict:
    """Call a single judge agent and return parsed rubric scores."""
    cfg    = AGENT_CONFIGS[agent_key]
    prompt = EVAL_PROMPT_TEMPLATE.format(
        agent_role=cfg["role"],
        agent_instruction=cfg["instruction"],
        question=question,
        answer=answer,
    )
    res = client.chat.completions.create(
        model=JUDGE_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=cfg["temperature"],
    )
    raw_text = res.choices[0].message.content
    scores   = parse_rubric_scores(raw_text)
    return {
        "raw_text":   raw_text,
        "scores":     scores,
        "normalized": normalize_to_10(scores["raw_total"]),
    }


def evaluate_answer(
    question:     str,
    answer:       str,
    is_follow_up: bool = False,
    original_qa:  dict = None,
) -> dict:
    """
    Full 3-layer evaluation pipeline.

    Returns:
    {
        "pass":         bool,
        "verification": dict,
        "agents":       { "technical": {...}, "depth": {...}, "bar_raiser": {...} },
        "weighted":     { "technical_score", "depth_score", "bar_raiser_score", "final_score" },
        "final_score":  float  (/10)
    }
    """
    # ── Step 1: Verify answer quality ──────────────────────────
    verification = classify_answer(question, answer)
    if not verification["pass"]:
        return {
            "pass":        False,
            "verification": verification,
            "agents":      {},
            "weighted":    {
                "technical_score":  0,
                "depth_score":      0,
                "bar_raiser_score": 0,
                "final_score":      0,
            },
            "final_score": 0,
        }

    # ── Step 2: Run 3 judge agents ──────────────────────────────
    agents = {}
    for key in ["technical", "depth", "bar_raiser"]:
        agents[key] = _call_judge(key, question, answer)

    # ── Step 3: Weighted final score ────────────────────────────
    weighted = weighted_final_score(
        agents["technical"]["scores"]["raw_total"],
        agents["depth"]["scores"]["raw_total"],
        agents["bar_raiser"]["scores"]["raw_total"],
    )

    return {
        "pass":         True,
        "verification": verification,
        "agents":       agents,
        "weighted":     weighted,
        "final_score":  weighted["final_score"],
    }