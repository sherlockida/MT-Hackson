"""Haversine distance and geo utilities (local copy for pin-zhuo)."""
import math


def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def geo_midpoint(points: list[dict]) -> dict:
    x = y = z = 0.0
    for p in points:
        lat_r, lng_r = math.radians(p["lat"]), math.radians(p["lng"])
        x += math.cos(lat_r) * math.cos(lng_r)
        y += math.cos(lat_r) * math.sin(lng_r)
        z += math.sin(lat_r)
    n = len(points)
    x, y, z = x / n, y / n, z / n
    lng_mid = math.atan2(y, x)
    hyp = math.sqrt(x * x + y * y)
    lat_mid = math.atan2(z, hyp)
    return {"lat": math.degrees(lat_mid), "lng": math.degrees(lng_mid)}
