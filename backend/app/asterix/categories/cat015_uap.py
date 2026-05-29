"""Cat 015 Edition 1.1 UAP — Part 28 INCS target reports."""

from app.asterix.uap import UapEntry

CAT015_UAP: tuple[UapEntry, ...] = (
    UapEntry(1, "010", "Data Source Identifier", "2", "data_source"),
    UapEntry(2, "000", "Message Type / Report Generation", "1", "message_type", related_field_ids=("report_generation",)),
    UapEntry(3, "015", "Service Identification", "1", "service_id"),
    UapEntry(4, "020", "Target Descriptor", "1+"),
    UapEntry(5, "030", "Track Status", "1+"),
    UapEntry(6, "145", "Time Of Applicability", "3", "time_of_applicability"),
    UapEntry(7, "161", "Track/Plot Number", "2", "track_plot_number"),
    UapEntry(8, "042", "Track Quality", "1+"),
    UapEntry(9, "050", "Velocity", "1+"),
    UapEntry(10, "060", "Contour Identifier", "1+"),
    UapEntry(11, "070", "Doppler Speed", "1+"),
    UapEntry(12, "400", "Measurement Identifier", "5", "measurement_id"),
    UapEntry(13, "600", "Horizontal Position (WGS-84)", "8", "wgs84", related_field_ids=("position_type",)),
    UapEntry(14, "610", "Position Accuracy", "1+"),
    UapEntry(15, "620", "Velocity Accuracy", "1+"),
    UapEntry(16, "630", "Acceleration", "1+"),
    UapEntry(17, "640", "Mode 3/A Code", "2"),
    UapEntry(18, "650", "Flight Level", "2"),
    UapEntry(19, "660", "Target Address", "3"),
    UapEntry(20, "625", "Range", "3", "range_azimuth"),
    UapEntry(21, "626", "Range Accuracy", "1+"),
    UapEntry(22, "627", "Azimuth", "2", "range_azimuth"),
    UapEntry(23, "628", "Azimuth Accuracy", "1+"),
    UapEntry(24, "RE", "Reserved Expansion Field", "1+"),
    UapEntry(25, "SP", "Special Purpose Field", "1+"),
)
