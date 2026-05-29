"""Unit tests for scenario route interpolation."""

import pytest

from app.core.motion import (
    apply_step_motion,
    default_end_waypoint,
    step_send_count,
    waypoint_from_fields,
)
from app.models.schemas import MotionMode, MotionWaypoint, StepMotion


@pytest.mark.unit
def test_step_send_count_uses_motion_ticks_when_enabled():
    motion = StepMotion(
        enabled=True,
        mode=MotionMode.WAYPOINTS,
        waypoints=[MotionWaypoint(), MotionWaypoint()],
        ticks=15,
    )
    assert step_send_count(1, motion) == 15
    assert step_send_count(5, StepMotion(enabled=False)) == 5


@pytest.mark.unit
def test_direction_mode_send_count_without_waypoints():
    motion = StepMotion(enabled=True, mode=MotionMode.DIRECTION, ticks=20)
    assert step_send_count(1, motion) == 20


@pytest.mark.unit
def test_wgs84_route_interpolates_midpoint():
    fields = {
        "position_type": 2,
        "wgs84": {"latitude_deg": 59.0, "longitude_deg": 18.0},
        "time_of_track": 100.0,
        "include_velocity": 0,
    }
    motion = StepMotion(
        enabled=True,
        mode=MotionMode.WAYPOINTS,
        waypoints=[
            MotionWaypoint(latitude_deg=59.0, longitude_deg=18.0),
            MotionWaypoint(latitude_deg=59.1, longitude_deg=18.2),
        ],
        ticks=3,
        tick_interval_ms=1000,
        update_time=True,
        derive_velocity=False,
    )
    mid = apply_step_motion(62, fields, motion, 1, 3)
    assert mid["wgs84"]["latitude_deg"] == pytest.approx(59.05)
    assert mid["wgs84"]["longitude_deg"] == pytest.approx(18.1)
    assert mid["time_of_track"] == pytest.approx(101.0)


@pytest.mark.unit
def test_cat048_route_interpolates_range():
    fields = {"position": {"rho_nm": 10.0, "theta_deg": 0.0}}
    motion = StepMotion(
        enabled=True,
        mode=MotionMode.WAYPOINTS,
        waypoints=[
            MotionWaypoint(rho_nm=10.0, theta_deg=0.0),
            MotionWaypoint(rho_nm=30.0, theta_deg=90.0),
        ],
        ticks=2,
        tick_interval_ms=500,
    )
    end = apply_step_motion(48, fields, motion, 1, 2)
    assert end["position"]["rho_nm"] == pytest.approx(30.0)
    assert end["position"]["theta_deg"] == pytest.approx(90.0)


@pytest.mark.unit
def test_cat034_route_interpolates_azimuth():
    fields = {"message_type": 2, "azimuth": 0.0}
    motion = StepMotion(
        enabled=True,
        mode=MotionMode.WAYPOINTS,
        waypoints=[
            MotionWaypoint(azimuth=0.0),
            MotionWaypoint(azimuth=180.0),
        ],
        ticks=2,
        tick_interval_ms=250,
    )
    end = apply_step_motion(34, fields, motion, 1, 2)
    assert end["azimuth"] == pytest.approx(180.0)


@pytest.mark.unit
def test_cartesian_velocity_is_derived():
    fields = {
        "position_type": 1,
        "cartesian": {"x_m": 0.0, "y_m": 0.0},
        "include_velocity": 0,
    }
    motion = StepMotion(
        enabled=True,
        mode=MotionMode.WAYPOINTS,
        waypoints=[
            MotionWaypoint(x_m=0.0, y_m=0.0),
            MotionWaypoint(x_m=1000.0, y_m=500.0),
        ],
        ticks=2,
        tick_interval_ms=1000,
        derive_velocity=True,
    )
    end = apply_step_motion(62, fields, motion, 1, 2)
    assert end["velocity"]["vx_mps"] == pytest.approx(1000.0)
    assert end["velocity"]["vy_mps"] == pytest.approx(500.0)
    assert end["include_velocity"] == 1


@pytest.mark.unit
def test_direction_mode_moves_wgs84_east():
    fields = {
        "position_type": 2,
        "wgs84": {"latitude_deg": 59.0, "longitude_deg": 18.0},
        "time_of_track": 100.0,
        "include_velocity": 0,
    }
    motion = StepMotion(
        enabled=True,
        mode=MotionMode.DIRECTION,
        heading_deg=90.0,
        step_distance=1000.0,
        ticks=5,
        tick_interval_ms=1000,
        derive_velocity=False,
    )
    tick2 = apply_step_motion(62, fields, motion, 2, 5)
    assert tick2["wgs84"]["latitude_deg"] == pytest.approx(59.0, abs=0.001)
    assert tick2["wgs84"]["longitude_deg"] > 18.0


@pytest.mark.unit
def test_default_end_waypoint_offsets_wgs84():
    fields = {
        "position_type": 2,
        "wgs84": {"latitude_deg": 59.3293, "longitude_deg": 18.0686},
    }
    start = waypoint_from_fields(62, fields)
    end = default_end_waypoint(62, fields)
    assert end.latitude_deg > start.latitude_deg
    assert end.longitude_deg > start.longitude_deg
