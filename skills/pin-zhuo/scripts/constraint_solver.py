"""CSP constraint solver for group dining - pin-zhuo core algorithm."""
from __future__ import annotations
import json
from pathlib import Path
from common_geo import haversine, geo_midpoint

RESTAURANT_DATA_PATH = Path(__file__).resolve().parent.parent / "mock_data" / "restaurants.json"


def load_restaurants(path: str | None = None) -> list[dict]:
    p = Path(path) if path else RESTAURANT_DATA_PATH
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def satisfies_hard(restaurant: dict, constraint: dict) -> tuple[bool, list[str]]:
    violations = []
    excludes = set(constraint.get("dietary_exclude", []))
    menu_tags = set(restaurant.get("menu_tags", []))
    conflicting = excludes & menu_tags
    if conflicting and not restaurant.get("has_allergen_free_options", False):
        violations.append(f"含有忌口食材: {', '.join(conflicting)}")

    budget = constraint.get("budget_max", 999)
    if restaurant.get("avg_price", 0) > budget * 1.1:
        violations.append(f"人均¥{restaurant['avg_price']} 超出预算¥{budget}")

    time_windows = constraint.get("time_windows", [])
    if time_windows:
        hours = restaurant.get("hours", {})
        r_open = hours.get("open", "00:00")
        r_close = hours.get("close", "23:59")
        has_overlap = False
        for tw in time_windows:
            if "-" in tw:
                tw_start, tw_end = tw.split("-")
                if tw_start <= r_close and tw_end >= r_open:
                    has_overlap = True
                    break
        if not has_overlap:
            violations.append(f"营业时间 {r_open}-{r_close} 与可用时间不匹配")

    return len(violations) == 0, violations


def score_for_member(restaurant: dict, constraint: dict, midpoint: dict) -> dict:
    score = 0.0
    met = []
    stretched = []

    excludes = set(constraint.get("dietary_exclude", []))
    menu_tags = set(restaurant.get("menu_tags", []))
    if not (excludes & menu_tags):
        met.append("dietary")
        score += 0.25
    elif restaurant.get("has_allergen_free_options", False):
        met.append("dietary")
        stretched.append(f"含有{', '.join(excludes & menu_tags)}但有替代选项")
        score += 0.15

    budget = constraint.get("budget_max", 999)
    price = restaurant.get("avg_price", 0)
    if price <= budget:
        met.append("budget")
        score += 0.25
    elif price <= budget * 1.1:
        met.append("budget")
        stretched.append(f"人均¥{price}, 略超预算¥{budget}")
        score += 0.15

    time_windows = constraint.get("time_windows", [])
    if time_windows:
        met.append("time")
        score += 0.15
    else:
        met.append("time")
        score += 0.15

    loc = constraint.get("location", {})
    dist = haversine(loc.get("lat", 0), loc.get("lng", 0),
                     restaurant["lat"], restaurant["lng"])
    dist_km = dist / 1000
    if dist_km < 2:
        met.append("distance")
        score += 0.2
    elif dist_km < 5:
        stretched.append(f"distance: {dist_km:.1f}km")
        score += 0.1
    else:
        stretched.append(f"distance: {dist_km:.1f}km (较远)")
        score += 0.05

    cuisine_prefs = set(constraint.get("cuisine_prefer", []))
    cuisine = restaurant.get("cuisine", "")
    if not cuisine_prefs or cuisine in cuisine_prefs:
        met.append("cuisine")
        score += 0.15
    else:
        stretched.append(f"cuisine: 不是首选但可接受")
        score += 0.05

    return {
        "score": round(min(1.0, score), 2),
        "met": met,
        "stretched": stretched,
        "distance_km": round(dist_km, 1),
    }


def solve(constraints: list[dict], restaurants: list[dict] | None = None) -> dict:
    if restaurants is None:
        restaurants = load_restaurants()

    feasible = []
    for r in restaurants:
        all_pass = True
        for c in constraints:
            passed, _ = satisfies_hard(r, c)
            if not passed:
                all_pass = False
                break
        if all_pass:
            feasible.append(r)

    if not feasible:
        feasible = relax_and_retry(constraints, restaurants)

    if not feasible:
        return {"solutions": [], "message": "无法找到满足所有约束的餐厅，请放宽条件"}

    locations = [c.get("location", {"lat": 39.95, "lng": 116.35}) for c in constraints]
    midpoint = geo_midpoint(locations)

    scored = []
    for r in feasible:
        per_member = {}
        for c in constraints:
            member = c.get("member_id", "unknown")
            per_member[member] = score_for_member(r, c, midpoint)

        scores = [s["score"] for s in per_member.values()]
        min_sat = min(scores) if scores else 0
        avg_sat = sum(scores) / len(scores) if scores else 0

        mid_dist = haversine(midpoint["lat"], midpoint["lng"], r["lat"], r["lng"])

        why = []
        all_dietary = all("dietary" in s["met"] for s in per_member.values())
        if all_dietary:
            why.append("满足所有人忌口")
        all_budget = all("budget" in s["met"] for s in per_member.values())
        if all_budget:
            why.append(f"人均¥{r['avg_price']}在预算内")
        why.append(f"距{len(constraints)}人位置中点{mid_dist/1000:.1f}km")

        scored.append({
            "restaurant": {
                "id": r["id"],
                "name": r["name"],
                "cuisine": r.get("cuisine", ""),
                "avg_price": r.get("avg_price", 0),
                "rating": r.get("rating", 0),
                "area": r.get("area", ""),
                "signature_dishes": r.get("signature_dishes", []),
            },
            "satisfaction": per_member,
            "fairness": round(min_sat, 2),
            "efficiency": round(avg_sat, 2),
            "geo_midpoint_distance_m": round(mid_dist),
            "why": why,
        })

    pareto = pareto_front(scored)
    return {"solutions": pareto[:3], "total_feasible": len(feasible)}


def relax_and_retry(constraints: list[dict], restaurants: list[dict]) -> list[dict]:
    relaxed = []
    for c in constraints:
        rc = dict(c)
        rc["budget_max"] = int(c.get("budget_max", 200) * 1.2)
        relaxed.append(rc)

    feasible = []
    for r in restaurants:
        all_pass = True
        for c in relaxed:
            passed, _ = satisfies_hard(r, c)
            if not passed:
                all_pass = False
                break
        if all_pass:
            feasible.append(r)
    return feasible


def pareto_front(solutions: list[dict]) -> list[dict]:
    if not solutions:
        return []
    result = []
    for s in solutions:
        dominated = False
        for other in solutions:
            if other is s:
                continue
            if (other["fairness"] >= s["fairness"] and
                    other["efficiency"] >= s["efficiency"] and
                    (other["fairness"] > s["fairness"] or other["efficiency"] > s["efficiency"])):
                dominated = True
                break
        if not dominated:
            result.append(s)
    result.sort(key=lambda x: -(x["fairness"] * 0.6 + x["efficiency"] * 0.4))
    if len(result) < 3 and len(solutions) >= 3:
        remaining = [s for s in solutions if s not in result]
        remaining.sort(key=lambda x: -(x["fairness"] * 0.6 + x["efficiency"] * 0.4))
        result.extend(remaining[:3 - len(result)])
    return result
