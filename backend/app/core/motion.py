"""Route interpolation for scenario steps — move tracks/plots along waypoints."""

from __future__ import annotations

import copy
import math
from typing import Any

from app.models.schemas import MotionMode, MotionWaypoint, StepMotion

_WGS84_M_PER_DEG_LAT = 111_320.0


def step_send_count(step_repeat: int, motion: StepMotion | None) -> int:
    if not motion or not motion.enabled:
        return step_repeat
    if motion.mode == MotionMode.DIRECTION:
        return motion.ticks
    if len(motion.waypoints) >= 2:
        return motion.ticks
    return step_repeat


def apply_step_motion(
    category: int,
    base_fields: dict[str, Any],
    motion: StepMotion,
    tick: int,
    total_ticks: int,
) -> dict[str, Any]:
    """Return field values for one tick along the route."""
    if not motion.enabled:
        return copy.deepcopy(base_fields)

    if motion.mode == MotionMode.DIRECTION:
        interpolated = _waypoint_at_direction(category, base_fields, motion, tick)
    elif len(motion.waypoints) >= 2:
        fraction = tick / (total_ticks - 1) if total_ticks > 1 else 0.0
        interpolated = _interpolate_waypoints(motion.waypoints, fraction)
    else:
        return copy.deepcopy(base_fields)

    fields = copy.deepcopy(base_fields)
    _apply_waypoint_to_fields(category, fields, interpolated)

    if motion.update_time and "time_of_track" in fields:
        base_time = float(base_fields.get("time_of_track", 0.0))
        fields["time_of_track"] = base_time + tick * motion.tick_interval_ms / 1000.0

    if motion.update_time and "time_of_applicability_position" in fields:
        base_time = float(base_fields.get("time_of_applicability_position", 0.0))
        fields["time_of_applicability_position"] = base_time + tick * motion.tick_interval_ms / 1000.0

    if motion.update_time and "time_of_day" in fields:
        base_time = float(base_fields.get("time_of_day", 0.0))
        fields["time_of_day"] = base_time + tick * motion.tick_interval_ms / 1000.0

    if motion.derive_velocity and category == 62:
        if tick > 0:
            prev = (
                _waypoint_at_direction(category, base_fields, motion, tick - 1)
                if motion.mode == MotionMode.DIRECTION
                else _interpolate_waypoints(
                    motion.waypoints,
                    (tick - 1) / (total_ticks - 1) if total_ticks > 1 else 0.0,
                )
            )
            _apply_derived_velocity(fields, interpolated, prev, motion.tick_interval_ms)
        elif motion.mode == MotionMode.DIRECTION:
            _apply_constant_velocity(fields, motion.heading_deg, motion.step_distance, motion.tick_interval_ms)

    return fields


def _waypoint_at_direction(
    category: int,
    base_fields: dict[str, Any],
    motion: StepMotion,
    tick: int,
) -> MotionWaypoint:
    start = waypoint_from_fields(category, base_fields)
    distance = tick * motion.step_distance
    heading_rad = math.radians(motion.heading_deg)

    if category == 62:
        position_type = int(base_fields.get("position_type", 2))
        if position_type == 1:
            dx = distance * math.sin(heading_rad)
            dy = distance * math.cos(heading_rad)
            return MotionWaypoint(
                x_m=(start.x_m or 0.0) + dx,
                y_m=(start.y_m or 0.0) + dy,
                geometric_altitude_ft=start.geometric_altitude_ft,
                flight_level=start.flight_level,
            )
        dn = distance * math.cos(heading_rad)
        de = distance * math.sin(heading_rad)
        lat = (start.latitude_deg or 0.0) + dn / _WGS84_M_PER_DEG_LAT
        lon_base = math.cos(math.radians(start.latitude_deg or 0.0)) * _WGS84_M_PER_DEG_LAT
        lon = (start.longitude_deg or 0.0) + de / lon_base if lon_base else (start.longitude_deg or 0.0)
        return MotionWaypoint(
            latitude_deg=lat,
            longitude_deg=lon,
            geometric_altitude_ft=start.geometric_altitude_ft,
            flight_level=start.flight_level,
        )

    if category == 21:
        dn = distance * math.cos(heading_rad)
        de = distance * math.sin(heading_rad)
        lat = (start.latitude_deg or 0.0) + dn / _WGS84_M_PER_DEG_LAT
        lon_base = math.cos(math.radians(start.latitude_deg or 0.0)) * _WGS84_M_PER_DEG_LAT
        lon = (start.longitude_deg or 0.0) + de / lon_base if lon_base else (start.longitude_deg or 0.0)
        return MotionWaypoint(
            latitude_deg=lat,
            longitude_deg=lon,
            geometric_altitude_ft=start.geometric_altitude_ft,
            flight_level=start.flight_level,
        )

    if category == 48:
        return MotionWaypoint(
            rho_nm=min((start.rho_nm or 0.0) + distance, 256.0),
            theta_deg=motion.heading_deg % 360.0,
        )

    if category == 34:
        return MotionWaypoint(azimuth=((start.azimuth or 0.0) + distance) % 360.0)

    if category == 240:
        return MotionWaypoint(azimuth=((start.azimuth or 0.0) + distance) % 360.0)

    return start


