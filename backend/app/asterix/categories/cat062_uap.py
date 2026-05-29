"""Cat 062 Edition 1.21 default User Application Profile (FRN 1–35)."""

from app.asterix.uap import UapEntry

# Eurocontrol Part 9 Cat 062 ed. 1.21 — Table 1 System Track Data UAP
CAT062_UAP: tuple[UapEntry, ...] = (
    UapEntry(1, "010", "Data Source Identifier", "2", "data_source", mandatory=True),
    UapEntry(2, None, "Spare", "-", spare=True),
    UapEntry(3, "015", "Service Identification", "1", "service_id"),
    UapEntry(4, "070", "Time Of Track Information", "3", "time_of_track", mandatory=True),
    UapEntry(5, "105", "Calculated Track Position (WGS-84)", "8", "wgs84", related_field_ids=("position_type",)),
    UapEntry(6, "100", "Calculated Track Position (Cartesian)", "6", "cartesian", related_field_ids=("position_type",)),
    UapEntry(7, "185", "Calculated Track Velocity (Cartesian)", "4", "velocity", related_field_ids=("include_velocity",)),
    UapEntry(8, "210", "Calculated Acceleration (Cartesian)", "2", "acceleration"),
    UapEntry(9, "060", "Track Mode 3/A Code", "2", "mode3a"),
    UapEntry(10, "245", "Target Identification", "7", "target_identification"),
    UapEntry(11, "380", "Aircraft Derived Data", "1+", "aircraft_derived_data"),
    UapEntry(12, "040", "Track Number", "2", "track_number", mandatory=True),
    UapEntry(13, "080", "Track Status", "1+", "track_status", mandatory=True),
    UapEntry(14, "290", "System Track Update Ages", "1+", "system_track_update_ages"),
    UapEntry(15, "200", "Mode of Movement", "1", "mode_of_movement"),
    UapEntry(16, "295", "Track Data Ages", "1+", "track_data_ages"),
    UapEntry(17, "136", "Measured Flight Level", "2", "flight_level"),
    UapEntry(18, "130", "Calculated Track Geometric Altitude", "2", "geometric_altitude_ft", related_field_ids=("include_geometric_altitude",)),
    UapEntry(19, "135", "Calculated Track Barometric Altitude", "2", "barometric_altitude"),
    UapEntry(20, "220", "Calculated Rate Of Climb/Descent", "2", "rate_of_climb"),
    UapEntry(21, "390", "Flight Plan Related Data", "1+", "flight_plan_data"),
    UapEntry(22, "270", "Target Size & Orientation", "1+", "target_size"),
    UapEntry(23, "300", "Vehicle Fleet Identification", "1", "vehicle_fleet_id"),
    UapEntry(24, "110", "Mode 5 Data reports & Extended Mode 1 Code", "1+", "mode5_data"),
    UapEntry(25, "120", "Track Mode 2 Code", "2", "mode2_code"),
    UapEntry(26, "510", "Composed Track Number", "3+", "composed_track_number"),
    UapEntry(27, "500", "Estimated Accuracies", "1+", "estimated_accuracies"),
    UapEntry(28, "340", "Measured Information", "1+", "measured_information"),
    UapEntry(29, None, "Spare", "-", spare=True),
    UapEntry(30, None, "Spare", "-", spare=True),
    UapEntry(31, None, "Spare", "-", spare=True),
    UapEntry(32, None, "Spare", "-", spare=True),
    UapEntry(33, None, "Spare", "-", spare=True),
    UapEntry(34, "RE", "Reserved Expansion Field", "1+", "reserved_expansion"),
    UapEntry(35, "SP", "Special Purpose Field", "1+", "special_purpose"),
)

CAT062_UAP_BY_FRN = {entry.frn: entry for entry in CAT062_UAP}
