"""The grammar of low-level values in the GD file format"""

from pyparsing import (
    DelimitedList,
    Forward,
    Group,
    Keyword,
    Opt,
    QuotedString,
    Suppress,
    Word,
    alphanums,
    alphas,
    common,
)

from .objects import GDObject, GDArray, StringName

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
obj_type = (
    Word(alphas, alphanums).set_results_name("object_name")
    + Suppress("(")
    + DelimitedList(value)
    + Suppress(")")
).set_parse_action(GDObject.from_parser)

# [ 1, 2 ] or [ 1, 2, ]
list_ = (
    Group(
        Suppress("[") + Opt(DelimitedList(value)) + Opt(Suppress(",")) + Suppress("]")
    )
    .set_name("list")
    .set_parse_action(lambda p: p.as_list())
)

# Array[SomeType]( [ 1, 2 ] )
typed_array = (
    (
        Suppress(Keyword("Array")) + 
        Suppress("[") + Word(alphas, alphanums).set_results_name("array_type") + Suppress("]") +
        Suppress("(") + list_ + Suppress(")")
    )
    .set_name("typed_list")
    .set_parse_action(GDArray.from_parser)
)

string_name = Suppress("&") + QuotedString('"', escChar="\\").set_parse_action(lambda p: StringName(p[0]))

key = string_name | QuotedString('"', escChar="\\")

key_val = Group(
    key + Suppress(":") + value
)

# {
# "_edit_use_anchors_": false
# }
dict_ = (
    (Suppress("{") + Opt(DelimitedList(key_val)) + Suppress("}"))
    .set_name("dict")
    .set_parse_action(lambda d: {k: v for k, v in d})
)

# Exports

value <<= primitive | list_ | dict_ | typed_array | obj_type
