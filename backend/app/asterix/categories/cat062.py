"""ASTERIX Category 062 – System Track Data (Eurocontrol Part 9, Edition 1.21)."""

from __future__ import annotations

from typing import Any

from app.asterix.base import (
    AsterixCategory,
    CategoryDefinition,
    FieldDefinition,
    FieldType,
    build_fspec,
)
from app.asterix.categories.cat062_encoders import (
    encode_acceleration,
    encode_barometric_altitude,
    encode_cartesian,
    encode_composed_track_number,
    encode_data_source,
    encode_flight_level,
    encode_geometric_altitude,
    encode_mode2,
    encode_mode3a,
    encode_mode_of_movement,
    encode_optional_compound,
    encode_rate_of_climb,
    encode_target_identification,
    encode_time_of_track,
    encode_track_number,
    encode_track_status,
    encode_vehicle_fleet_id,
    encode_velocity,
    encode_wgs84,
    include_section,
    resolve_position_type,
)
from app.asterix.categories.cat062_uap import CAT062_UAP
from app.asterix.uap import uap_to_dicts

_POSITION_TYPES = [
    {"value": 0, "label": "No position"},
    {"value": 1, "label": "Cartesian (FRN 6 · I062/100)"},
    {"value": 2, "label": "WGS-84 (FRN 5 · I062/105)"},
]

_SRC_OPTIONS = [
    {"value": 0, "label": "000 — No source"},
    {"value": 1, "label": "001 — GNSS"},
    {"value": 2, "label": "010 — 3D radar"},
    {"value": 3, "label": "011 — Triangulation"},
    {"value": 4, "label": "100 — Height from coverage"},
    {"value": 5, "label": "101 — Speed look-up table"},
    {"value": 6, "label": "110 — Default height"},
    {"value": 7, "label": "111 — Multilateration"},
]

_MOVEMENT_OPTIONS = [
    {"value": 0, "label": "Constant / Level / No discrepancy"},
    {"value": 1, "label": "Right / Increasing / Climb / Discrepancy"},
    {"value": 2, "label": "Left / Decreasing / Descent"},
    {"value": 3, "label": "Undetermined"},
]

_STI_OPTIONS = [
    {"value": 0, "label": "00 — Callsign or registration downlinked"},
    {"value": 1, "label": "01 — Callsign not downlinked"},
    {"value": 2, "label": "10 — Registration not downlinked"},
    {"value": 3, "label": "11 — Invalid"},
]

_VFI_OPTIONS = [
    {"value": 0, "label": "0 — Unknown"},
    {"value": 1, "label": "1 — ATC equipment maintenance"},
    {"value": 9, "label": "9 — Bus"},
    {"value": 10, "label": "10 — Tug"},
    {"value": 15, "label": "15 — Aircraft maintenance"},
    {"value": 16, "label": "16 — Follow-me"},
]

_YES_NO = [
    {"value": 1, "label": "Yes — set FRN in FSPEC"},
    {"value": 0, "label": "No"},
]


def _frn_label(frn: int, item_id: str, name: str) -> str:
    return f"FRN {frn} · I062/{item_id} {name}" if item_id else name


def _include_toggle() -> FieldDefinition:
    return FieldDefinition(
        id="include",
        label="Include in FSPEC",
        field_type=FieldType.ENUM,
        default=0,
        options=_YES_NO,
    )


def _raw_hex_field() -> FieldDefinition:
    return FieldDefinition(
        id="raw_hex",
        label="Raw payload hex (optional override)",
        field_type=FieldType.STRING,
        default="",
        description="Leave empty for minimal valid encoding (FX=0). Advanced: paste full item bytes.",
    )


def _optional_compound(frn: int, item_id: str, field_id: str, name: str) -> FieldDefinition:
    return FieldDefinition(
        id=field_id,
        label=_frn_label(frn, item_id, name),
        field_type=FieldType.COMPOUND,
        default={"include": 0, "raw_hex": ""},
        description="Variable-length item — enable Include, or supply raw hex from an external editor.",
        uap_frn=frn,
        item_id=item_id,
        include_flag=True,
        fields=[_include_toggle(), _raw_hex_field()],
    )


