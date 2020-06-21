import unittest

from godot_parser import GDScene


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