def _apply_constant_velocity(
    fields: dict[str, Any],
    heading_deg: float,
    step_distance: float,
    tick_interval_ms: int,
) -> None:
    dt = tick_interval_ms / 1000.0
    if dt <= 0:
        return
    heading_rad = math.radians(heading_deg)
    speed = step_distance / dt
    velocity = fields.setdefault("velocity", {})
    velocity["vx_mps"] = speed * math.sin(heading_rad)
    velocity["vy_mps"] = speed * math.cos(heading_rad)
    fields["include_velocity"] = 1


def _interpolate_waypoints(waypoints: list[MotionWaypoint], fraction: float) -> MotionWaypoint:
    fraction = max(0.0, min(1.0, fraction))
    if len(waypoints) == 1:
        return waypoints[0]

    segment_count = len(waypoints) - 1
    scaled = fraction * segment_count
    index = min(int(scaled), segment_count - 1)
    local_t = scaled - index
    start = waypoints[index]
    end = waypoints[index + 1]
    return _lerp_waypoint(start, end, local_t)


def _lerp_waypoint(a: MotionWaypoint, b: MotionWaypoint, t: float) -> MotionWaypoint:
    return MotionWaypoint(
        latitude_deg=_lerp_optional(a.latitude_deg, b.latitude_deg, t),
        longitude_deg=_lerp_optional(a.longitude_deg, b.longitude_deg, t),
        x_m=_lerp_optional(a.x_m, b.x_m, t),
        y_m=_lerp_optional(a.y_m, b.y_m, t),
        rho_nm=_lerp_optional(a.rho_nm, b.rho_nm, t),
        theta_deg=_lerp_angular(a.theta_deg, b.theta_deg, t),
        range_m=_lerp_optional(a.range_m, b.range_m, t),
        azimuth=_lerp_angular(a.azimuth, b.azimuth, t),
        geometric_altitude_ft=_lerp_optional(a.geometric_altitude_ft, b.geometric_altitude_ft, t),
        flight_level=_lerp_optional(a.flight_level, b.flight_level, t),
    )


def _lerp_optional(a: float | None, b: float | None, t: float) -> float | None:
    if a is None and b is None:
        return None
    if a is None:
        return b
    if b is None:
        return a
    return a + (b - a) * t


def _lerp_angular(a: float | None, b: float | None, t: float) -> float | None:
    if a is None and b is None:
        return None
    if a is None:
        return b
    if b is None:
        return a
    delta = ((b - a + 180) % 360) - 180
    return (a + delta * t) % 360


