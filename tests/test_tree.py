import os
import shutil
import tempfile
import unittest

from godot_parser import GDScene, Node, SubResource, TreeMutationException
from godot_parser.util import find_project_root, gdpath_to_filepath


class TestTree(unittest.TestCase):

    """Test the the high-level tree API"""

    def test_get_node(self):
        """Test for get_node()"""
        scene = GDScene()
        scene.add_node("RootNode")
        scene.add_node("Child", parent=".")
        child = scene.add_node("Child2", parent="Child")
        node = scene.get_node("Child/Child2")
        self.assertEqual(node, child)

    def test_remove_node(self):
        """Test for remove_node()"""
        scene = GDScene()
        scene.add_node("RootNode")
        scene.add_node("Child", parent=".")
        node = scene.find_section("node", name="Child")
        self.assertIsNotNone(node)

        # Remove by name
        with scene.use_tree() as tree:
            tree.root.remove_child("Child")
        node = scene.find_section("node", name="Child")
        self.assertIsNone(node)

        # Remove by index
        scene.add_node("Child", parent=".")
        with scene.use_tree() as tree:
            tree.root.remove_child(0)
        node = scene.find_section("node", name="Child")
        self.assertIsNone(node)

        # Remove by reference
        scene.add_node("Child", parent=".")
        with scene.use_tree() as tree:
            node = tree.root.get_children()[0]
            tree.root.remove_child(node)
        node = scene.find_section("node", name="Child")
        self.assertIsNone(node)

        # Remove child
        scene.add_node("Child", parent=".")
        with scene.use_tree() as tree:
            node = tree.root.get_child(0)
            node.remove_from_parent()
        node = scene.find_section("node", name="Child")
        self.assertIsNone(node)

    def test_insert_child(self):
        """Test for insert_child()"""
        scene = GDScene()
        scene.add_node("RootNode")
        scene.add_node("Child1", parent=".")
        with scene.use_tree() as tree:
            child = Node("Child2", type="Node")
            tree.root.insert_child(0, child)
        child1 = scene.find_section("node", name="Child1")
        child2 = scene.find_section("node", name="Child2")
        idx1 = scene.get_sections().index(child1)
        idx2 = scene.get_sections().index(child2)
        print(scene.get_sections())
        self.assertLess(idx2, idx1)

    def test_empty_scene(self):
        """Empty scenes should not crash"""
        scene = GDScene()
        with scene.use_tree() as tree:
            n = tree.get_node("Any")
            self.assertIsNone(n)

    def test_get_missing_node(self):
        """get_node on missing node should return None"""
        scene = GDScene()
        scene.add_node("RootNode")
        node = scene.get_node("Foo/Bar/Baz")
        self.assertIsNone(node)

    def test_properties(self):
        """Test for changing properties on a node"""
        scene = GDScene()
        scene.add_node("RootNode")
        with scene.use_tree() as tree:
            tree.root["vframes"] = 10
            self.assertEqual(tree.root["vframes"], 10)
            tree.root["hframes"] = 10
            del tree.root["hframes"]
            del tree.root["hframes"]
            self.assertIsNone(tree.root.get("hframes"))
        child = scene.find_section("node")
        self.assertEqual(child["vframes"], 10)

    def test_dunder(self):
        """Test __magic__ methods on Node"""
        n = Node("Player")
        self.assertEqual(str(n), "Node(Player)")
        self.assertEqual(repr(n), "Node(Player)")


