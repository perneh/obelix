"""Cat 048 Edition 1.32 UAP — Obelix encoder FRN mapping + full-spec placeholders."""

from app.asterix.uap import UapEntry

CAT048_UAP: tuple[UapEntry, ...] = (
    UapEntry(1, "010", "Data Source Identifier", "2", "data_source"),
    UapEntry(2, "040", "Measured Position (RHO/THETA)", "4", "position"),
    UapEntry(3, "070", "Mode 3/A Code", "4", "mode3a"),
    UapEntry(4, "020", "Target Report Descriptor", "1+"),
    UapEntry(5, "140", "Time of Day", "3"),
    UapEntry(6, "161", "Track/Plot Number", "2"),
    UapEntry(7, "170", "Track Status", "1+"),
    UapEntry(8, "210", "Calculated Track Velocity", "4"),
    UapEntry(9, "030", "Warning/Error Conditions", "1+"),
    UapEntry(10, "080", "Mode 3/A Code Confidence", "1+"),
    UapEntry(11, "100", "Mode C Code / Flight Level", "2+"),
    UapEntry(12, "110", "Height Measured by 3D Radar", "2"),
    UapEntry(13, "120", "Radial Doppler Speed", "1+"),
    UapEntry(14, "230", "Communications/ACAS Capability", "1+"),
    UapEntry(15, "260", "ACAS Resolution Advisory", "1+"),
    UapEntry(16, "055", "Mode 1 Code", "2"),
    UapEntry(17, "050", "Mode 2 Code", "2"),
    UapEntry(18, "065", "Mode 1 Code Confidence", "1+"),
    UapEntry(19, "060", "Mode 2 Code Confidence", "1+"),
    UapEntry(20, "042", "Calculated Position", "4"),
    UapEntry(21, "200", "Track Status", "1+"),
    UapEntry(22, "220", "Aircraft Address", "3"),
    UapEntry(23, "240", "Aircraft Identification", "7"),
    UapEntry(24, "250", "Mode S MB Data", "1+"),
    UapEntry(25, "RE", "Reserved Expansion Field", "1+"),
    UapEntry(26, "SP", "Special Purpose Field", "1+"),
)
