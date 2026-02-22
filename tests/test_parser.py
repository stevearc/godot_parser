import os
import unittest

from pyparsing import ParseException

from godot_parser import (
    GDFile,
    GDObject,
    GDSection,
    GDSectionHeader,
    StringName,
    TypedArray,
    TypedDictionary,
    Vector2,
    parse,
)

HERE = os.path.dirname(__file__)

TEST_CASES = [
    (
        "[gd_scene load_steps=5 format=2]",
        GDFile(GDSection(GDSectionHeader("gd_scene", load_steps=5, format=2))),
    ),
    (
        "[gd_resource load_steps=5 format=2]",
        GDFile(GDSection(GDSectionHeader("gd_resource", load_steps=5, format=2))),
    ),
    (
        "[gd_resource format=3]",
        GDFile(GDSection(GDSectionHeader("gd_resource", format=3))),
    ),
    (
        '[ext_resource path="res://Sample.tscn" type="PackedScene" id=1]',
        GDFile(
            GDSection(
                GDSectionHeader(
                    "ext_resource", path="res://Sample.tscn", type="PackedScene", id=1
                )
            )
        ),
    ),
    (
        """[gd_scene load_steps=5 format=2]
    [ext_resource path="res://Sample.tscn" type="PackedScene" id=1]""",
        GDFile(
            GDSection(GDSectionHeader("gd_scene", load_steps=5, format=2)),
            GDSection(
                GDSectionHeader(
                    "ext_resource", path="res://Sample.tscn", type="PackedScene", id=1
                )
            ),
        ),
    ),
    (
        """[sub_resource type="RectangleShape2D" id=1]
        extents = Vector2( 12.7855, 17.0634 )
        other = null
        "with spaces" = 1
            """,
        GDFile(
            GDSection(
                GDSectionHeader("sub_resource", type="RectangleShape2D", id=1),
                extents=Vector2(12.7855, 17.0634),
                other=None,
                **{"with spaces": 1}
            )
        ),
    ),
    (
        """[sub_resource type="Animation" id=2]
    tracks/0/keys = {
    "transitions": PoolRealArray( 1, 1 ),
    "update": 0,
    "values": [ Vector2( 0, 0 ), Vector2( 1, 0 ) ]
    }""",
        GDFile(
            GDSection(
                GDSectionHeader("sub_resource", type="Animation", id=2),
                **{
                    "tracks/0/keys": {
                        "transitions": GDObject("PoolRealArray", 1, 1),
                        "update": 0,
                        "values": [Vector2(0, 0), Vector2(1, 0)],
                    }
                }
            )
        ),
    ),
    (
        """[resource]
    0/name = "Sand"
        """,
        GDFile(GDSection(GDSectionHeader("resource"), **{"0/name": "Sand"})),
    ),
    (
        """[node name="Label" parent="." groups=["foo", "bar"]]
    text = "Hello
    "
    """,
        GDFile(
            GDSection(
                GDSectionHeader(
                    "node", name="Label", parent=".", groups=["foo", "bar"]
                ),
                text="Hello\n    ",
            )
        ),
    ),
    (
        """[sub_resource type="TileSetAtlasSource" id=2]
    0:0/0 = 0
    0:0/0/physics_layer_0/linear_velocity = Vector2(0, 0)
    0:0/0/physics_layer_0/angular_velocity = 0.0
    """,
        GDFile(
            GDSection(
                GDSectionHeader("sub_resource", type="TileSetAtlasSource", id=2),
                **{
                    "0:0/0": 0,
                    "0:0/0/physics_layer_0/linear_velocity": Vector2(0, 0),
                    "0:0/0/physics_layer_0/angular_velocity": 0.0,
                }
            )
        ),
    ),
    (
        """[sub_resource type="CustomType" id=1]
        string_value = "String"
        string_name_value = &"StringName"
        string_quote = "\\"String\\""
        string_name_quote = &"\\"StringName\\""
        string_single_quote = "\'String\'"
        string_name_single_quote = &"\'StringName\'"
        """,
        GDFile(
            GDSection(
                GDSectionHeader("sub_resource", type="CustomType", id=1),
                **{
                    "string_value": "String",
                    "string_name_value": StringName("StringName"),
                    "string_quote": '"String"',
                    "string_name_quote": StringName('"StringName"'),
                    "string_single_quote": "'String'",
                    "string_name_single_quote": StringName("'StringName'"),
                }
            )
        ),
    ),
    (
        """[sub_resource type="CustomType" id=1]
        typed_dict_1 = Dictionary[StringName, ExtResource("1_testt")]({
        &"key": ExtResource("2_testt")
        })
        typed_dict_2 = Dictionary[ExtResource("1_testt"), StringName]({
        ExtResource("2_testt"): &"key"
        })
        """,
        GDFile(
            GDSection(
                GDSectionHeader("sub_resource", type="CustomType", id=1),
                **{
                    "typed_dict_1": TypedDictionary(
                        "StringName",
                        GDObject("ExtResource", "1_testt"),
                        {StringName("key"): GDObject("ExtResource", "2_testt")},
                    ),
                    "typed_dict_2": TypedDictionary(
                        GDObject("ExtResource", "1_testt"),
                        "StringName",
                        {GDObject("ExtResource", "2_testt"): StringName("key")},
                    ),
                }
            )
        ),
    ),
    (
        """[sub_resource type="CustomType" id=1]
        typed_array_1 = Array[StringName]([&"a", &"b", &"c"])
        typed_array_2 = Array[ExtResource("1_typee")]([ExtResource("1_qwert"), ExtResource("2_testt")])
        """,
        GDFile(
            GDSection(
                GDSectionHeader("sub_resource", type="CustomType", id=1),
                **{
                    "typed_array_1": TypedArray(
                        "StringName",
                        [
                            StringName("a"),
                            StringName("b"),
                            StringName("c"),
                        ],
                    ),
                    "typed_array_2": TypedArray(
                        GDObject("ExtResource", "1_typee"),
                        [
                            GDObject("ExtResource", "1_qwert"),
                            GDObject("ExtResource", "2_testt"),
                        ],
                    ),
                }
            )
        ),
    ),
    (
        """[node name="Label" type="Label" parent="." unique_id=1387035530]
        text = "\ta\\\"q\\'é'd\\\"\n\n\\\\"
        """,
        GDFile(
            GDSection(
                GDSectionHeader(
                    "node", name="Label", type="Label", parent=".", unique_id=1387035530
                ),
                **{"text": "\ta\"q'é'd\"\n\n\\"}
            )
        ),
    ),
]


class TestParser(unittest.TestCase):
    """ """

    def _run_test(self, string: str, expected):
        """Run a set of tests"""
        try:
            parse_result = parse(string)
            if expected == "error":
                assert False, "Parsing '%s' should have failed.\nGot: %s" % (
                    string,
                    parse_result,
                )
            else:
                self.assertEqual(parse_result, expected)
        except ParseException as e:
            if expected != "error":
                print(string)
                print(" " * e.loc + "^")
                print(str(e))
                raise
        except AssertionError:
            print("Parsing : %s" % string)
            print("Expected: %r" % expected)
            print("Got     : %r" % parse_result)
            raise

    def test_cases(self):
        """Run the parsing test cases"""
        for string, expected in TEST_CASES:
            self._run_test(string, expected)
