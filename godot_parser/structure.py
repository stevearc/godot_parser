""" The grammar of the larger structures in the GD file format """

from pyparsing import (
    Empty,
    Group,
    Optional,
    Suppress,
    Word,
    alphanums,
    delimitedList,
    lineStart,
)

from .sections import GDSection, GDSectionHeader
from .values import value

key = Word(alphanums + "_/").setName("key")
var = Word(alphanums + "_").setName("variable")
attribute = Group(var + Suppress("=") + value)

# [node name="Node2D"]
section_header = (
    (
        Suppress(lineStart)
        + Suppress("[")
        + var.setResultsName("section_type")
        + Optional(delimitedList(attribute, Empty()))
        + Suppress("]")
    )
    .setName("section_header")
    .setParseAction(GDSectionHeader.from_parser)
)

# texture = ExtResource( 1 )
section_entry = Group(Suppress(lineStart) + key + Suppress("=") + value).setName(
    "section_entry"
)
section_contents = delimitedList(section_entry, Empty()).setName("section_contents")

# [node name="Sprite" type="Sprite"]
# texture = ExtResource( 1 )
section = (
    (section_header + Optional(section_contents))
    .setName("section")
    .setParseAction(GDSection.from_parser)
)

# Exports

scene_file = delimitedList(section, Empty())
