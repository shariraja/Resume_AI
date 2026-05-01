from collections import defaultdict

class KnowledgeGraph:
    def __init__(self):
        self.mastery = defaultdict(lambda: 0.5)
        self.attempts = defaultdict(int)
        self.mistakes = []
        self.strengths = []

    def update(self, topic: str, score_10: float, gaps: list = None):
        self.attempts[topic] += 1
        prev = self.mastery[topic]
        alpha = 0.4
        self.mastery[topic] = round(alpha * (score_10 / 10) + (1 - alpha) * prev, 3)
        if score_10 >= 7:
            if topic not in self.strengths:
                self.strengths.append(topic)
        if gaps:
            for g in gaps:
                self.mistakes.append((topic, g))

    def weakest_topics(self, n: int = 3) -> list:
        return [t for t, _ in sorted(self.mastery.items(), key=lambda x: x[1])[:n]]

    def weakness_vector(self) -> dict:
        return dict(self.mastery)

    def summary(self) -> str:
        lines = ["Topic Mastery:"]
        for topic, score in sorted(self.mastery.items(), key=lambda x: x[1]):
            bar = "█" * int(score * 10) + "░" * (10 - int(score * 10))
            lines.append(f"  {topic:<25} {bar} {score:.0%}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {"mastery": dict(self.mastery), "attempts": dict(self.attempts),
                "mistakes": self.mistakes, "strengths": self.strengths}
