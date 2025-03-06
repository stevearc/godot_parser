""" The grammar of low-level values in the GD file format """

from pyparsing import (
    DelimitedList,
    Forward,
    Group,
    Keyword,
    Literal,
    Opt,
    Optional,
    QuotedString,
    Suppress,
    Word,
    alphanums,
    alphas,
    common,
)

from .objects import GDObject
from .sections import GDTypedArray

boolean = (
    (Keyword("true") | Keyword("false"))
    .set_name("bool")
    .set_parse_action(lambda x: x[0].lower() == "true")
)

null = Keyword("null").set_parse_action(lambda _: [None])


primitive = (
    null | QuotedString('"', escChar="\\", multiline=True) | boolean | common.number
)
value = Forward()

# Vector2( 1, 2 )
# May not have args: PackedStringArray()
obj_type = (
    Word(alphas, alphanums).set_results_name("object_name")
    + Suppress("(")
    + Opt(DelimitedList(value))
    + Suppress(")")
).set_parse_action(GDObject.from_parser)

# [ 1, 2 ] or [ 1, 2, ]
list_ = (
    Group(
        Suppress("[") + Opt(DelimitedList(value)) + Opt(Suppress(",")) + Suppress("]")
    )
    .set_name("list")
)
key_val = Group(QuotedString('"', escChar="\\") + Suppress(":") + value)

# {
# "_edit_use_anchors_": false
# }
dict_ = (
    (Suppress("{") + Opt(DelimitedList(key_val)) + Suppress("}"))
    .set_name("dict")
    .set_parse_action(lambda d: {k: v for k, v in d})
)

# Typed arrays: e.g. Array[PackedInt32Array]([PackedInt32Array(0, 1, 2, 3, 4, 5)])
# Need to support, e.g.:
# polygons = Array[PackedInt32Array]([PackedInt32Array(0, 1, 2, 3), PackedInt32Array(3, 2, 4, 5)])
typed_array = (
    Literal("Array").suppress() +
    Suppress("[") +
    Word(alphanums + "_").set_results_name("inner_type") +
    Suppress("]") +
    Suppress("(") +
    list_.set_results_name("inner_value") +
    Suppress(")")
).set_name("typed_array").set_parse_action(GDTypedArray.from_parser)

# Exports

value <<= primitive | list_ | dict_ | obj_type | typed_array
