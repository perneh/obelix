"""Cat 240 Edition 1.3 UAP — Radar Video Transmission."""

from app.asterix.uap import UapEntry

CAT240_UAP: tuple[UapEntry, ...] = (
    UapEntry(1, "010", "Data Source Identifier", "2", "data_source", mandatory=True),
    UapEntry(2, "000", "Message Type", "1", "message_type"),
    UapEntry(3, "020", "Video Record Header", "4", "video_sequence"),
    UapEntry(4, "030", "Video Summary", "1+", "video_summary"),
    UapEntry(5, "040", "Video Header Nano", "12", "video_header", related_field_ids=("header_format",)),
    UapEntry(6, "041", "Video Header Femto", "12", "video_header", related_field_ids=("header_format",)),
    UapEntry(7, "048", "Video Cells Resolution & Compression", "2", "video_resolution"),
    UapEntry(8, "049", "Video Octets & Video Cells Counters", "5", "video_counters"),
    UapEntry(9, "050", "Video Block Low Data Volume", "1+4×N", "video_block", related_field_ids=("video_block_format",)),
    UapEntry(10, "051", "Video Block Medium Data Volume", "1+64×N", "video_block", related_field_ids=("video_block_format",)),
    UapEntry(11, "052", "Video Block High Data Volume", "1+256×N", "video_block", related_field_ids=("video_block_format",)),
    UapEntry(12, "140", "Time of Day", "3", "time_of_day", related_field_ids=("include_time_of_day",)),
    UapEntry(13, "RE", "Reserved Expansion Field", "1+", "reserved_expansion"),
    UapEntry(14, "SP", "Special Purpose Field", "1+", "special_purpose"),
)
