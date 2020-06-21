""" The grammar of low-level values in the GD file format """

from pyparsing import (
    Forward,
    Group,
    Keyword,
    Optional,
    QuotedString,
    Suppress,
    Word,
    alphanums,
    alphas,
    delimitedList,
    pyparsing_common,
)

from .objects import GDObject

boolean = (
    (Keyword("true") | Keyword("false"))
    .setName("bool")
    .setParseAction(lambda x: x[0].lower() == "true")
)

null = Keyword("null").setParseAction(lambda _: [None])


primitive = (
    null
    | QuotedString('"', escChar="\\", multiline=True)
    | boolean
    | pyparsing_common.number
)
value = Forward()

# Vector2( 1, 2 )
obj_type = (
    Word(alphas, alphanums).setResultsName("object_name")
    + Suppress("(")
    + delimitedList(value)
    + Suppress(")")
).setParseAction(GDObject.from_parser)

# [ 1, 2 ]
list_ = (
    Group(Suppress("[") + Optional(delimitedList(value)) + Suppress("]"))
    .setName("list")
    .setParseAction(lambda p: p.asList())
)
key_val = Group(QuotedString('"', escChar="\\") + Suppress(":") + value)

# {
# "_edit_use_anchors_": false
# }
dict_ = (
    (Suppress("{") + Optional(delimitedList(key_val)) + Suppress("}"))
    .setName("dict")
    .setParseAction(lambda d: {k: v for k, v in d})
)

# Exports

value <<= primitive | list_ | dict_ | obj_type
