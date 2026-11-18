import re
from typing import Dict, Any

class DifficultyEstimator:
    """
    Module 5: Multi-Factor Difficulty Estimation Engine
    Estimates difficulty category (Easy, Medium, Hard) and numerical score D in [0.0, 1.0]
    by synthesizing Bloom's cognitive depth, linguistic complexity,
    solution step count, and conceptual abstraction.
    """

    BLOOM_WEIGHT_MAP = {
        "L1": 0.16,
        "L2": 0.33,
        "L3": 0.52,
        "L4": 0.70,
        "L5": 0.85,
        "L6": 1.00
    }

    STEP_KEYWORDS = [
        "calculate", "derive", "compute", "step-by-step", "trace", "prove",
        "solve", "show that", "determine", "execute", "simulate", "pseudocode"
    ]

    CONCEPT_KEYWORDS = [
        "trade-off", "distributed", "concurrency", "fault-tolerant", "asymptotic",
        "optimality", "heuristics", "convergence", "adversarial", "constraint satisfaction",
        "bayesian", "markov", "deep neural", "heterogeneous"
    ]

    def estimate_difficulty(self, text: str, bloom_level: str = "L2", marks: int = 5) -> Dict[str, Any]:
        """
        Calculates numerical difficulty score D in [0.0, 1.0] and classifies
        as Easy, Medium, or Hard.
        """
        lower = text.lower()
        words = lower.split()
        word_count = len(words)

        # 1. Bloom's Taxonomy factor (w_b = 0.40)
        f_bloom = self.BLOOM_WEIGHT_MAP.get(bloom_level, 0.40)

        # 2. Expected Solution Steps factor (w_s = 0.25)
        # Inferred from marks and procedural keywords
        step_cues = sum(1 for kw in self.STEP_KEYWORDS if kw in lower)
        marks_normalized = min(marks / 15.0, 1.0)
        f_steps = min(0.4 * marks_normalized + 0.6 * min(step_cues * 0.35, 1.0), 1.0)

        # 3. Conceptual Depth factor (w_c = 0.20)
        concept_cues = sum(1 for kw in self.CONCEPT_KEYWORDS if kw in lower)
        f_concept = min(0.2 + (concept_cues * 0.25), 1.0)

        # 4. Linguistic & Structural Complexity (w_l = 0.15)
        # Based on sentence length, multi-part questions, technical term density
        avg_word_len = sum(len(w) for w in words) / max(word_count, 1)
        length_score = min(word_count / 40.0, 1.0)
        vocab_score = min(avg_word_len / 7.0, 1.0)
        f_ling = (length_score * 0.5) + (vocab_score * 0.5)

        # Composite Difficulty Score
        difficulty_score = (
            0.40 * f_bloom +
            0.25 * f_steps +
            0.20 * f_concept +
            0.15 * f_ling
        )
        difficulty_score = round(min(max(difficulty_score, 0.05), 0.98), 3)

        # Categorization Thresholds
        if difficulty_score < 0.42:
            category = "Easy"
        elif difficulty_score <= 0.72:
            category = "Medium"
        else:
            category = "Hard"

        return {
            "difficulty": category,
            "difficulty_score": difficulty_score,
            "components": {
                "bloom_factor": round(f_bloom, 3),
                "steps_factor": round(f_steps, 3),
                "concept_factor": round(f_concept, 3),
                "linguistic_factor": round(f_ling, 3)
            },
            "explanation": f"Question scored {difficulty_score} ({category}) based on {bloom_level} cognitive demands, {marks}M weightage, and conceptual density."
        }

difficulty_estimator = DifficultyEstimator()
