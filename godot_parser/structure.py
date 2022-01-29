""" The grammar of the larger structures in the GD file format """

from pyparsing import (
    Empty,
    Group,
    LineEnd,
    Optional,
    QuotedString,
    Suppress,
    Word,
    alphanums,
    delimited_list,
)

from .sections import GDSection, GDSectionHeader
from .values import value

key = QuotedString('"', escChar="\\", multiline=False).setName("key") | Word(
    alphanums + "_/"
).setName("key")
var = Word(alphanums + "_").setName("variable")
attribute = Group(var + Suppress("=") + value)

# [node name="Node2D"]
section_header = (
    (
        Suppress("[")
        + var.setResultsName("section_type")
        + Optional(delimited_list(attribute, Empty()))
        + Suppress("]")
        + Suppress(LineEnd())
    )
    .setName("section_header")
    .setParseAction(GDSectionHeader.from_parser)
)

# texture = ExtResource( 1 )
section_entry = Group(key + Suppress("=") + value + Suppress(LineEnd())).setName(
    "section_entry"
)
section_contents = delimited_list(section_entry, Empty()).setName("section_contents")

# [node name="Sprite" type="Sprite"]
# texture = ExtResource( 1 )
section = (
    (section_header + Optional(section_contents))
    .setName("section")
    .setParseAction(GDSection.from_parser)
)

# Exports

scene_file = delimited_list(section, Empty())
