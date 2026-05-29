"""Cat 065 Edition 1.5 UAP — SDPS Service Status Reports."""

from app.asterix.uap import UapEntry

CAT065_UAP: tuple[UapEntry, ...] = (
    UapEntry(1, "010", "Data Source Identifier", "2", "data_source", mandatory=True),
    UapEntry(2, "000", "Message Type", "1", "message_type"),
    UapEntry(3, "015", "Service Identification", "1", "service_id"),
    UapEntry(4, "030", "Time of Message", "3", "time_of_message"),
    UapEntry(5, "020", "Batch Number", "1", "batch_number", related_field_ids=("include_batch_number",)),
    UapEntry(6, "040", "SDPS Configuration and Status", "1", "sdps_configuration"),
    UapEntry(7, "050", "Service Status Report", "1", "service_status_report"),
    UapEntry(8, None, "Spare", "-", spare=True),
    UapEntry(9, None, "Spare", "-", spare=True),
    UapEntry(10, None, "Spare", "-", spare=True),
    UapEntry(11, None, "Spare", "-", spare=True),
    UapEntry(12, None, "Spare", "-", spare=True),
    UapEntry(13, "RE", "Reserved Expansion Field", "1+", "reserved_expansion"),
    UapEntry(14, "SP", "Special Purpose Field", "1+", "special_purpose"),
)
