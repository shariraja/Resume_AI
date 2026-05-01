# interview/adaptive_engine.py

from config import DIFFICULTY_LEVELS, HIRING_MODES


class AdaptiveEngine:

    def __init__(self, mode: str = "google"):
        self.mode       = mode
        self.difficulty = 2
        self.history    = []   # list of scores
        self._fu_index  = 0    # follow-up rotation counter

    # ── DIFFICULTY ─────────────────────────────────────────────
    def update_difficulty(self, score_10: float):
        self.history.append(score_10)
        if score_10 >= 7:
            self.difficulty = min(5, self.difficulty + 1)
        elif score_10 <= 3:
            self.difficulty = max(1, self.difficulty - 1)
        # 4–6 → hold current level

    def get_difficulty_label(self) -> str:
        return DIFFICULTY_LEVELS.get(self.difficulty, "FAANG Level")

    # ── FOLLOW-UP TYPE (rotating + score-aware) ────────────────
    def select_followup_type(self, score_10: float, weakness_vector: dict) -> str:
        """
        Rotate follow-up types so every question gets a different probe style.
        Types: deep_dive | edge_case | scaling | failure
        """
        all_types  = ["deep_dive", "edge_case", "scaling", "failure"]
        mode_cfg   = HIRING_MODES.get(self.mode, HIRING_MODES["google"])
        aggression = mode_cfg["follow_up_aggression"]

        if aggression == "high":
            if score_10 >= 7:
                # Strong answer → push harder (scaling or failure)
                hard_types = ["scaling", "failure"]
                fu_type    = hard_types[self._fu_index % len(hard_types)]
            elif score_10 >= 5:
                # Medium answer → rotate through all types
                fu_type = all_types[self._fu_index % len(all_types)]
            else:
                # Weak answer → go deeper on basics
                fu_type = "deep_dive"
        else:
            # medium aggression → rotate between deep_dive and edge_case
            soft_types = ["deep_dive", "edge_case"]
            fu_type    = soft_types[self._fu_index % len(soft_types)]

        self._fu_index += 1   # advance rotation counter
        return fu_type

    # ── MODE CONFIG ────────────────────────────────────────────
    def get_mode_config(self) -> dict:
        return HIRING_MODES.get(self.mode, HIRING_MODES["google"])

    def get_strictness(self) -> float:
        return self.get_mode_config()["strictness"]