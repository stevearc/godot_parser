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

from .objects import GDObject, StringName, TypedArray, TypedDictionary

boolean = (
    (Keyword("true") | Keyword("false"))
    .set_name("bool")
    .set_parse_action(lambda x: x[0].lower() == "true")
)

null = Keyword("null").set_parse_action(lambda _: [None])

_string = QuotedString('"', escChar="\\", multiline=True).set_name("string")

_string_name = (
    (Suppress("&") + _string)
    .set_name("string_name")
    .set_parse_action(StringName.from_parser)
)

primitive = null | _string | _string_name | boolean | common.number
value = Forward()

# Vector2( 1, 2 )
obj_ = (
    Word(alphas, alphanums).set_results_name("object_name")
    + Suppress("(")
    + Opt(DelimitedList(value))
    + Suppress(")")
).set_parse_action(GDObject.from_parser)

obj_type = obj_ | Word(alphas, alphanums)

# [ 1, 2 ] or [ 1, 2, ]
list_ = (
    Group(
        Suppress("[") + Opt(DelimitedList(value)) + Opt(Suppress(",")) + Suppress("]")
    )
    .set_name("list")
    .set_parse_action(lambda p: p.as_list())
)

# Array[StringName]([&"a", &"b", &"c"])
typed_list = (
    Word(alphas, alphanums).set_results_name("object_name")
    + (Suppress("[") + obj_type.set_results_name("type") + Suppress("]"))
    + Suppress("(")
    + list_
    + Suppress(")")
).set_parse_action(TypedArray.from_parser)

key_val = Group(value + Suppress(":") + value)

# {
# "_edit_use_anchors_": false
# }
dict_ = (
    (Suppress("{") + Opt(DelimitedList(key_val)) + Suppress("}"))
    .set_name("dict")
    .set_parse_action(lambda d: {k: v for k, v in d})
)

# Dictionary[StringName,ExtResource("1_qwert")]({
# &"_edit_use_anchors_": ExtResource("2_testt")
# })
typed_dict = (
    Word(alphas, alphanums).set_results_name("object_name")
    + (
        Suppress("[")
        + obj_type.set_results_name("key_type")
        + Suppress(",")
        + obj_type.set_results_name("value_type")
        + Suppress("]")
    )
    + Suppress("(")
    + dict_
    + Suppress(")")
).set_parse_action(TypedDictionary.from_parser)

# Exports

value <<= list_ | typed_list | dict_ | typed_dict | obj_ | primitive
