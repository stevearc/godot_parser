import os
import unittest

from godot_parser import GDScene

HERE = os.path.dirname(__file__)

TEST_CASES = [
    (GDScene(), "[gd_scene load_steps=1 format=2]",),
    (
        GDScene().add_ext_resource("res://Other.tscn", "PackedScene"),
        """[gd_scene load_steps=2 format=2]

[ext_resource path="res://Other.tscn" type="PackedScene" id=1]""",
    ),
]


class TestCreator(unittest.TestCase):

    """ Test the Godot file creation API """

    def test_cases(self):
        """ Run the parsing test cases """
        for obj, expected in TEST_CASES:
            print("Running test")
            self.assertEqual(str(obj), expected)
