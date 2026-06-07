"""Vector math utilities for atmosphere matching."""
import math


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def vibe_dict_to_vector(vibe: dict) -> list[float]:
    keys = ["noise_level", "light", "crowd_density", "social_vibe",
            "energy", "aesthetic", "outdoor_ratio"]
    return [vibe.get(k, 0.5) for k in keys]