class Cat062(AsterixCategory):
    """SDPS system track messages per Eurocontrol Cat 062 default UAP (FRN 1–35)."""

    @classmethod
    def definition(cls) -> CategoryDefinition:
        fields = [
            FieldDefinition(
                id="data_source",
                label=_frn_label(1, "010", "Data Source Identifier"),
                field_type=FieldType.COMPOUND,
                default={"sac": 1, "sic": 1},
                description="Mandatory",
                uap_frn=1,
                item_id="010",
                fields=[
                    FieldDefinition(id="sac", label="SAC", field_type=FieldType.UINT8, default=1),
                    FieldDefinition(id="sic", label="SIC", field_type=FieldType.UINT8, default=1),
                ],
            ),
            FieldDefinition(
                id="service_id",
                label=_frn_label(3, "015", "Service Identification"),
                field_type=FieldType.UINT8,
                default=0,
                description="Optional — set > 0 to include FRN 3",
                min_value=0,
                max_value=255,
                uap_frn=3,
                item_id="015",
            ),
            FieldDefinition(
                id="time_of_track",
                label=_frn_label(4, "070", "Time Of Track Information"),
                field_type=FieldType.FLOAT,
                default=44100.0,
                description="Mandatory — seconds since midnight UTC (LSB = 1/128 s)",
                min_value=0.0,
                max_value=86400.0,
                unit="s",
                uap_frn=4,
                item_id="070",
            ),
            FieldDefinition(
                id="position_type",
                label="Position item selection",
                field_type=FieldType.ENUM,
                default=2,
                description="Select FRN 5 (WGS-84) or FRN 6 (Cartesian), or neither",
                options=_POSITION_TYPES,
            ),
            FieldDefinition(
                id="wgs84",
                label=_frn_label(5, "105", "Calculated Position (WGS-84)"),
                field_type=FieldType.COMPOUND,
                default={"latitude_deg": 59.3293, "longitude_deg": 18.0686},
                uap_frn=5,
                item_id="105",
                fields=[
                    FieldDefinition(id="latitude_deg", label="Latitude", field_type=FieldType.FLOAT, default=59.3293, unit="°"),
                    FieldDefinition(id="longitude_deg", label="Longitude", field_type=FieldType.FLOAT, default=18.0686, unit="°"),
                ],
            ),
            FieldDefinition(
                id="cartesian",
                label=_frn_label(6, "100", "Calculated Track Position (Cartesian)"),
                field_type=FieldType.COMPOUND,
                default={"x_m": 1000.0, "y_m": 2000.0},
                uap_frn=6,
                item_id="100",
                fields=[
                    FieldDefinition(id="x_m", label="X", field_type=FieldType.FLOAT, default=1000.0, unit="m"),
                    FieldDefinition(id="y_m", label="Y", field_type=FieldType.FLOAT, default=2000.0, unit="m"),
                ],
            ),
            FieldDefinition(
                id="include_velocity",
                label="FRN 7 · Include velocity (I062/185)",
                field_type=FieldType.ENUM,
                default=1,
                options=_YES_NO,
            ),
            FieldDefinition(
                id="velocity",
                label=_frn_label(7, "185", "Calculated Track Velocity (Cartesian)"),
                field_type=FieldType.COMPOUND,
                default={"vx_mps": 50.0, "vy_mps": 10.0},
                uap_frn=7,
                item_id="185",
                fields=[
                    FieldDefinition(id="vx_mps", label="Vx", field_type=FieldType.FLOAT, default=50.0, unit="m/s"),
                    FieldDefinition(id="vy_mps", label="Vy", field_type=FieldType.FLOAT, default=10.0, unit="m/s"),
                ],
            ),
            FieldDefinition(
                id="acceleration",
                label=_frn_label(8, "210", "Calculated Acceleration (Cartesian)"),
                field_type=FieldType.COMPOUND,
                default={"include": 0, "ax_mps2": 0.0, "ay_mps2": 0.0},
                uap_frn=8,
                item_id="210",
                include_flag=True,
                fields=[
                    _include_toggle(),
                    FieldDefinition(id="ax_mps2", label="Ax", field_type=FieldType.FLOAT, default=0.0, unit="m/s²"),
                    FieldDefinition(id="ay_mps2", label="Ay", field_type=FieldType.FLOAT, default=0.0, unit="m/s²"),
                ],
            ),
            FieldDefinition(
                id="mode3a",
                label=_frn_label(9, "060", "Track Mode 3/A Code"),
                field_type=FieldType.COMPOUND,
                default={"code": 7000, "validated": 1, "garbled": 0, "changed": 0},
                description="Set code to 0 to omit FRN 9",
                uap_frn=9,
                item_id="060",
                fields=[
                    FieldDefinition(id="code", label="Mode 3/A (octal)", field_type=FieldType.UINT16, default=7000, max_value=7777),
                    FieldDefinition(
                        id="validated",
                        label="Validated",
                        field_type=FieldType.ENUM,
                        default=1,
                        options=[{"value": 1, "label": "Validated"}, {"value": 0, "label": "Not validated"}],
                    ),
                    FieldDefinition(
                        id="garbled",
                        label="Garbled",
                        field_type=FieldType.ENUM,
                        default=0,
                        options=[{"value": 0, "label": "Normal"}, {"value": 1, "label": "Garbled"}],
                    ),
                    FieldDefinition(
                        id="changed",
                        label="Changed",
                        field_type=FieldType.ENUM,
                        default=0,
                        options=[{"value": 0, "label": "No change"}, {"value": 1, "label": "Changed"}],
                    ),
                ],
            ),
            FieldDefinition(
                id="target_identification",
                label=_frn_label(10, "245", "Target Identification"),
                field_type=FieldType.COMPOUND,
                default={"include": 0, "sti": 0, "callsign": "SVF123"},
                uap_frn=10,
                item_id="245",
                include_flag=True,
                fields=[
                    _include_toggle(),
                    FieldDefinition(id="sti", label="STI", field_type=FieldType.ENUM, default=0, options=_STI_OPTIONS),
                    FieldDefinition(id="callsign", label="Callsign (8 chars)", field_type=FieldType.STRING, default="SVF123"),
                ],
            ),
            _optional_compound(11, "380", "aircraft_derived_data", "Aircraft Derived Data"),
            FieldDefinition(
                id="track_number",
                label=_frn_label(12, "040", "Track Number"),
                field_type=FieldType.UINT16,
                default=1,
                description="Mandatory",
                uap_frn=12,
                item_id="040",
            ),
            FieldDefinition(
                id="track_status",
                label=_frn_label(13, "080", "Track Status"),
                field_type=FieldType.COMPOUND,
                default={"monosensor": 0, "spi": 0, "mrh_geometric": 1, "src": 0, "tentative": 0},
                description="Mandatory — first extent (FX=0). Extended status via raw hex in future.",
                uap_frn=13,
                item_id="080",
                fields=[
                    FieldDefinition(id="monosensor", label="MON", field_type=FieldType.ENUM, default=0, options=[{"value": 0, "label": "Multisensor"}, {"value": 1, "label": "Monosensor"}]),
                    FieldDefinition(id="spi", label="SPI", field_type=FieldType.ENUM, default=0, options=_YES_NO[:2]),
                    FieldDefinition(id="mrh_geometric", label="MRH", field_type=FieldType.ENUM, default=1, options=[{"value": 0, "label": "Barometric"}, {"value": 1, "label": "Geometric"}]),
                    FieldDefinition(id="src", label="SRC", field_type=FieldType.ENUM, default=0, options=_SRC_OPTIONS),
                    FieldDefinition(id="tentative", label="CNF", field_type=FieldType.ENUM, default=0, options=[{"value": 0, "label": "Confirmed"}, {"value": 1, "label": "Tentative"}]),
                ],
            ),
            _optional_compound(14, "290", "system_track_update_ages", "System Track Update Ages"),
            FieldDefinition(
                id="mode_of_movement",
                label=_frn_label(15, "200", "Mode of Movement"),
                field_type=FieldType.COMPOUND,
                default={"include": 0, "transversal": 0, "longitudinal": 0, "vertical": 0, "altitude_discrepancy": 0},
                uap_frn=15,
                item_id="200",
                include_flag=True,
                fields=[
                    _include_toggle(),
                    FieldDefinition(id="transversal", label="TRANS (turn)", field_type=FieldType.ENUM, default=0, options=_MOVEMENT_OPTIONS),
                    FieldDefinition(id="longitudinal", label="LONG (speed)", field_type=FieldType.ENUM, default=0, options=_MOVEMENT_OPTIONS),
                    FieldDefinition(id="vertical", label="VERT (climb)", field_type=FieldType.ENUM, default=0, options=_MOVEMENT_OPTIONS),
                    FieldDefinition(id="altitude_discrepancy", label="ADF", field_type=FieldType.ENUM, default=0, options=_YES_NO[:2]),
                ],
            ),
            _optional_compound(16, "295", "track_data_ages", "Track Data Ages"),
            FieldDefinition(
                id="flight_level",
                label=_frn_label(17, "136", "Measured Flight Level"),
                field_type=FieldType.FLOAT,
                default=0.0,
                description="Set 0 to omit FRN 17",
                unit="FL",
                uap_frn=17,
                item_id="136",
            ),
            FieldDefinition(
                id="include_geometric_altitude",
                label="FRN 18 · Include geometric altitude (I062/130)",
                field_type=FieldType.ENUM,
                default=1,
                options=_YES_NO,
            ),
            FieldDefinition(
                id="geometric_altitude_ft",
                label=_frn_label(18, "130", "Calculated Track Geometric Altitude"),
                field_type=FieldType.FLOAT,
                default=35000.0,
                unit="ft",
                uap_frn=18,
                item_id="130",
            ),
            FieldDefinition(
                id="barometric_altitude",
                label=_frn_label(19, "135", "Calculated Track Barometric Altitude"),
                field_type=FieldType.COMPOUND,
                default={"include": 0, "qnh_applied": 0, "flight_level": 350.0},
                uap_frn=19,
                item_id="135",
                include_flag=True,
                fields=[
                    _include_toggle(),
                    FieldDefinition(id="qnh_applied", label="QNH correction applied", field_type=FieldType.ENUM, default=0, options=_YES_NO[:2]),
                    FieldDefinition(id="flight_level", label="Barometric FL", field_type=FieldType.FLOAT, default=350.0, unit="FL"),
                ],
            ),
            FieldDefinition(
                id="rate_of_climb",
                label=_frn_label(20, "220", "Calculated Rate Of Climb/Descent"),
                field_type=FieldType.COMPOUND,
                default={"include": 0, "fpm": 0.0},
                uap_frn=20,
                item_id="220",
                include_flag=True,
                fields=[
                    _include_toggle(),
                    FieldDefinition(id="fpm", label="Rate", field_type=FieldType.FLOAT, default=0.0, unit="ft/min"),
                ],
            ),
            _optional_compound(21, "390", "flight_plan_data", "Flight Plan Related Data"),
            _optional_compound(22, "270", "target_size", "Target Size & Orientation"),
            FieldDefinition(
                id="vehicle_fleet_id",
                label=_frn_label(23, "300", "Vehicle Fleet Identification"),
                field_type=FieldType.COMPOUND,
                default={"include": 0, "fleet_id": 0},
                uap_frn=23,
                item_id="300",
                include_flag=True,
                fields=[
                    _include_toggle(),
                    FieldDefinition(id="fleet_id", label="VFI", field_type=FieldType.ENUM, default=0, options=_VFI_OPTIONS),
                ],
            ),
            _optional_compound(24, "110", "mode5_data", "Mode 5 Data reports & Extended Mode 1 Code"),
            FieldDefinition(
                id="mode2_code",
                label=_frn_label(25, "120", "Track Mode 2 Code"),
                field_type=FieldType.COMPOUND,
                default={"include": 0, "code": 0},
                uap_frn=25,
                item_id="120",
                include_flag=True,
                fields=[
                    _include_toggle(),
                    FieldDefinition(id="code", label="Mode 2 (octal)", field_type=FieldType.UINT16, default=0, max_value=7777),
                ],
            ),
            FieldDefinition(
                id="composed_track_number",
                label=_frn_label(26, "510", "Composed Track Number"),
                field_type=FieldType.COMPOUND,
                default={"include": 0, "system_unit_id": 1, "system_track_number": 1},
                uap_frn=26,
                item_id="510",
                include_flag=True,
                fields=[
                    _include_toggle(),
                    FieldDefinition(id="system_unit_id", label="System unit ID", field_type=FieldType.UINT8, default=1),
                    FieldDefinition(id="system_track_number", label="System track number", field_type=FieldType.UINT16, default=1),
                ],
            ),
            _optional_compound(27, "500", "estimated_accuracies", "Estimated Accuracies"),
            _optional_compound(28, "340", "measured_information", "Measured Information"),
            FieldDefinition(
                id="reserved_expansion",
                label=_frn_label(34, "RE", "Reserved Expansion Field"),
                field_type=FieldType.COMPOUND,
                default={"include": 0, "raw_hex": ""},
                uap_frn=34,
                item_id="RE",
                include_flag=True,
                fields=[_include_toggle(), _raw_hex_field()],
            ),
            FieldDefinition(
                id="special_purpose",
                label=_frn_label(35, "SP", "Special Purpose Field"),
                field_type=FieldType.COMPOUND,
                default={"include": 0, "raw_hex": ""},
                uap_frn=35,
                item_id="SP",
                include_flag=True,
                fields=[_include_toggle(), _raw_hex_field()],
            ),
        ]

        return CategoryDefinition(
            category=62,
            name="System Track Data",
            edition="1.21",
            description=(
                "Processed SDPS system track (Cat 062 ed. 1.21). All UAP positions FRN 1–35 are "
                "listed below; editable fields map to FRN/data items. FRN 2 and 29–33 are spare."
            ),
            fields=fields,
            uap=uap_to_dicts(CAT062_UAP),
        )

    @classmethod
    def encode_record(cls, field_values: dict[str, Any]) -> bytes:
        items_by_frn: dict[int, bytes] = {}

        items_by_frn[1] = encode_data_source(field_values.get("data_source", {}))
        items_by_frn[4] = encode_time_of_track(float(field_values.get("time_of_track", 0.0)))
        items_by_frn[12] = encode_track_number(int(field_values.get("track_number", 1)))
        items_by_frn[13] = encode_track_status(field_values.get("track_status", {}))

        service_id = int(field_values.get("service_id", 0))
        if service_id > 0:
            items_by_frn[3] = bytes([service_id & 0xFF])

        position_type = resolve_position_type(field_values.get("position_type", 2))
        if position_type == "cartesian":
            items_by_frn[6] = encode_cartesian(field_values.get("cartesian", {}))
        elif position_type == "wgs84":
            items_by_frn[5] = encode_wgs84(field_values.get("wgs84", {}))

        if int(field_values.get("include_velocity", 1)):
            items_by_frn[7] = encode_velocity(field_values.get("velocity", {}))

        if include_section(field_values, "acceleration"):
            items_by_frn[8] = encode_acceleration(field_values.get("acceleration", {}))

        mode3a = field_values.get("mode3a", {})
        if int(mode3a.get("code", 0)) > 0:
            items_by_frn[9] = encode_mode3a(mode3a)

        if include_section(field_values, "target_identification"):
            items_by_frn[10] = encode_target_identification(field_values.get("target_identification", {}))

        for frn, key in (
            (11, "aircraft_derived_data"),
            (14, "system_track_update_ages"),
            (16, "track_data_ages"),
            (21, "flight_plan_data"),
            (22, "target_size"),
            (24, "mode5_data"),
            (27, "estimated_accuracies"),
            (28, "measured_information"),
            (34, "reserved_expansion"),
            (35, "special_purpose"),
        ):
            payload = encode_optional_compound(field_values, key)
            if payload is not None:
                items_by_frn[frn] = payload

        if include_section(field_values, "mode_of_movement"):
            items_by_frn[15] = encode_mode_of_movement(field_values.get("mode_of_movement", {}))

        flight_level = float(field_values.get("flight_level", 0.0))
        if flight_level != 0.0:
            items_by_frn[17] = encode_flight_level(flight_level)

        if int(field_values.get("include_geometric_altitude", 1)):
            items_by_frn[18] = encode_geometric_altitude(float(field_values.get("geometric_altitude_ft", 0.0)))

        if include_section(field_values, "barometric_altitude"):
            items_by_frn[19] = encode_barometric_altitude(field_values.get("barometric_altitude", {}))

        if include_section(field_values, "rate_of_climb"):
            items_by_frn[20] = encode_rate_of_climb(float(field_values.get("rate_of_climb", {}).get("fpm", 0.0)))

        if include_section(field_values, "vehicle_fleet_id"):
            items_by_frn[23] = encode_vehicle_fleet_id(
                int(field_values.get("vehicle_fleet_id", {}).get("fleet_id", 0))
            )

        if include_section(field_values, "mode2_code"):
            items_by_frn[25] = encode_mode2(field_values.get("mode2_code", {}))

        if include_section(field_values, "composed_track_number"):
            items_by_frn[26] = encode_composed_track_number(field_values.get("composed_track_number", {}))

        present_frns = sorted(items_by_frn)
        return build_fspec(present_frns) + b"".join(items_by_frn[frn] for frn in present_frns)
