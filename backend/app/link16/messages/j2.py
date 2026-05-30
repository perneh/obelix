"""Link 16 J2.x PPLI messages."""

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
    strength_field,
)

J20 = make_j_message_class(
    j_series="J2.0",
    name="Initial Entry",
    description="Initial entry of a Link 16 participant into the network.",
    npg=1,
    fields=[
        source_ju_field(10001),
        npg_field(1),
        identity_field(3),
        strength_field(1),
        position_field(lat=59.33, lon=18.05),
        altitude_field(5000),
        *course_speed_fields(course=270, speed=250),
    ],
)

J22 = make_j_message_class(
    j_series="J2.2",
    name="PPLI",
    description="Precise Participant Location and Identification.",
    npg=1,
    fields=[
        source_ju_field(10001),
        npg_field(1),
        identity_field(3),
        strength_field(1),
        position_field(lat=59.33, lon=18.05),
        altitude_field(5000),
        *course_speed_fields(course=270, speed=250),
    ],
)

J23 = make_j_message_class(
    j_series="J2.3",
    name="Air PPLI",
    description="Air platform PPLI with mode 3/A and flight profile.",
    npg=1,
    fields=[
        source_ju_field(10001),
        npg_field(1),
        identity_field(3),
        platform_air_field(1),
        mode3a_field(7777),
        position_field(lat=59.33, lon=18.05),
        altitude_field(35000),
        *course_speed_fields(course=90, speed=450),
    ],
)

J24 = make_j_message_class(
    j_series="J2.4",
    name="Surface PPLI",
    description="Surface platform PPLI.",
    npg=1,
    fields=[
        source_ju_field(10002),
        npg_field(1),
        identity_field(3),
        platform_surface_field(1),
        position_field(lat=57.7, lon=11.9),
        *course_speed_fields(course=180, speed=18),
    ],
)

J25 = make_j_message_class(
    j_series="J2.5",
    name="Land Point PPLI",
    description="Land point / fixed site PPLI.",
    npg=1,
    fields=[
        source_ju_field(10003),
        npg_field(1),
        identity_field(4),
        position_field(lat=59.33, lon=18.05),
        altitude_field(100),
    ],
)

J26 = make_j_message_class(
    j_series="J2.6",
    name="Space PPLI",
    description="Space platform PPLI.",
    npg=1,
    fields=[
        source_ju_field(10004),
        npg_field(1),
        identity_field(3),
        position_field(lat=0.0, lon=0.0),
        altitude_field(400000),
        *course_speed_fields(course=0, speed=17000),
    ],
)

J2_MESSAGES = [J20, J22, J23, J24, J25, J26]