def _apply_waypoint_to_fields(
    category: int,
    fields: dict[str, Any],
    waypoint: MotionWaypoint,
) -> None:
    if category == 62:
        position_type = int(fields.get("position_type", 2))
        if position_type == 1:
            if waypoint.x_m is not None or waypoint.y_m is not None:
                cart = fields.setdefault("cartesian", {})
                if waypoint.x_m is not None:
                    cart["x_m"] = waypoint.x_m
                if waypoint.y_m is not None:
                    cart["y_m"] = waypoint.y_m
        elif position_type == 2:
            if waypoint.latitude_deg is not None or waypoint.longitude_deg is not None:
                wgs = fields.setdefault("wgs84", {})
                if waypoint.latitude_deg is not None:
                    wgs["latitude_deg"] = waypoint.latitude_deg
                if waypoint.longitude_deg is not None:
                    wgs["longitude_deg"] = waypoint.longitude_deg
        if waypoint.geometric_altitude_ft is not None:
            fields["geometric_altitude_ft"] = waypoint.geometric_altitude_ft
        if waypoint.flight_level is not None:
            fields["flight_level"] = waypoint.flight_level
    elif category == 21:
        if waypoint.latitude_deg is not None or waypoint.longitude_deg is not None:
            wgs = fields.setdefault("wgs84", {})
            if waypoint.latitude_deg is not None:
                wgs["latitude_deg"] = waypoint.latitude_deg
            if waypoint.longitude_deg is not None:
                wgs["longitude_deg"] = waypoint.longitude_deg
        if waypoint.flight_level is not None:
            fields["flight_level"] = waypoint.flight_level
        if waypoint.geometric_altitude_ft is not None:
            fields["geometric_height_ft"] = waypoint.geometric_altitude_ft
    elif category == 48:
        if waypoint.rho_nm is not None or waypoint.theta_deg is not None:
            pos = fields.setdefault("position", {})
            if waypoint.rho_nm is not None:
                pos["rho_nm"] = waypoint.rho_nm
            if waypoint.theta_deg is not None:
                pos["theta_deg"] = waypoint.theta_deg
    elif category == 15:
        position_type = int(fields.get("position_type", 2))
        if position_type == 1:
            if waypoint.latitude_deg is not None or waypoint.longitude_deg is not None:
                wgs = fields.setdefault("wgs84", {})
                if waypoint.latitude_deg is not None:
                    wgs["latitude_deg"] = waypoint.latitude_deg
                if waypoint.longitude_deg is not None:
                    wgs["longitude_deg"] = waypoint.longitude_deg
        elif position_type == 2:
            if waypoint.range_m is not None or waypoint.azimuth is not None:
                ra = fields.setdefault("range_azimuth", {})
                if waypoint.range_m is not None:
                    ra["range_m"] = waypoint.range_m
                if waypoint.azimuth is not None:
                    ra["azimuth_deg"] = waypoint.azimuth
    elif category == 34:
        if waypoint.azimuth is not None:
            fields["azimuth"] = waypoint.azimuth
    elif category == 240:
        if waypoint.azimuth is not None:
            header = fields.setdefault("video_header", {})
            start_az = float(header.get("start_az_deg", 0.0))
            end_az = float(header.get("end_az_deg", 2.0))
            beam = (end_az - start_az) % 360.0
            if beam > 180.0 or beam < 0.1:
                beam = 3.0
            center = waypoint.azimuth % 360.0
            header["start_az_deg"] = (center - beam / 2.0) % 360.0
            header["end_az_deg"] = (center + beam / 2.0) % 360.0


def _apply_derived_velocity(
    fields: dict[str, Any],
    current: MotionWaypoint,
    previous: MotionWaypoint,
    tick_interval_ms: int,
) -> None:
    dt = tick_interval_ms / 1000.0
    if dt <= 0:
        return

    position_type = int(fields.get("position_type", 2))
    velocity = fields.setdefault("velocity", {})

    if position_type == 1 and current.x_m is not None and previous.x_m is not None:
        velocity["vx_mps"] = (current.x_m - previous.x_m) / dt
        velocity["vy_mps"] = (current.y_m - previous.y_m) / dt if current.y_m is not None and previous.y_m is not None else 0.0
        fields["include_velocity"] = 1
    elif (
        position_type == 2
        and current.latitude_deg is not None
        and previous.latitude_deg is not None
        and current.longitude_deg is not None
        and previous.longitude_deg is not None
    ):
        lat_mid = math.radians((current.latitude_deg + previous.latitude_deg) / 2.0)
        dy_m = (current.latitude_deg - previous.latitude_deg) * _WGS84_M_PER_DEG_LAT
        dx_m = (current.longitude_deg - previous.longitude_deg) * _WGS84_M_PER_DEG_LAT * math.cos(lat_mid)
        velocity["vx_mps"] = dx_m / dt
        velocity["vy_mps"] = dy_m / dt
        fields["include_velocity"] = 1


