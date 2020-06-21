import unittest

from godot_parser import GDScene, Node


class TestTree(unittest.TestCase):

    """ Test the the high-level tree API """

    def test_get_node(self):
        """ Test for get_node() """
        scene = GDScene()
        scene.add_node("RootNode")
        scene.add_node("Child", parent=".")
        child = scene.add_node("Child2", parent="Child")
        node = scene.get_node("Child/Child2")
        self.assertEqual(node, child)

    def test_remove_node(self):
        """ Test for remove_node() """
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

    def test_empty_scene(self):
        """ Empty scenes should not crash """
        scene = GDScene()
        with scene.use_tree() as tree:
            pass

    def test_get_missing_node(self):
        """ get_node on missing node should return None """
        scene = GDScene()
        scene.add_node("RootNode")
        node = scene.get_node("Foo/Bar/Baz")
        self.assertIsNone(node)

    def test_properties(self):
        """ Test for changing properties on a node """
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
        """ Test __magic__ methods on Node """
        n = Node("Player")
        self.assertEqual(str(n), "Node(Player)")
        self.assertEqual(repr(n), "Node(Player)")
