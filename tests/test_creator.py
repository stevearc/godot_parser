import unittest

from godot_parser import GDScene, Node


class TestCreator(unittest.TestCase):

    """ Test the Godot file creation API """

    def test_basic_scene(self):
        """ Run the parsing test cases """
        self.assertEqual(str(GDScene()).strip(), "[gd_scene load_steps=1 format=2]")

    def test_ext_resource(self):
        """ Test serializing a scene with an ext_resource """
        scene = GDScene()
        scene.add_ext_resource("res://Other.tscn", "PackedScene")
        self.assertEqual(
            str(scene),
            """[gd_scene load_steps=2 format=2]

[ext_resource path="res://Other.tscn" type="PackedScene" id=1]
""",
        )

    def test_node(self):
        """ Test serializing a scene with a node """
        scene = GDScene()
        scene.add_node("RootNode", type="Node2D")
        scene.add_node("Child", type="Area2D", parent=".")
        self.assertEqual(
            str(scene),
            """[gd_scene load_steps=1 format=2]

[node name="RootNode" type="Node2D"]

[node name="Child" type="Area2D" parent="."]
""",
        )

    def test_tree_create(self):
        """ Test creating a scene with the tree API """
        scene = GDScene()
        with scene.use_tree() as tree:
            tree.root = Node("RootNode", type="Node2D")
            tree.root.add_child(
                Node("Child", type="Area2D", properties={"visible": False})
            )
        self.assertEqual(
            str(scene),
            """[gd_scene load_steps=1 format=2]

[node name="RootNode" type="Node2D"]

[node name="Child" type="Area2D" parent="."]
visible = false
""",
        )

    def test_tree_deep_create(self):
        """ Test creating a scene with nested children using the tree API """
        scene = GDScene()
        with scene.use_tree() as tree:
            tree.root = Node("RootNode", type="Node2D")
            child = Node("Child", type="Node")
            tree.root.add_child(child)
            child.add_child(Node("ChildChild", type="Node"))
            child.add_child(Node("ChildChild2", type="Node"))
        self.assertEqual(
            str(scene),
            """[gd_scene load_steps=1 format=2]

[node name="RootNode" type="Node2D"]

[node name="Child" type="Node" parent="."]

[node name="ChildChild" type="Node" parent="Child"]

[node name="ChildChild2" type="Node" parent="Child"]
""",
        )