def waypoint_from_fields(category: int, fields: dict[str, Any]) -> MotionWaypoint:
    """Extract animatable position from message fields."""
    if category == 62:
        position_type = int(fields.get("position_type", 2))
        wgs = fields.get("wgs84", {})
        cart = fields.get("cartesian", {})
        return MotionWaypoint(
            latitude_deg=float(wgs.get("latitude_deg", 0.0)) if position_type == 2 else None,
            longitude_deg=float(wgs.get("longitude_deg", 0.0)) if position_type == 2 else None,
            x_m=float(cart.get("x_m", 0.0)) if position_type == 1 else None,
            y_m=float(cart.get("y_m", 0.0)) if position_type == 1 else None,
            geometric_altitude_ft=float(fields.get("geometric_altitude_ft", 0.0)) or None,
            flight_level=float(fields.get("flight_level", 0.0)) or None,
        )
    if category == 48:
        pos = fields.get("position", {})
        return MotionWaypoint(
            rho_nm=float(pos.get("rho_nm", 0.0)),
            theta_deg=float(pos.get("theta_deg", 0.0)),
        )
    if category == 15:
        position_type = int(fields.get("position_type", 2))
        wgs = fields.get("wgs84", {})
        ra = fields.get("range_azimuth", {})
        if position_type == 1:
            return MotionWaypoint(
                latitude_deg=float(wgs.get("latitude_deg", 0.0)),
                longitude_deg=float(wgs.get("longitude_deg", 0.0)),
            )
        return MotionWaypoint(
            range_m=float(ra.get("range_m", 0.0)),
            azimuth=float(ra.get("azimuth_deg", 0.0)),
        )
    if category == 21:
        wgs = fields.get("wgs84", {})
        return MotionWaypoint(
            latitude_deg=float(wgs.get("latitude_deg", 0.0)),
            longitude_deg=float(wgs.get("longitude_deg", 0.0)),
            flight_level=float(fields.get("flight_level", 0.0)) or None,
            geometric_altitude_ft=float(fields.get("geometric_height_ft", 0.0)) or None,
        )
    if category == 34:
        return MotionWaypoint(azimuth=float(fields.get("azimuth", 0.0)))
    if category == 240:
        header = fields.get("video_header", {})
        start_az = float(header.get("start_az_deg", 0.0))
        end_az = float(header.get("end_az_deg", 2.0))
        center = (start_az + end_az) / 2.0
        if end_az < start_az:
            center = (start_az + end_az + 360.0) / 2.0 % 360.0
        return MotionWaypoint(azimuth=center % 360.0)
    return MotionWaypoint()


def default_step_distance(category: int) -> float:
    if category == 48:
        return 1.0
    if category == 34:
        return 10.0
    if category == 240:
        return 2.0
    if category == 15:
        return 1000.0
    return 1000.0


def default_end_waypoint(category: int, fields: dict[str, Any]) -> MotionWaypoint:
    """Build a sensible end waypoint offset from the current message."""
    start = waypoint_from_fields(category, fields)
    if category == 62:
        position_type = int(fields.get("position_type", 2))
        if position_type == 1:
            return MotionWaypoint(
                x_m=(start.x_m or 0.0) + 10_000.0,
                y_m=(start.y_m or 0.0) + 5_000.0,
                geometric_altitude_ft=start.geometric_altitude_ft,
                flight_level=start.flight_level,
            )
        return MotionWaypoint(
            latitude_deg=(start.latitude_deg or 0.0) + 0.08,
            longitude_deg=(start.longitude_deg or 0.0) + 0.12,
            geometric_altitude_ft=start.geometric_altitude_ft,
            flight_level=start.flight_level,
        )
    if category == 48:
        return MotionWaypoint(
            rho_nm=min((start.rho_nm or 0.0) + 20.0, 256.0),
            theta_deg=((start.theta_deg or 0.0) + 90.0) % 360.0,
        )
    if category == 15:
        position_type = int(fields.get("position_type", 2))
        if position_type == 1:
            return MotionWaypoint(
                latitude_deg=(start.latitude_deg or 0.0) + 0.08,
                longitude_deg=(start.longitude_deg or 0.0) + 0.12,
            )
        return MotionWaypoint(
            range_m=(start.range_m or 0.0) + 10_000.0,
            azimuth=((start.azimuth or 0.0) + 45.0) % 360.0,
        )
    if category == 21:
        return MotionWaypoint(
            latitude_deg=(start.latitude_deg or 0.0) + 0.08,
            longitude_deg=(start.longitude_deg or 0.0) + 0.12,
            flight_level=start.flight_level,
            geometric_altitude_ft=start.geometric_altitude_ft,
        )
    if category == 34:
        return MotionWaypoint(azimuth=((start.azimuth or 0.0) + 90.0) % 360.0)
    if category == 240:
        return MotionWaypoint(azimuth=((start.azimuth or 0.0) + 90.0) % 360.0)
    return MotionWaypoint()
