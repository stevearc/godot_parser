import unittest

from godot_parser import (
    GDExtResourceSection,
    GDNodeSection,
    GDSection,
    GDSectionHeader,
    GDSubResourceSection,
)


class TestGDSections(unittest.TestCase):

    """Tests for GD file sections"""

    def test_header_dunder(self):
        """Tests for __magic__ methods on GDSectionHeader"""
        h = GDSectionHeader("node")
        self.assertEqual(str(h), "[node]")
        self.assertEqual(repr(h), "GDSectionHeader([node])")
        h2 = GDSectionHeader("node")
        self.assertEqual(h, h2)
        h2["type"] = "Node2D"
        self.assertNotEqual(h, h2)
        self.assertNotEqual(h, "[node]")

    def test_section_dunder(self):
        """Tests for __magic__ methods on GDSection"""
        h = GDSectionHeader("node")
        s = GDSection(h, vframes=10)
        self.assertEqual(str(s), "[node]\nvframes = 10")
        self.assertEqual(repr(s), "GDSection([node]\nvframes = 10)")
        self.assertEqual(s["vframes"], 10)

        s2 = GDSection(GDSectionHeader("node"), vframes=10)
        self.assertEqual(s, s2)
        s2["vframes"] = 100
        self.assertNotEqual(s, s2)
        self.assertNotEqual(s, "[node]\nvframes = 10")

        del s["vframes"]
        self.assertEqual(s.get("vframes"), None)
        del s["vframes"]

    def test_ext_resource(self):
        """Test for GDExtResourceSection"""
        s = GDExtResourceSection("res://Other.tscn", type="PackedScene", id=1)
        self.assertEqual(s.path, "res://Other.tscn")
        self.assertEqual(s.type, "PackedScene")
        self.assertEqual(s.id, 1)
        s.path = "res://New.tscn"
        self.assertEqual(s.path, "res://New.tscn")
        s.type = "Texture"
        self.assertEqual(s.type, "Texture")
        s.id = 2
        self.assertEqual(s.id, 2)

    def test_sub_resource(self):
        """Test for GDSubResourceSection"""
        s = GDSubResourceSection(type="CircleShape2D", id=1)
        self.assertEqual(s.type, "CircleShape2D")
        self.assertEqual(s.id, 1)
        s.type = "Animation"
        self.assertEqual(s.type, "Animation")
        s.id = 2
        self.assertEqual(s.id, 2)

    def test_node(self):
        """Test for GDNodeSection"""
        s = GDNodeSection("Sprite", type="Sprite", groups=["foo", "bar"])
        self.assertIsNone(s.instance)
        self.assertIsNone(s.index)
        self.assertEqual(s.type, "Sprite")
        self.assertEqual(s.groups, ["foo", "bar"])

        # Setting the instance removes the type
        s.instance = 1
        self.assertEqual(s.instance, 1)
        self.assertEqual(s.type, None)

        # Setting the type removes the instance
        s.type = "Sprite"
        self.assertEqual(s.type, "Sprite")
        self.assertIsNone(s.instance)

        s.index = 3
        self.assertEqual(s.index, 3)
        s.index = None
        self.assertEqual(s.index, None)

        # Setting groups
        s.groups = ["baz"]
        self.assertEqual(s.groups, ["baz"])
