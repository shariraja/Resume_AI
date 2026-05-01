# evaluators/score_rubric.py

import re
from config import RUBRIC, RUBRIC_TOTAL, AGENT_WEIGHTS


def parse_rubric_scores(feedback_text: str) -> dict:
    def extract(pattern, text, default=0):
        m = re.search(pattern, text)
        return int(m.group(1)) if m else default

    return {
        "correctness":     extract(r"Correctness:\s*(\d+)/4",     feedback_text),
        "depth":           extract(r"Depth:\s*(\d+)/3",           feedback_text),
        "edge_cases":      extract(r"Edge Cases:\s*(\d+)/2",      feedback_text),
        "system_thinking": extract(r"System Thinking:\s*(\d+)/2", feedback_text),
        "communication":   extract(r"Communication:\s*(\d+)/2",   feedback_text),
        "raw_total":       extract(r"Total:\s*(\d+)/13",          feedback_text),
    }


def normalize_to_10(raw_total: int) -> float:
    if raw_total <= 0:
        return 0.0
    return min(round((raw_total / RUBRIC_TOTAL) * 10, 1), 9.5)


def weighted_final_score(tech_raw: int, depth_raw: int, bar_raw: int) -> dict:
    tech_norm  = normalize_to_10(tech_raw)
    depth_norm = normalize_to_10(depth_raw)
    bar_norm   = normalize_to_10(bar_raw)
    final = (
        tech_norm  * AGENT_WEIGHTS["technical"]  +
        depth_norm * AGENT_WEIGHTS["depth"]      +
        bar_norm   * AGENT_WEIGHTS["bar_raiser"]
    )
    return {
        "technical_score":  tech_norm,
        "depth_score":      depth_norm,
        "bar_raiser_score": bar_norm,
        "final_score":      round(min(final, 9.5), 1),
    }


def compute_improvement_slope(scores: list) -> float:
    if len(scores) < 2:
        return 0.0
    deltas    = [scores[i] - scores[i - 1] for i in range(1, len(scores))]
    avg_delta = sum(deltas) / len(deltas)
    return round(max(-1.0, min(1.0, avg_delta / 10)), 3)


def compute_consistency_score(scores: list) -> float:
    """
    Consistency 0-10.
    All zeros = 0 (not rewarded for being consistently bad).
    """
    if not scores:
        return 0.0
    if all(s == 0 for s in scores):
        return 0.0
    if len(scores) < 2:
        return round(scores[0], 1)
    mean      = sum(scores) / len(scores)
    variance  = sum((s - mean) ** 2 for s in scores) / len(scores)
    std_dev   = variance ** 0.5
    return round(max(0.0, 10.0 - (std_dev * 1.5)), 1)


def compute_final_interview_score(
    main_scores:     list,
    followup_scores: list,
    weights:         dict,
) -> dict:
    """
    Final = interview*0.5 + followup*0.2 + consistency*0.15 + slope*0.15

    FIXES:
    - All zeros -> final = 0.0 exactly
    - avg_main == 0 -> short-circuit return 0
    - consistency of zeros -> 0
    - only real non-zero followups counted
    """
    if not main_scores:
        return _zero_result()

    avg_main = round(sum(main_scores) / len(main_scores), 2)

    if avg_main == 0.0:
        return _zero_result()

    real_fu      = [s for s in followup_scores if s > 0]
    avg_followup = round(sum(real_fu) / len(real_fu), 2) if real_fu else avg_main

    consistency = compute_consistency_score(main_scores)
    slope_raw   = compute_improvement_slope(main_scores)
    slope_score = round(5.0 + (slope_raw * 5.0), 1)

    final = (
        avg_main     * weights["interview"]          +
        avg_followup * weights["followup_depth"]     +
        consistency  * weights["consistency"]        +
        slope_score  * weights["improvement_slope"]
    )

    return {
        "final": round(min(final, 9.5), 1),
        "breakdown": {
            "avg_main":     avg_main,
            "avg_followup": avg_followup,
            "consistency":  consistency,
            "slope_score":  slope_score,
        },
    }


def _zero_result() -> dict:
    return {
        "final": 0.0,
        "breakdown": {
            "avg_main":     0.0,
            "avg_followup": 0.0,
            "consistency":  0.0,
            "slope_score":  0.0,
        },
    }