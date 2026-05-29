"""Geographic helpers for scenario route generation."""

from __future__ import annotations

import math

EARTH_RADIUS_M = 6_371_000.0

# Reference locations (WGS-84)
BROMMA = (59.3544, 17.9417)
VISBY = (57.6628, 18.3462)
KALININGRAD = (54.7100, 20.5117)
STOCKHOLM_RADAR = (59.3500, 18.0500)  # Notional monoradar / SDPS reference


def bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Initial bearing from point 1 to point 2 (0=N, 90=E)."""
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dlam = math.radians(lon2 - lon1)
    y = math.sin(dlam) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlam)
    return (math.degrees(math.atan2(y, x)) + 360.0) % 360.0


def distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Haversine distance in metres."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


def polar_from_radar(
    target_lat: float,
    target_lon: float,
    radar_lat: float = STOCKHOLM_RADAR[0],
    radar_lon: float = STOCKHOLM_RADAR[1],
) -> tuple[float, float]:
    """Approximate range (NM) and azimuth (deg) from radar to target."""
    dist_m = distance_m(radar_lat, radar_lon, target_lat, target_lon)
    rho_nm = dist_m / 1852.0
    theta_deg = bearing_deg(radar_lat, radar_lon, target_lat, target_lon)
    return rho_nm, theta_deg
