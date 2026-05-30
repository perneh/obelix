"""Link 16 J3.x track messages."""

from __future__ import annotations

from app.link16.messages._factory import make_j_message_class
from app.link16.messages.fields_common import (
    altitude_field,
    course_speed_fields,
    identity_field,
    mode3a_field,
    npg_field,
    platform_air_field,
    platform_surface_field,
    position_field,
    source_ju_field,
    track_number_field,
)

J30 = make_j_message_class(
    j_series="J3.0",
    name="Reference Point",
    description="Reference point track for C2 geometry.",
    npg=2,
    fields=[
        source_ju_field(),
        npg_field(2),
        track_number_field(1),
        identity_field(4),
        position_field(lat=59.0, lon=18.0),
        altitude_field(0),
    ],
)

J31 = make_j_message_class(
    j_series="J3.1",
    name="Emergency Point",
    description="Emergency point track.",
    npg=2,
    fields=[
        source_ju_field(),
        npg_field(2),
        track_number_field(2),
        identity_field(1),
        position_field(lat=59.1, lon=18.1),
        altitude_field(10000),
    ],
)

J32 = make_j_message_class(
    j_series="J3.2",
    name="Air Track",
    description="Air track report for the tactical picture.",
    npg=2,
    fields=[
        source_ju_field(),
        npg_field(2),
        track_number_field(101),
        identity_field(3),
        platform_air_field(1),
        mode3a_field(7777),
        position_field(lat=59.33, lon=18.05),
        altitude_field(35000),
        *course_speed_fields(course=90, speed=450),
    ],
)

J33 = make_j_message_class(
    j_series="J3.3",
    name="Surface Track",
    description="Surface track report.",
    npg=2,
    fields=[
        source_ju_field(),
        npg_field(2),
        track_number_field(201),
        identity_field(3),
        platform_surface_field(1),
        position_field(lat=57.7, lon=11.9),
        *course_speed_fields(course=180, speed=18),
    ],
)

J34 = make_j_message_class(
    j_series="J3.4",
    name="Subsurface Track",
    description="Subsurface track report.",
    npg=2,
    fields=[
        source_ju_field(),
        npg_field(2),
        track_number_field(301),
        identity_field(1),
        position_field(lat=56.0, lon=12.0),
        altitude_field(-200),
        *course_speed_fields(course=45, speed=12),
    ],
)

J35 = make_j_message_class(
    j_series="J3.5",
    name="Land Point Track",
    description="Land point / point track.",
    npg=2,
    fields=[
        source_ju_field(),
        npg_field(2),
        track_number_field(401),
        identity_field(4),
        position_field(lat=59.33, lon=18.05),
        altitude_field(150),
    ],
)

J36 = make_j_message_class(
    j_series="J3.6",
    name="Space Track",
    description="Space track report.",
    npg=2,
    fields=[
        source_ju_field(),
        npg_field(2),
        track_number_field(501),
        identity_field(3),
        position_field(lat=0.0, lon=0.0),
        altitude_field(400000),
        *course_speed_fields(course=0, speed=17000),
    ],
)

J3_MESSAGES = [J30, J31, J32, J33, J34, J35, J36]
