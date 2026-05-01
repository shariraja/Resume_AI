# utils/helpers.py

import re
import streamlit as st


def display_score_breakdown(eval_result: dict):
    if not eval_result:
        st.warning("No evaluation data available.")
        return

    # ── Verification failed ─────────────────────────────────────
    if not eval_result.get("pass", True):
        reason = eval_result.get("verification", {}).get("reason", "Invalid answer.")
        st.error(f"❌ **Answer rejected:** {reason}")
        st.metric("Score", "0/10")
        return

    weighted    = eval_result.get("weighted", {})
    final_score = eval_result.get("final_score", 0)
    agents      = eval_result.get("agents", {})

    # ── Score banner ────────────────────────────────────────────
    if final_score >= 8:
        st.success(f"🎯 Final Score: **{final_score}/10** — Excellent!")
    elif final_score >= 6:
        st.info(f"🎯 Final Score: **{final_score}/10** — Good")
    elif final_score >= 4:
        st.warning(f"🎯 Final Score: **{final_score}/10** — Needs Work")
    else:
        st.error(f"🎯 Final Score: **{final_score}/10** — Poor")

    # ── 3-Agent score columns ───────────────────────────────────
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("⚙️ Technical (40%)",  f"{weighted.get('technical_score',  0)}/10")
    with c2:
        st.metric("🧠 Depth (40%)",      f"{weighted.get('depth_score',      0)}/10")
    with c3:
        st.metric("🏁 Bar Raiser (20%)", f"{weighted.get('bar_raiser_score', 0)}/10")

    # ── Per-agent rubric details — NO nested expanders ──────────
    st.divider()
    st.markdown("##### 📋 Agent Breakdown")

    for agent_key, label in [
        ("technical",  "⚙️ Technical Judge"),
        ("depth",      "🧠 Depth Judge"),
        ("bar_raiser", "🏁 Bar Raiser")
    ]:
        agent_data = agents.get(agent_key, {})
        if not agent_data:
            continue

        scores   = agent_data.get("scores", {})
        raw_text = agent_data.get("raw_text", "")

        st.markdown(f"**{label}**")

        r1, r2, r3, r4, r5 = st.columns(5)
        r1.metric("Correctness",     f"{scores.get('correctness',     0)}/4")
        r2.metric("Depth",           f"{scores.get('depth',           0)}/3")
        r3.metric("Edge Cases",      f"{scores.get('edge_cases',      0)}/2")
        r4.metric("System Thinking", f"{scores.get('system_thinking', 0)}/2")
        r5.metric("Communication",   f"{scores.get('communication',   0)}/2")

        # Feedback
        fb = re.search(r"Feedback:\s*(.+?)(?=Gaps:|$)", raw_text, re.DOTALL)
        if fb:
            st.info(f"💬 {fb.group(1).strip()}")

        # Gaps
        gaps = re.search(r"Gaps:\s*(.+?)$", raw_text, re.DOTALL)
        if gaps:
            gap_text = gaps.group(1).strip()
            numbered = re.findall(r"\(\d+\)\s*(.+?)(?=\(\d+\)|$)", gap_text, re.DOTALL)
            if numbered:
                st.warning("📈 **To score higher:**")
                for g in numbered:
                    st.warning(f"  → {g.strip()}")
            else:
                st.warning(f"📈 **Gaps:** {gap_text}")

        st.divider()