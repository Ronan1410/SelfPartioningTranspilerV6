from src.analyzer import CodeFeatures

class CostModel:
    """
    Defines the suitability of each language for certain features.
    Scores are heuristic-based (0.0 to 1.0+).
    """
    
    # Weights: [Math, IO, Loops, Recursion, Classes, Async, Strings]
    WEIGHTS = {
        "Rust": {
            "math": 1.0, "io": 0.8, "loops": 1.0, "recursion": 0.8, "classes": 0.1, "async": 0.9, "strings": 0.7, "base_cost": 0.9
        },
        "C++": {
            "math": 1.0, "io": 0.9, "loops": 1.0, "recursion": 1.0, "classes": 0.8, "async": 0.7, "strings": 0.6, "base_cost": 0.85
        },
        "Go": {
            "math": 0.7, "io": 1.0, "loops": 0.9, "recursion": 0.6, "classes": 0.2, "async": 1.0, "strings": 0.9, "base_cost": 0.8
        },
        "Java": {
            "math": 0.8, "io": 0.9, "loops": 0.8, "recursion": 0.7, "classes": 2.0, "async": 0.8, "strings": 1.0, "base_cost": 0.7
        }
    }

    @staticmethod
    def calculate_score(features: CodeFeatures, lang: str) -> float:
        w = CostModel.WEIGHTS[lang]
        
        # Start with base cost (inverse it for score: higher is better suitability)
        # Actually, let's just treat the weights as "Suitability Scores"
        score = w["base_cost"] * 10.0
        
        # Add contributions
        score += features.math_ops * w["math"] * 2.0
        score += features.io_ops * w["io"] * 2.0
        score += features.loops * w["loops"] * 3.0
        score += features.string_ops * w["strings"] * 1.5
        score += features.classes * w["classes"] * 10.0 # Boost class weight significantly
        score += features.async_ops * w["async"] * 5.0
        
        if features.recursion:
            score += w["recursion"] * 15.0
            
        return score

class DecisionEngine:
    def __init__(self, use_neural_fallback=False):
        self.use_neural = use_neural_fallback

    def decide(self, features: CodeFeatures) -> str:
        # Calculate score for each language
        scores = {}
        for lang in CostModel.WEIGHTS.keys():
            scores[lang] = CostModel.calculate_score(features, lang)
            
        # Find max
        best_lang = max(scores, key=scores.get)
        max_score = scores[best_lang]
        
        # Calculate margin to see if inconclusive (e.g., top two are very close)
        sorted_scores = sorted(scores.values(), reverse=True)
        margin = sorted_scores[0] - sorted_scores[1]
        
        if margin < 0.1 and self.use_neural:
            # If inconclusive, return None to signal fallback
            return None
            
        return best_lang, scores
