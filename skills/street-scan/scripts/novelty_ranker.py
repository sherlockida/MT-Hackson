"""Novelty-first ranking algorithm for street-scan."""
from __future__ import annotations
import json
import time
from pathlib import Path

USER_DATA_PATH = Path(__file__).resolve().parent.parent.parent.parent / "data" / "user_profiles.json"


def load_user_profile(user_id: str, path: str | None = None) -> dict:
    p = Path(path) if path else USER_DATA_PATH
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    for u in data.get("users", []):
        if u["id"] == user_id:
            return u
    return {
        "id": user_id, "visited_pois": [], "search_history": [],
        "taste_profile": {}, "dietary_exclude": [], "spice_tolerance": "medium",
    }


def rank_pois(pois: list[dict], user_id: str, context: dict | None = None) -> list[dict]:
    user = load_user_profile(user_id)
    context = context or {}
    scored = []
    for poi in pois:
        novelty = compute_novelty(poi, user)
        serendipity = compute_serendipity(poi, user)
        contextual = compute_contextual_fit(poi, context)
        total = 0.45 * novelty + 0.30 * serendipity + 0.25 * contextual
        poi_result = dict(poi)
        poi_result["novelty_score"] = round(novelty, 3)
        poi_result["serendipity_score"] = round(serendipity, 3)
        poi_result["contextual_score"] = round(contextual, 3)
        poi_result["total_score"] = round(total, 3)
        poi_result["why"] = generate_why(poi, user, novelty, serendipity)
        scored.append(poi_result)
    scored.sort(key=lambda x: -x["total_score"])
    return scored


def compute_novelty(poi: dict, user: dict) -> float:
    visited = set(user.get("visited_pois", []))
    store_novel = 0.0 if poi["id"] in visited else 0.4
    cat = poi.get("category", "")
    taste = user.get("taste_profile", {})
    if cat in taste:
        recency_factor = min(1.0, taste[cat].get("count", 0) / 10)
        cat_novel = 0.3 * (1 - recency_factor)
    else:
        cat_novel = 0.3
    area = poi.get("area", "")
    area_visits = sum(1 for pid in visited if area and area in pid)
    area_novel = 0.3 * (1 - min(1.0, area_visits / 5))
    return min(1.0, store_novel + cat_novel + area_novel)


def compute_serendipity(poi: dict, user: dict) -> float:
    search_hist = set(user.get("search_history", []))
    taste = user.get("taste_profile", {})
    cat = poi.get("category", "")
    subcat = poi.get("subcategory", "")
    never_searched = 1.0 if cat not in search_hist and subcat not in search_hist else 0.0
    unrated = 0.5 if cat not in taste else 0.0
    opened = poi.get("opened_months", 12)
    is_new = 0.3 if opened < 3 else 0.0
    return min(1.0, never_searched * 0.4 + unrated * 0.3 + is_new * 0.3)


def compute_contextual_fit(poi: dict, context: dict) -> float:
    score = 0.5
    hour = context.get("hour")
    if hour is not None:
        h = poi.get("hours", {})
        open_h = int(h.get("open", "00:00").split(":")[0])
        close_h = int(h.get("close", "23:59").split(":")[0])
        if close_h == 0:
            close_h = 24
        if open_h <= hour < close_h:
            remaining = close_h - hour
            score += 0.2 if remaining >= 2 else 0.1
    mood = context.get("mood", "")
    if mood:
        tags = set(poi.get("tags", []))
        mood_words = set(mood)
        if tags & mood_words:
            score += 0.2
    dist = poi.get("distance_m", 500)
    if dist < 200:
        score += 0.1
    elif dist < 400:
        score += 0.05
    return min(1.0, score)


def generate_why(poi: dict, user: dict, novelty: float, serendipity: float) -> str:
    reasons = []
    visited = set(user.get("visited_pois", []))
    taste = user.get("taste_profile", {})
    cat = poi.get("category", "")
    if poi["id"] not in visited:
        if cat not in taste:
            reasons.append(f"你还没试过{cat}，这是全新体验")
        else:
            reasons.append(f"这家{cat}你没来过")
    opened = poi.get("opened_months", 12)
    if opened < 3:
        reasons.append(f"新店，开业才 {opened} 个月")
    if serendipity > 0.6:
        reasons.append("意外发现，可能给你惊喜")
    sig = poi.get("signature", "")
    if sig:
        reasons.append(sig)
    return "; ".join(reasons[:2]) if reasons else "值得一逛"
