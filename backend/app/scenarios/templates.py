"""Realistic multi-category ASTERIX scenario templates."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from app.models.schemas import (
    AsterixMessage,
    MotionMode,
    MotionWaypoint,
    Scenario,
    ScenarioStep,
    ScenarioTransport,
    StepMotion,
)
from app.scenarios.geo import (
    BROMMA,
    KALININGRAD,
    STOCKHOLM_RADAR,
    VISBY,
    bearing_deg,
    distance_m,
    polar_from_radar,
)

# System identifiers (SAC/SIC)
SDPS_SAC, SDPS_SIC = 1, 1
INCS_SAC, INCS_SIC = 1, 2
RADAR_SAC, RADAR_SIC = 2, 1
ADSB_SAC, ADSB_SIC = 3, 1


@dataclass
class TemplateParams:
    tick_interval_ms: int = 2000
    ticks: int = 60
    jas_track_number: int = 101
    mig_track_number: int = 201
    jas_mode3a: int = 7777
    mig_mode3a: int = 7770
    jas_flight_level: float = 350.0
    mig_flight_level: float = 410.0
    loop_count: int = 1
    host: str = "host.docker.internal"
    port: int = 8600


def list_template_catalog() -> list[dict[str, Any]]:
    return [
        {
            "id": "jas-bromma-visby",
            "name": "JAS 39 – Bromma → Visby",
            "description": (
                "Friendly Gripen transit using all ASTERIX categories: INCS config, "
                "monoradar service messages, plots, INCS target report, ADS-B report, "
                "SDPS service status, radar video, and SDPS system track."
            ),
            "aircraft": "JAS 39 Gripen",
            "route": "ESSB Bromma → ESSV Visby",
        },
        {
            "id": "mig-kaliningrad-visby",
            "name": "Hostile MiG – Kaliningrad → Visby",
            "description": (
                "Non-cooperative hostile track from Kaliningrad toward Visby. "
                "Full radar/INCS/SDPS/ADS-B picture across all implemented categories."
            ),
            "aircraft": "MiG-29 (hostile)",
            "route": "Kaliningrad → ESSV Visby",
        },
        {
            "id": "baltic-combined",
            "name": "Baltic exercise – JAS + MiG combined",
            "description": (
                "Combined air picture: friendly JAS on Stockholm–Visby route while "
                "hostile MiG approaches from Kaliningrad. Interleaved ASTERIX traffic "
                "including ADS-B reports."
            ),
            "aircraft": "JAS 39 + MiG-29",
            "route": "Baltic Sea airspace",
        },
    ]


def build_template(template_id: str, params: TemplateParams | None = None) -> Scenario:
    p = params or TemplateParams()
    builders = {
        "jas-bromma-visby": _build_jas_bromma_visby,
        "mig-kaliningrad-visby": _build_mig_kaliningrad_visby,
        "baltic-combined": _build_baltic_combined,
    }
    if template_id not in builders:
        raise KeyError(f"Unknown scenario template: {template_id}")
    return builders[template_id](p)


def _transport(p: TemplateParams) -> ScenarioTransport:
    return ScenarioTransport(host=p.host, port=p.port, protocol="udp")


def _motion_wgs(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
    p: TemplateParams,
    *,
    derive_velocity: bool = True,
) -> StepMotion:
    heading = bearing_deg(start_lat, start_lon, end_lat, end_lon)
    dist = distance_m(start_lat, start_lon, end_lat, end_lon)
    step_distance = max(dist / max(p.ticks - 1, 1), 500.0)
    return StepMotion(
        enabled=True,
        mode=MotionMode.DIRECTION,
        waypoints=[
            MotionWaypoint(latitude_deg=start_lat, longitude_deg=start_lon),
            MotionWaypoint(latitude_deg=end_lat, longitude_deg=end_lon),
        ],
        heading_deg=heading,
        step_distance=step_distance,
        ticks=p.ticks,
        tick_interval_ms=p.tick_interval_ms,
        update_time=True,
        derive_velocity=derive_velocity,
    )


def _motion_polar(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
    p: TemplateParams,
) -> StepMotion:
    rho0, theta0 = polar_from_radar(start_lat, start_lon)
    rho1, theta1 = polar_from_radar(end_lat, end_lon)
    heading = bearing_deg(*STOCKHOLM_RADAR, end_lat, end_lon)
    step_nm = max(abs(rho1 - rho0) / max(p.ticks - 1, 1), 0.5)
    return StepMotion(
        enabled=True,
        mode=MotionMode.DIRECTION,
        waypoints=[
            MotionWaypoint(rho_nm=rho0, theta_deg=theta0),
            MotionWaypoint(rho_nm=rho1, theta_deg=theta1),
        ],
        heading_deg=heading,
        step_distance=step_nm,
        ticks=p.ticks,
        tick_interval_ms=p.tick_interval_ms,
        update_time=False,
        derive_velocity=False,
    )


def _motion_range_azimuth(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
    p: TemplateParams,
) -> StepMotion:
    dist0 = distance_m(*STOCKHOLM_RADAR, start_lat, start_lon)
    dist1 = distance_m(*STOCKHOLM_RADAR, end_lat, end_lon)
    az = bearing_deg(*STOCKHOLM_RADAR, end_lat, end_lon)
    step_m = max(abs(dist1 - dist0) / max(p.ticks - 1, 1), 500.0)
    return StepMotion(
        enabled=True,
        mode=MotionMode.DIRECTION,
        waypoints=[
            MotionWaypoint(range_m=dist0, azimuth=az),
            MotionWaypoint(range_m=dist1, azimuth=az),
        ],
        heading_deg=az,
        step_distance=step_m,
        ticks=p.ticks,
        tick_interval_ms=p.tick_interval_ms,
        update_time=True,
        derive_velocity=False,
    )


def _step(step_id: str, name: str, category: int, fields: dict, motion: StepMotion | None = None, **kw) -> ScenarioStep:
    return ScenarioStep(
        id=step_id,
        name=name,
        message=AsterixMessage(category=category, fields=fields),
        motion=motion,
        **kw,
    )


def _step_016_config(p: TemplateParams, step_id: str = "incs-config") -> ScenarioStep:
    return _step(
        step_id,
        "INCS system configuration (Cat 016)",
        16,
        {
            "data_source": {"sac": INCS_SAC, "sic": INCS_SIC},
            "service_id": 1,
            "message_type": 1,
            "time_of_day": 36000.0,
            "reporting_period_s": 60,
            "pair": {"pair_id": 1, "transmitter_id": 10, "receiver_id": 20},
            "reference_point": {
                "latitude_deg": STOCKHOLM_RADAR[0],
                "longitude_deg": STOCKHOLM_RADAR[1],
                "height_m": 45.0,
            },
        },
        delay_ms=0,
    )


def _step_065_sdps_status(
    step_id: str,
    *,
    message_type: int = 1,
    service_status_report: int = 15,
    sdps_nogo: int = 0,
    include_service_status_report: int = 0,
    delay_ms: int = 100,
) -> ScenarioStep:
    fields: dict[str, Any] = {
        "data_source": {"sac": SDPS_SAC, "sic": SDPS_SIC},
        "message_type": message_type,
        "service_id": 1,
        "time_of_message": 36000.0,
        "include_sdps_configuration": 1 if message_type == 1 else 0,
        "sdps_configuration": {
            "nogo": sdps_nogo,
            "ovl": 0,
            "tsv": 0,
            "pss": 1,
            "sttn": 0,
        },
        "include_service_status_report": include_service_status_report,
        "service_status_report": service_status_report,
    }
    if message_type == 3:
        fields["include_service_status_report"] = 1
    name = {
        1: "SDPS operational status (Cat 065)",
        2: "SDPS end of batch (Cat 065)",
        3: "SDPS service status report (Cat 065)",
    }.get(message_type, "SDPS service status (Cat 065)")
    return _step(step_id, name, 65, fields, delay_ms=delay_ms)


def _motion_azimuth_sweep(center_az: float, p: TemplateParams, beam_width_deg: float = 3.0) -> StepMotion:
    return StepMotion(
        enabled=True,
        mode=MotionMode.DIRECTION,
        waypoints=[
            MotionWaypoint(azimuth=center_az),
            MotionWaypoint(azimuth=(center_az + 90.0) % 360.0),
        ],
        heading_deg=(center_az + 90.0) % 360.0,
        step_distance=beam_width_deg,
        ticks=p.ticks,
        tick_interval_ms=p.tick_interval_ms,
        update_time=True,
        derive_velocity=False,
    )


def _default_video_header(azimuth_deg: float, beam_width_deg: float = 3.0) -> dict[str, Any]:
    start = (azimuth_deg - beam_width_deg / 2.0) % 360.0
    end = (azimuth_deg + beam_width_deg / 2.0) % 360.0
    return {
        "start_az_deg": start,
        "end_az_deg": end,
        "start_range_cells": 0,
        "cell_duration_ns": 1000,
        "cell_duration_fs": 1_000_000,
    }


def _step_240_video_summary(step_id: str, summary: str, delay_ms: int = 0) -> ScenarioStep:
    return _step(
        step_id,
        "Radar video summary (Cat 240)",
        240,
        {
            "data_source": {"sac": RADAR_SAC, "sic": RADAR_SIC},
            "message_type": 1,
            "video_summary": summary,
        },
        delay_ms=delay_ms,
    )


def _step_240_video_radial(
    step_id: str,
    azimuth_deg: float,
    p: TemplateParams,
    *,
    video_sequence: int = 1,
    delay_ms: int = 0,
    beam_width_deg: float = 3.0,
) -> ScenarioStep:
    return _step(
        step_id,
        f"Radar video radial {azimuth_deg:.0f}° (Cat 240)",
        240,
        {
            "data_source": {"sac": RADAR_SAC, "sic": RADAR_SIC},
            "message_type": 2,
            "video_sequence": video_sequence,
            "header_format": "nano",
            "video_header": _default_video_header(azimuth_deg, beam_width_deg),
            "video_resolution": {"compression": 0, "resolution": 4},
            "video_block_format": "low",
            "video_cells_hex": "",
            "include_time_of_day": 1,
            "time_of_day": 36000.0,
        },
        motion=_motion_azimuth_sweep(azimuth_deg, p, beam_width_deg),
        delay_ms=delay_ms,
    )


def _step_034_north_marker(step_id: str = "north-marker", delay_ms: int = 0) -> ScenarioStep:
    return _step(
        step_id,
        "North marker (Cat 034)",
        34,
        {
            "message_type": 1,
            "data_source": {"sac": RADAR_SAC, "sic": RADAR_SIC},
            "azimuth": 0.0,
        },
        delay_ms=delay_ms,
        repeat=2,
    )


def _step_034_sector(azimuth: float, step_id: str = "sector-cross", delay_ms: int = 500) -> ScenarioStep:
    return _step(
        step_id,
        f"Sector crossing {azimuth:.0f}° (Cat 034)",
        34,
        {
            "message_type": 2,
            "data_source": {"sac": RADAR_SAC, "sic": RADAR_SIC},
            "azimuth": azimuth,
        },
        delay_ms=delay_ms,
    )


def _step_062_track(
    name: str,
    track_number: int,
    mode3a: int,
    flight_level: float,
    start: tuple[float, float],
    end: tuple[float, float],
    p: TemplateParams,
    step_id: str,
    delay_ms: int = 0,
) -> ScenarioStep:
    return _step(
        step_id,
        name,
        62,
        {
            "data_source": {"sac": SDPS_SAC, "sic": SDPS_SIC},
            "service_id": 1,
            "time_of_track": 36000.0,
            "position_type": 2,
            "wgs84": {"latitude_deg": start[0], "longitude_deg": start[1]},
            "velocity": {"vx_mps": 0.0, "vy_mps": 0.0},
            "mode3a": {"code": mode3a, "validated": 1, "garbled": 0, "changed": 0},
            "track_number": track_number,
            "track_status": {
                "monosensor": 0,
                "spi": 0,
                "mrh_geometric": 1,
                "src": 1,
                "tentative": 0,
            },
            "flight_level": flight_level,
            "geometric_altitude_ft": flight_level * 100.0,
            "include_velocity": 1,
            "include_geometric_altitude": 1,
        },
        motion=_motion_wgs(start[0], start[1], end[0], end[1], p),
        delay_ms=delay_ms,
    )


def _step_048_plot(
    name: str,
    start: tuple[float, float],
    end: tuple[float, float],
    p: TemplateParams,
    step_id: str,
    mode3a: int = 0,
    delay_ms: int = 0,
) -> ScenarioStep:
    rho, theta = polar_from_radar(start[0], start[1])
    return _step(
        step_id,
        name,
        48,
        {
            "data_source": {"sac": RADAR_SAC, "sic": RADAR_SIC},
            "position": {"rho_nm": rho, "theta_deg": theta},
            "mode3a": mode3a,
        },
        motion=_motion_polar(start[0], start[1], end[0], end[1], p),
        delay_ms=delay_ms,
    )


def _step_015_incs(
    name: str,
    track_number: int,
    start: tuple[float, float],
    end: tuple[float, float],
    p: TemplateParams,
    step_id: str,
    pair_id: int = 1,
    delay_ms: int = 0,
) -> ScenarioStep:
    dist0 = distance_m(*STOCKHOLM_RADAR, start[0], start[1])
    az = bearing_deg(*STOCKHOLM_RADAR, end[0], end[1])
    return _step(
        step_id,
        name,
        15,
        {
            "data_source": {"sac": INCS_SAC, "sic": INCS_SIC},
            "message_type": 2,
            "report_generation": 0,
            "service_id": 1,
            "time_of_applicability": 36000.0,
            "track_plot_number": track_number,
            "measurement_id": {"pair_id": pair_id, "observation_number": 1},
            "position_type": 2,
            "range_azimuth": {"range_m": dist0, "azimuth_deg": az},
        },
        motion=_motion_range_azimuth(start[0], start[1], end[0], end[1], p),
        delay_ms=delay_ms,
    )


def _step_021_adsb(
    name: str,
    start: tuple[float, float],
    end: tuple[float, float],
    p: TemplateParams,
    step_id: str,
    *,
    target_address: str,
    callsign: str,
    mode3a: int = 0,
    flight_level: float = 350.0,
    atp: int = 0,
    include_mode3a: int = 1,
    include_target_identification: int = 1,
    delay_ms: int = 0,
) -> ScenarioStep:
    return _step(
        step_id,
        name,
        21,
        {
            "data_source": {"sac": ADSB_SAC, "sic": ADSB_SIC},
            "target_report_descriptor": {
                "atp": atp,
                "arc": 0,
                "rc": 0,
                "rab": 0,
                "include_extension1": 1,
                "dcr": 0,
                "gbs": 0,
                "sim": 0,
                "tst": 0,
            },
            "time_of_applicability_position": 36000.0,
            "position_resolution": "high",
            "wgs84": {"latitude_deg": start[0], "longitude_deg": start[1]},
            "target_address": target_address,
            "include_mode3a": include_mode3a,
            "mode3a": mode3a,
            "include_flight_level": 1,
            "flight_level": flight_level,
            "include_geometric_height": 1,
            "geometric_height_ft": flight_level * 100.0,
            "include_target_identification": include_target_identification,
            "target_identification": callsign,
        },
        motion=_motion_wgs(start[0], start[1], end[0], end[1], p),
        delay_ms=delay_ms,
    )


def _build_jas_bromma_visby(p: TemplateParams) -> Scenario:
    heading = bearing_deg(*BROMMA, *VISBY)
    steps = [
        _step_016_config(p, "jas-016"),
        _step_065_sdps_status("jas-065", delay_ms=100),
        _step_034_north_marker("jas-034-nm", delay_ms=200),
        _step_240_video_summary("jas-240-sum", "BALTIC-JAS-RADAR-VR", delay_ms=100),
        _step_034_sector(heading, "jas-034-sector", delay_ms=300),
        _step_240_video_radial("jas-240-vid", heading, p, delay_ms=200),
        _step_062_track(
            "JAS 39 system track (Cat 062)",
            p.jas_track_number,
            p.jas_mode3a,
            p.jas_flight_level,
            BROMMA,
            VISBY,
            p,
            "jas-062",
            delay_ms=500,
        ),
        _step_048_plot(
            "JAS 39 monoradar plot (Cat 048)",
            BROMMA,
            VISBY,
            p,
            "jas-048",
            mode3a=p.jas_mode3a,
            delay_ms=200,
        ),
        _step_015_incs(
            "JAS 39 INCS measurement track (Cat 015)",
            p.jas_track_number,
            BROMMA,
            VISBY,
            p,
            "jas-015",
            delay_ms=200,
        ),
        _step_021_adsb(
            "JAS 39 ADS-B report (Cat 021)",
            BROMMA,
            VISBY,
            p,
            "jas-021",
            target_address="4AC872",
            callsign="SVF101  ",
            mode3a=p.jas_mode3a,
            flight_level=p.jas_flight_level,
            delay_ms=200,
        ),
    ]
    return Scenario(
        id="jas-bromma-visby",
        name="JAS 39 – Bromma → Visby",
        description="Friendly Gripen – full ASTERIX category coverage (015/016/021/034/048/062/065/240).",
        transport=_transport(p),
        loop_count=p.loop_count,
        interval_ms=5000,
        steps=steps,
    )


def _build_mig_kaliningrad_visby(p: TemplateParams) -> Scenario:
    heading = bearing_deg(*KALININGRAD, *VISBY)
    steps = [
        _step_016_config(p, "mig-016"),
        _step_065_sdps_status(
            "mig-065",
            message_type=3,
            service_status_report=1,
            sdps_nogo=1,
            delay_ms=100,
        ),
        _step_034_north_marker("mig-034-nm", delay_ms=200),
        _step_240_video_summary("mig-240-sum", "BALTIC-MIG-RADAR-VR", delay_ms=100),
        _step_034_sector(heading, "mig-034-sector", delay_ms=300),
        _step_240_video_radial("mig-240-vid", heading, p, video_sequence=2, delay_ms=200),
        _step_062_track(
            "Hostile MiG system track (Cat 062)",
            p.mig_track_number,
            p.mig_mode3a,
            p.mig_flight_level,
            KALININGRAD,
            VISBY,
            p,
            "mig-062",
            delay_ms=500,
        ),
        _step_048_plot(
            "Hostile MiG monoradar plot (Cat 048)",
            KALININGRAD,
            VISBY,
            p,
            "mig-048",
            mode3a=p.mig_mode3a,
            delay_ms=200,
        ),
        _step_015_incs(
            "Hostile MiG INCS plot (Cat 015)",
            p.mig_track_number,
            KALININGRAD,
            VISBY,
            p,
            "mig-015",
            pair_id=2,
            delay_ms=200,
        ),
        _step_021_adsb(
            "Hostile MiG ADS-B (anonymous, Cat 021)",
            KALININGRAD,
            VISBY,
            p,
            "mig-021",
            target_address="000001",
            callsign="",
            atp=3,
            include_mode3a=0,
            include_target_identification=0,
            flight_level=p.mig_flight_level,
            delay_ms=200,
        ),
    ]
    return Scenario(
        id="mig-kaliningrad-visby",
        name="Hostile MiG – Kaliningrad → Visby",
        description="Non-cooperative hostile track – all ASTERIX categories (015/016/021/034/048/062/065/240).",
        transport=_transport(p),
        loop_count=p.loop_count,
        interval_ms=5000,
        steps=steps,
    )


def _build_baltic_combined(p: TemplateParams) -> Scenario:
    jas_h = bearing_deg(*BROMMA, *VISBY)
    mig_h = bearing_deg(*KALININGRAD, *VISBY)
    steps = [
        _step_016_config(p, "bal-016"),
        _step_065_sdps_status("bal-065", delay_ms=50),
        _step_034_north_marker("bal-034-nm", delay_ms=0),
        _step_240_video_summary("bal-240-sum", "BALTIC-COMBINED-RADAR-VR", delay_ms=50),
        _step_034_sector(jas_h, "bal-034-jas-sector", delay_ms=400),
        _step_240_video_radial("bal-jas-240-vid", jas_h, p, delay_ms=100),
        _step_062_track(
            "JAS 39 SDPS track (Cat 062)",
            p.jas_track_number,
            p.jas_mode3a,
            p.jas_flight_level,
            BROMMA,
            VISBY,
            p,
            "bal-jas-062",
            delay_ms=300,
        ),
        _step_048_plot("JAS plot (Cat 048)", BROMMA, VISBY, p, "bal-jas-048", p.jas_mode3a, delay_ms=100),
        _step_015_incs(
            "JAS INCS (Cat 015)", p.jas_track_number, BROMMA, VISBY, p, "bal-jas-015", delay_ms=100
        ),
        _step_021_adsb(
            "JAS ADS-B (Cat 021)",
            BROMMA,
            VISBY,
            p,
            "bal-jas-021",
            target_address="4AC872",
            callsign="SVF101  ",
            mode3a=p.jas_mode3a,
            flight_level=p.jas_flight_level,
            delay_ms=100,
        ),
        _step_034_sector(mig_h, "bal-034-mig-sector", delay_ms=400),
        _step_240_video_radial("bal-mig-240-vid", mig_h, p, video_sequence=2, delay_ms=100),
        _step_062_track(
            "Hostile MiG SDPS track (Cat 062)",
            p.mig_track_number,
            p.mig_mode3a,
            p.mig_flight_level,
            KALININGRAD,
            VISBY,
            p,
            "bal-mig-062",
            delay_ms=300,
        ),
        _step_048_plot(
            "MiG plot (Cat 048)", KALININGRAD, VISBY, p, "bal-mig-048", p.mig_mode3a, delay_ms=100
        ),
        _step_015_incs(
            "MiG INCS (Cat 015)",
            p.mig_track_number,
            KALININGRAD,
            VISBY,
            p,
            "bal-mig-015",
            pair_id=2,
            delay_ms=100,
        ),
        _step_021_adsb(
            "MiG ADS-B anonymous (Cat 021)",
            KALININGRAD,
            VISBY,
            p,
            "bal-mig-021",
            target_address="000001",
            callsign="",
            atp=3,
            include_mode3a=0,
            include_target_identification=0,
            flight_level=p.mig_flight_level,
            delay_ms=100,
        ),
    ]
    return Scenario(
        id="baltic-combined",
        name="Baltic exercise – JAS + MiG",
        description=(
            "Combined air picture: JAS from Bromma and hostile MiG from Kaliningrad, "
            "all categories 015/016/021/034/048/062/065/240."
        ),
        transport=_transport(p),
        loop_count=p.loop_count,
        interval_ms=10000,
        steps=steps,
    )
