"""Atmosphere vectorization + cosine matching for vibe-match."""
from __future__ import annotations
import json
import math
from datetime import datetime
from pathlib import Path

VENUE_DATA_PATH = Path(__file__).resolve().parent.parent / "mock_data" / "venues.json"

VIBE_DIMS = ["noise_level", "light", "crowd_density", "social_vibe",
             "energy", "aesthetic", "outdoor_ratio"]

KEYWORD_MAP = {
    "安静": {"noise_level": 0.1, "energy": 0.2},
    "静": {"noise_level": 0.1, "energy": 0.2},
    "吵": {"noise_level": 0.8, "energy": 0.7},
    "热闹": {"noise_level": 0.7, "crowd_density": 0.7, "social_vibe": 0.8, "energy": 0.7},
    "嗨": {"noise_level": 0.9, "energy": 0.9, "crowd_density": 0.8},
    "放松": {"energy": 0.2, "noise_level": 0.3},
    "慢": {"energy": 0.2},
    "快": {"energy": 0.8},
    "一个人": {"social_vibe": 0.1, "crowd_density": 0.2},
    "独处": {"social_vibe": 0.1, "crowd_density": 0.1},
    "约会": {"social_vibe": 0.4, "crowd_density": 0.3, "aesthetic": 0.7, "light": 0.3},
    "朋友": {"social_vibe": 0.6, "crowd_density": 0.5},
    "聚会": {"social_vibe": 0.8, "crowd_density": 0.7, "energy": 0.7},
    "团建": {"social_vibe": 0.9, "crowd_density": 0.8, "energy": 0.8},
    "昏暗": {"light": 0.1},
    "烛光": {"light": 0.1, "aesthetic": 0.7},
    "明亮": {"light": 0.9},
    "阳光": {"light": 0.9, "outdoor_ratio": 0.6},
    "户外": {"outdoor_ratio": 0.9},
    "露台": {"outdoor_ratio": 0.7},
    "室内": {"outdoor_ratio": 0.1},
    "包间": {"crowd_density": 0.1, "noise_level": 0.2},
    "网红": {"aesthetic": 0.9},
    "ins": {"aesthetic": 0.9},
    "打卡": {"aesthetic": 0.8},
    "复古": {"aesthetic": 0.4},
    "工业风": {"aesthetic": 0.2},
    "精致": {"aesthetic": 0.8},
    "爵士": {"noise_level": 0.3, "energy": 0.3, "aesthetic": 0.6},
    "摇滚": {"noise_level": 0.8, "energy": 0.9},
    "电子": {"noise_level": 0.7, "energy": 0.8},
    "音乐": {"noise_level": 0.4, "energy": 0.4},
    "潮": {"social_vibe": 0.4},
    "喝酒": {"social_vibe": 0.5, "energy": 0.4},
    "咖啡": {"noise_level": 0.3, "energy": 0.3},
    "茶": {"noise_level": 0.2, "energy": 0.2},
    "看书": {"noise_level": 0.1, "social_vibe": 0.1, "energy": 0.1},
    "工作": {"noise_level": 0.2, "social_vibe": 0.2, "light": 0.7},
    "待到很晚": {"energy": 0.3},
    "深夜": {"energy": 0.3, "light": 0.2},
    "早上": {"light": 0.8, "energy": 0.4},
    "下午": {"energy": 0.4},
    "晚上": {"light": 0.3},
}


def load_venues(path: str | None = None) -> list[dict]:
    p = Path(path) if path else VENUE_DATA_PATH
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def text_to_vibe_vector(text: str) -> list[float]:
    accum = {dim: [] for dim in VIBE_DIMS}
    for keyword, values in KEYWORD_MAP.items():
        if keyword in text:
            for dim, val in values.items():
                accum[dim].append(val)
    vector = []
    for dim in VIBE_DIMS:
        if accum[dim]:
            vector.append(sum(accum[dim]) / len(accum[dim]))
        else:
            vector.append(0.5)
    return vector


