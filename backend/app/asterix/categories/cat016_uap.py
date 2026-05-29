"""Cat 016 Edition 1.0 UAP — Part 30 INCS configuration."""

from app.asterix.uap import UapEntry

CAT016_UAP: tuple[UapEntry, ...] = (
    UapEntry(1, "010", "Data Source Identifier", "2", "data_source"),
    UapEntry(2, "015", "Service Identification", "1", "service_id"),
    UapEntry(3, "000", "Message Type", "1", "message_type"),
    UapEntry(4, "140", "Time Of Day", "3", "time_of_day"),
    UapEntry(5, "200", "Configuration Reporting Period", "1", "reporting_period_s"),
    UapEntry(6, "300", "Pair Identification", "7", "pair"),
    UapEntry(7, "400", "System Reference Point (WGS-84)", "8", "reference_point"),
    UapEntry(8, "405", "Height of Reference Point", "2", "reference_point"),
    UapEntry(9, "410", "Transmitter Properties", "1+"),
    UapEntry(10, "420", "Receiver Properties", "1+"),
    UapEntry(11, "430", "System Configuration", "1+"),
    UapEntry(12, "RE", "Reserved Expansion Field", "1+"),
    UapEntry(13, "SP", "Special Purpose Field", "1+"),
)
