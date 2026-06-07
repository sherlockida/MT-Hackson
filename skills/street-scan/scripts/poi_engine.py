"""POI spatial matching engine for street-scan."""
from __future__ import annotations
import json
import os
from pathlib import Path

MOCK_DATA_PATH = Path(__file__).resolve().parent.parent / "mock_data" / "pois.json"


def load_pois(path: str | None = None) -> list[dict]:
    p = Path(path) if path else MOCK_DATA_PATH
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def filter_by_radius(pois: list[dict], lat: float, lng: float,
                     radius_m: float, heading: str | None = None) -> list[dict]:
    from common_geo import haversine, bearing_label
    results = []
    for poi in pois:
        dist = haversine(lat, lng, poi["lat"], poi["lng"])
        if dist <= radius_m:
            direction = bearing_label(lat, lng, poi["lat"], poi["lng"])
            if heading and direction != heading and not _heading_compatible(direction, heading):
                continue
            poi_copy = dict(poi)
            poi_copy["distance_m"] = round(dist)
            poi_copy["direction"] = direction
            results.append(poi_copy)
    return results


def _heading_compatible(direction: str, heading: str) -> bool:
    adjacent = {
        "北": ["东北", "西北"], "东北": ["北", "东"], "东": ["东北", "东南"],
        "东南": ["东", "南"], "南": ["东南", "西南"], "西南": ["南", "西"],
        "西": ["西南", "西北"], "西北": ["西", "北"],
    }
    return direction in adjacent.get(heading, [])


def filter_open_now(pois: list[dict], hour: int | None = None) -> list[dict]:
    if hour is None:
        from datetime import datetime
        hour = datetime.now().hour
    results = []
    for poi in pois:
        h = poi.get("hours", {})
        open_h = int(h.get("open", "00:00").split(":")[0])
        close_h = int(h.get("close", "23:59").split(":")[0])
        if close_h == 0:
            close_h = 24
        if close_h < open_h:
            if hour >= open_h or hour < close_h:
                results.append(poi)
        elif open_h <= hour < close_h:
            results.append(poi)
    return results
