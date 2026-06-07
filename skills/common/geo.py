"""Haversine distance and geo utilities."""
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


def bearing_label(lat1: float, lng1: float, lat2: float, lng2: float) -> str:
    dlng = math.radians(lng2 - lng1)
    lat1_r, lat2_r = math.radians(lat1), math.radians(lat2)
    x = math.sin(dlng) * math.cos(lat2_r)
    y = math.cos(lat1_r) * math.sin(lat2_r) - math.sin(lat1_r) * math.cos(lat2_r) * math.cos(dlng)
    brng = math.degrees(math.atan2(x, y))
    brng = (brng + 360) % 360
    dirs = ["北", "东北", "东", "东南", "南", "西南", "西", "西北"]
    return dirs[round(brng / 45) % 8]


def walk_instruction(dist_m: float, direction: str) -> str:
    if dist_m < 100:
        return f"{direction}方向，步行约 {int(dist_m)} 米"
    minutes = max(1, round(dist_m / 80))
    return f"{direction}方向，步行约 {minutes} 分钟（{int(dist_m)} 米）"
