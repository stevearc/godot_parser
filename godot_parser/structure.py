"""The grammar of the larger structures in the GD file format"""

from pyparsing import (
    DelimitedList,
    Empty,
    Group,
    LineEnd,
    Opt,
    QuotedString,
    Suppress,
    Word,
    alphanums,
)

from .sections import GDSection, GDSectionHeader
from .values import value

key = QuotedString('"', escChar="\\", multiline=False).set_name("key") | Word(
    alphanums + "_/:"
).set_name("key")
var = Word(alphanums + "_").set_name("variable")
attribute = Group(var + Suppress("=") + value)

# [node name="Node2D"]
section_header = (
    (
        Suppress("[")
        + var.set_results_name("section_type")
        + Opt(DelimitedList(attribute, Empty()))
        + Suppress("]")
        + Suppress(LineEnd())
    )
    .set_name("section_header")
    .set_parse_action(GDSectionHeader.from_parser)
)

# texture = ExtResource( 1 )
section_entry = Group(key + Suppress("=") + value + Suppress(LineEnd())).set_name(
    "section_entry"
)
section_contents = DelimitedList(section_entry, Empty()).set_name("section_contents")

# [node name="Sprite" type="Sprite"]
# texture = ExtResource( 1 )
section = (
    (section_header + Opt(section_contents))
    .set_name("section")
    .set_parse_action(GDSection.from_parser)
)

# Exports

scene_file = DelimitedList(section, Empty())
