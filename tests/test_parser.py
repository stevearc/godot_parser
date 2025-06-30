import os
import unittest

from pyparsing import ParseException

from godot_parser import StringName, GDFile, GDObject, GDArray, GDSection, GDSubResourceSection, GDSectionHeader, Vector2, parse

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
        """[sub_resource type="Compositor" id="3"]
    compositor_effects = Array[CompositorEffect]([ExtResource("1")])
    """,
        GDFile(
            GDSection(
                GDSectionHeader("sub_resource", type="Compositor", id="3"),
                compositor_effects=GDArray(
                    "CompositorEffect",
                    [GDObject("ExtResource", "1")],
                )
            )
        ),
    ),
    (
        """[sub_resource type="AnimationLibrary" id="1"]
    _data = {
    &"RESET": SubResource("2"),
    &"sprint": SubResource("3"),
    &"walk": SubResource("4")
    }""",
        GDFile(
            GDSection(
                GDSectionHeader("sub_resource", type="AnimationLibrary", id="1"),
                **{
                    "_data": {
                        StringName("RESET"): GDObject("SubResource", "2"),
                        StringName("sprint"): GDObject("SubResource", "3"),
                        StringName("walk"): GDObject("SubResource", "4"),
                    }
                }
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