def venue_to_vector(venue: dict) -> list[float]:
    vibe = venue.get("vibe", {})
    return [vibe.get(dim, 0.5) for dim in VIBE_DIMS]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def compute_time_fit(venue: dict, hour: int | None = None) -> float:
    if hour is None:
        hour = datetime.now().hour
    hours = venue.get("hours", {})
    open_h = int(hours.get("open", "00:00").split(":")[0])
    close_h = int(hours.get("close", "23:59").split(":")[0])
    if close_h == 0:
        close_h = 24
    if close_h < open_h:
        if hour >= open_h or hour < close_h:
            return 1.0
        return 0.0
    if open_h <= hour < close_h:
        remaining = close_h - hour
        if remaining >= 3:
            return 1.0
        return 0.5 + 0.5 * (remaining / 3)
    return 0.0


def match_venues(text: str, lat: float | None = None, lng: float | None = None,
                 radius_m: float = 5000, hour: int | None = None,
                 venues: list[dict] | None = None) -> list[dict]:
    if venues is None:
        venues = load_venues()

    query_vec = text_to_vibe_vector(text)

    results = []
    for v in venues:
        if lat is not None and lng is not None:
            from common_geo import haversine
            dist = haversine(lat, lng, v["lat"], v["lng"])
            if dist > radius_m:
                continue
            v_copy = dict(v)
            v_copy["distance_m"] = round(dist)
        else:
            v_copy = dict(v)
            v_copy["distance_m"] = 0

        venue_vec = venue_to_vector(v)
        sim = cosine_similarity(query_vec, venue_vec)

        time_fit = compute_time_fit(v, hour)
        final_score = sim * 0.8 + time_fit * 0.2

        v_copy["match_score"] = round(final_score, 3)
        v_copy["vibe_similarity"] = round(sim, 3)
        v_copy["time_fit"] = round(time_fit, 3)
        v_copy["query_vector"] = [round(x, 2) for x in query_vec]
        v_copy["venue_vector"] = [round(x, 2) for x in venue_vec]

        dim_explanations = []
        for i, dim in enumerate(VIBE_DIMS):
            diff = abs(query_vec[i] - venue_vec[i])
            if diff < 0.2:
                dim_explanations.append(f"{dim} ✓")
            elif diff > 0.4:
                dim_explanations.append(f"{dim} △ (差距{diff:.1f})")
        v_copy["dim_match"] = dim_explanations

        results.append(v_copy)

    results.sort(key=lambda x: -x["match_score"])
    return results


def get_venue_profile(poi_id: str, venues: list[dict] | None = None) -> dict | None:
    if venues is None:
        venues = load_venues()
    for v in venues:
        if v["id"] == poi_id:
            vec = venue_to_vector(v)
            return {
                "venue": v,
                "vector": {dim: round(vec[i], 2) for i, dim in enumerate(VIBE_DIMS)},
                "radar": {
                    dim: _dim_label(dim, vec[i])
                    for i, dim in enumerate(VIBE_DIMS)
                },
            }
    return None


def compare_venues(id_a: str, id_b: str, venues: list[dict] | None = None) -> dict:
    if venues is None:
        venues = load_venues()
    a = get_venue_profile(id_a, venues)
    b = get_venue_profile(id_b, venues)
    if not a or not b:
        return {"error": "venue not found"}
    vec_a = venue_to_vector(a["venue"])
    vec_b = venue_to_vector(b["venue"])
    sim = cosine_similarity(vec_a, vec_b)
    diffs = {}
    for i, dim in enumerate(VIBE_DIMS):
        diffs[dim] = {
            "a": round(vec_a[i], 2),
            "b": round(vec_b[i], 2),
            "diff": round(abs(vec_a[i] - vec_b[i]), 2),
        }
    return {
        "venue_a": {"id": id_a, "name": a["venue"]["name"]},
        "venue_b": {"id": id_b, "name": b["venue"]["name"]},
        "similarity": round(sim, 3),
        "dimensions": diffs,
    }


def _dim_label(dim: str, val: float) -> str:
    labels = {
        "noise_level": ("安静", "喧闹"),
        "light": ("昏暗", "明亮"),
        "crowd_density": ("清静", "热闹"),
        "social_vibe": ("独处", "社交"),
        "energy": ("放松", "活力"),
        "aesthetic": ("粗犷", "精致"),
        "outdoor_ratio": ("室内", "户外"),
    }
    low, high = labels.get(dim, ("低", "高"))
    if val < 0.3:
        return low
    if val > 0.7:
        return high
    return f"{low}偏{high}" if val > 0.5 else f"{high}偏{low}"