class TestInheritedScenes(unittest.TestCase):

    """Test the the high-level tree API for inherited scenes"""

    project_dir = None
    root_scene = None
    mid_scene = None
    leaf_scene = None

    @classmethod
    def setUpClass(cls):
        super(TestInheritedScenes, cls).setUpClass()
        cls.project_dir = tempfile.mkdtemp()
        with open(os.path.join(cls.project_dir, "project.godot"), "w") as ofile:
            ofile.write("fake project")
        cls.root_scene = os.path.join(cls.project_dir, "Root.tscn")
        cls.mid_scene = os.path.join(cls.project_dir, "Mid.tscn")
        cls.leaf_scene = os.path.join(cls.project_dir, "Leaf.tscn")
        scene = GDScene.parse(
            """
[gd_scene load_steps=1 format=2]
[node name="Root" type="KinematicBody2D"]
collision_layer = 3
[node name="CollisionShape2D" type="CollisionShape2D" parent="."]
disabled = true
[node name="Sprite" type="Sprite" parent="."]
flip_h = false
[node name="Health" type="Control" parent="."]
[node name="LifeBar" type="TextureProgress" parent="Health"]
"""
        )
        scene.write(cls.root_scene)

        scene = GDScene.parse(
            """
[gd_scene load_steps=2 format=2]
[ext_resource path="res://Root.tscn" type="PackedScene" id=1]
[node name="Mid" instance=ExtResource( 1 )]
collision_layer = 4
[node name="Health" parent="." index="2"]
pause_mode = 2
"""
        )
        scene.write(cls.mid_scene)

        scene = GDScene.parse(
            """
[gd_scene load_steps=2 format=2]
[ext_resource path="res://Mid.tscn" type="PackedScene" id=1]
[sub_resource type="CircleShape2D" id=1]
[node name="Leaf" instance=ExtResource( 1 )]
shape = SubResource( 1 )
[node name="Sprite" type="Sprite" parent="." index="1"]
flip_h = true
"""
        )
        scene.write(cls.leaf_scene)

    @classmethod
    def tearDownClass(cls):
        super(TestInheritedScenes, cls).tearDownClass()
        if os.path.isdir(cls.project_dir):
            shutil.rmtree(cls.project_dir)

    def test_load_inherited(self):
        """Can load an inherited scene and read the nodes"""
        scene = GDScene.load(self.leaf_scene)
        with scene.use_tree() as tree:
            node = tree.get_node("Health/LifeBar")
            self.assertIsNotNone(node)
            self.assertEqual(node.type, "TextureProgress")

    def test_add_new_nodes(self):
        """Can add new nodes to an inherited scene"""
        scene = GDScene.load(self.leaf_scene)
        with scene.use_tree() as tree:
            tree.get_node("Health/LifeBar")
            node = Node("NewChild", type="Control")
            tree.root.add_child(node)
            # Non-inherited node can change name, type, instance
            node.instance = 2
            node.type = "Node2D"
            node.name = "NewChild2"
        found = scene.find_section("node", name="NewChild2")
        self.assertIsNotNone(found)
        self.assertEqual(found.type, "Node2D")
        self.assertEqual(found.parent, ".")
        self.assertEqual(found.index, 3)

    def test_cannot_remove(self):
        """Cannot remove inherited nodes"""
        scene = GDScene.load(self.leaf_scene)
        with scene.use_tree() as tree:
            node = tree.get_node("Health")
            self.assertRaises(TreeMutationException, node.remove_from_parent)
            self.assertRaises(TreeMutationException, lambda: tree.root.remove_child(0))
            self.assertRaises(
                TreeMutationException, lambda: tree.root.remove_child("Health")
            )

    def test_cannot_mutate(self):
        """Cannot change the name/type/instance of inherited nodes"""
        scene = GDScene.load(self.leaf_scene)

        def change_name(x):
            x.name = "foo"

        def change_type(x):
            x.type = "foo"

        def change_instance(x):
            x.instance = 2

        with scene.use_tree() as tree:
            node = tree.get_node("Health")
            self.assertRaises(TreeMutationException, lambda: change_name(node))
            self.assertRaises(TreeMutationException, lambda: change_type(node))
            self.assertRaises(TreeMutationException, lambda: change_instance(node))

    def test_inherit_properties(self):
        """Inherited nodes inherit properties"""
        scene = GDScene.load(self.leaf_scene)
        with scene.use_tree() as tree:
            self.assertEqual(tree.root["shape"], SubResource(1))
            self.assertEqual(tree.root["collision_layer"], 4)
            self.assertEqual(tree.root.get("collision_layer"), 4)
            self.assertEqual(tree.root.get("missing"), None)
            self.assertRaises(KeyError, lambda: tree.root["missing"])

    def test_unchanged_sections(self):
        """Inherited nodes do not appear in sections"""
        scene = GDScene.load(self.leaf_scene)
        num_nodes = len(scene.get_nodes())
        self.assertEqual(num_nodes, 2)
        with scene.use_tree() as tree:
            sprite = tree.get_node("Sprite")
            sprite["flip_v"] = True
        # No new nodes
        num_nodes = len(scene.get_nodes())
        self.assertEqual(num_nodes, 2)

    def test_overwrite_sections(self):
        """Inherited nodes appear in sections if we change their configuration"""
        scene = GDScene.load(self.leaf_scene)
        with scene.use_tree() as tree:
            node = tree.get_node("Health/LifeBar")
            node["pause_mode"] = 2
        num_nodes = len(scene.get_nodes())
        self.assertEqual(num_nodes, 3)
        node = scene.find_section("node", name="LifeBar", parent="Health")
        self.assertIsNotNone(node)

    def test_disappear_sections(self):
        """Inherited nodes are removed from sections if we change their configuration to match parent"""
        scene = GDScene.load(self.leaf_scene)
        with scene.use_tree() as tree:
            sprite = tree.get_node("Sprite")
            sprite["flip_h"] = False
        # Sprite should match parent now, and not be in file
        node = scene.find_section("node", name="Sprite")
        self.assertIsNone(node)

    def test_find_project_root(self):
        """Can find project root even if deep in folder"""
        os.mkdir(os.path.join(self.project_dir, "Dir1"))
        nested = os.path.join(self.project_dir, "Dir1", "Dir2")
        os.mkdir(nested)
        root = find_project_root(nested)
        self.assertEqual(root, self.project_dir)

    def test_invalid_tree(self):
        """Raise exception when tree is invalid"""
        scene = GDScene()
        scene.add_node("RootNode")
        scene.add_node("Child", parent="Missing")
        self.assertRaises(TreeMutationException, lambda: scene.get_node("Child"))

    def test_missing_root(self):
        """Raise exception when GDScene is inherited but missing project_root"""
        scene = GDScene()
        scene.add_ext_node("Root", 1)
        self.assertRaises(RuntimeError, lambda: scene.get_node("Root"))

    def test_missing_ext_resource(self):
        """Raise exception when GDScene is inherited but ext_resource is missing"""
        scene = GDScene.load(self.leaf_scene)
        for section in scene.get_ext_resources():
            scene.remove_section(section)
        self.assertRaises(RuntimeError, lambda: scene.get_node("Root"))


class TestUtil(unittest.TestCase):

    """Tests for util"""

    def test_bad_gdpath(self):
        """Raise exception on bad gdpath"""
        self.assertRaises(ValueError, lambda: gdpath_to_filepath("/", "foobar"))

    def test_no_project(self):
        """If no Godot project is found, return None"""
        root = find_project_root(tempfile.gettempdir())
        self.assertIsNone(root)
