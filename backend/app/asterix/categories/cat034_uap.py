"""Cat 034 Edition 1.29 UAP — Obelix encoder FRN mapping."""

from app.asterix.uap import UapEntry

# Obelix FSPEC order matches FRN 1–3 below. Full spec defines additional items (not encoded).
CAT034_UAP: tuple[UapEntry, ...] = (
    UapEntry(1, "000", "Message Type", "1", "message_type"),
    UapEntry(2, "010", "Data Source Identifier", "2", "data_source"),
    UapEntry(3, "020", "Antenna Azimuth", "2", "azimuth"),
    UapEntry(4, "030", "Time of Day", "3"),
    UapEntry(5, "041", "Antenna Rotation Period", "2"),
    UapEntry(6, "050", "Station Configuration Status", "1+"),
    UapEntry(7, "060", "Station Processing Mode", "1"),
    UapEntry(8, "070", "Plot Count Values", "1+"),
    UapEntry(9, "100", "Dynamic Window Type 1", "1+"),
    UapEntry(10, "110", "Dynamic Window Type 2", "1+"),
    UapEntry(11, "120", "Geographical Filtering", "1+"),
    UapEntry(12, "130", "Jamming Strobe", "1+"),
    UapEntry(13, "RE", "Reserved Expansion Field", "1+"),
    UapEntry(14, "SP", "Special Purpose Field", "1+"),
)
