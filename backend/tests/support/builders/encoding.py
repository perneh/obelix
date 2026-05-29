"""Pure builders for ASTERIX encoding test data."""

from __future__ import annotations

from typing import Any


def build_cat015_range_plot_fields(
    *,
    sac: int = 1,
    sic: int = 2,
    track_number: int = 42,
    range_m: float = 5000.0,
    azimuth_deg: float = 45.0,
) -> dict[str, Any]:
    return {
        "data_source": {"sac": sac, "sic": sic},
        "message_type": 1,
        "report_generation": 0,
        "service_id": 0,
        "time_of_applicability": 128.0,
        "track_plot_number": track_number,
        "position_type": 2,
        "range_azimuth": {"range_m": range_m, "azimuth_deg": azimuth_deg},
        "measurement_id": {"pair_id": 0, "observation_number": 0},
    }


def build_cat016_system_config_fields(
    *,
    sac: int = 1,
    sic: int = 1,
    pair_id: int = 1,
) -> dict[str, Any]:
    return {
        "data_source": {"sac": sac, "sic": sic},
        "service_id": 0,
        "message_type": 1,
        "time_of_day": 128.0,
        "reporting_period_s": 0,
        "pair": {"pair_id": pair_id, "transmitter_id": 10, "receiver_id": 20},
        "reference_point": {
            "latitude_deg": 59.0,
            "longitude_deg": 18.0,
            "height_m": 25.0,
        },
    }


def build_cat034_north_marker_fields(*, sac: int = 1, sic: int = 2) -> dict[str, Any]:
    return {
        "message_type": 1,
        "data_source": {"sac": sac, "sic": sic},
    }


def build_cat034_sector_crossing_fields(
    *,
    sac: int = 3,
    sic: int = 4,
    azimuth: float = 90.0,
) -> dict[str, Any]:
    return {
        "message_type": 2,
        "data_source": {"sac": sac, "sic": sic},
        "azimuth": azimuth,
    }


def build_cat048_plot_fields(
    *,
    sac: int = 1,
    sic: int = 1,
    rho_nm: float = 10.0,
    theta_deg: float = 45.0,
    mode3a: int = 7000,
) -> dict[str, Any]:
    return {
        "data_source": {"sac": sac, "sic": sic},
        "position": {"rho_nm": rho_nm, "theta_deg": theta_deg},
        "mode3a": mode3a,
    }


def build_cat048_registry_fields(
    *,
    sac: int = 2,
    sic: int = 3,
    rho_nm: float = 5.0,
    theta_deg: float = 180.0,
    mode3a: int = 0,
) -> dict[str, Any]:
    return {
        "data_source": {"sac": sac, "sic": sic},
        "position": {"rho_nm": rho_nm, "theta_deg": theta_deg},
        "mode3a": mode3a,
    }


def build_cat021_adsb_fields(
    *,
    sac: int = 3,
    sic: int = 1,
    latitude_deg: float = 59.3293,
    longitude_deg: float = 18.0686,
    target_address: str = "4AC872",
    callsign: str = "SVF101  ",
    mode3a: int = 7777,
    flight_level: float = 350.0,
    atp: int = 0,
    include_mode3a: int = 1,
    include_target_identification: int = 1,
) -> dict[str, Any]:
    return {
        "data_source": {"sac": sac, "sic": sic},
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
        "wgs84": {"latitude_deg": latitude_deg, "longitude_deg": longitude_deg},
        "target_address": target_address,
        "include_mode3a": include_mode3a,
        "mode3a": mode3a,
        "include_flight_level": 1,
        "flight_level": flight_level,
        "include_geometric_height": 1,
        "geometric_height_ft": flight_level * 100.0,
        "include_target_identification": include_target_identification,
        "target_identification": callsign,
    }


def build_cat065_sdps_status_fields(
    *,
    sac: int = 1,
    sic: int = 1,
    message_type: int = 1,
    service_id: int = 1,
    include_sdps_configuration: int = 1,
    include_service_status_report: int = 0,
    service_status_report: int = 15,
    sdps_nogo: int = 0,
) -> dict[str, Any]:
    return {
        "data_source": {"sac": sac, "sic": sic},
        "message_type": message_type,
        "service_id": service_id,
        "time_of_message": 36000.0,
        "include_sdps_configuration": include_sdps_configuration,
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


def build_cat062_minimal_fields(
    *,
    sac: int = 1,
    sic: int = 1,
    track_number: int = 42,
    time_seconds: float = 44100.0,
) -> dict[str, Any]:
    """Mandatory Cat 062 items only: 010, 070, 040, 080."""
    return {
        "data_source": {"sac": sac, "sic": sic},
        "service_id": 0,
        "time_of_track": time_seconds,
        "position_type": 0,
        "track_number": track_number,
        "track_status": {
            "monosensor": 0,
            "spi": 0,
            "mrh_geometric": 1,
            "src": 0,
            "tentative": 0,
        },
        "include_velocity": 0,
        "include_geometric_altitude": 0,
        "mode3a": {"code": 0, "validated": 1, "garbled": 0, "changed": 0},
        "flight_level": 0.0,
    }


def build_cat062_system_track_fields(
    *,
    sac: int = 1,
    sic: int = 2,
    track_number: int = 100,
    latitude_deg: float = 59.3293,
    longitude_deg: float = 18.0686,
) -> dict[str, Any]:
    """Typical system track with WGS-84 position and velocity."""
    fields = build_cat062_minimal_fields(sac=sac, sic=sic, track_number=track_number)
    fields.update(
        {
            "service_id": 1,
            "position_type": 2,
            "wgs84": {"latitude_deg": latitude_deg, "longitude_deg": longitude_deg},
            "velocity": {"vx_mps": 120.0, "vy_mps": -30.0},
            "include_velocity": 1,
            "mode3a": {"code": 7000, "validated": 1, "garbled": 0, "changed": 0},
            "geometric_altitude_ft": 35000.0,
            "include_geometric_altitude": 1,
            "flight_level": 350.0,
        }
    )
    return fields
