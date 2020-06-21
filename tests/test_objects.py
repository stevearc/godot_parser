import unittest

from godot_parser import Vector2, Vector3, Color, NodePath, ExtResource, SubResource


class TestGDObjects(unittest.TestCase):

    """ Tests for GD object wrappers """

    def test_vector2(self):
        """ Test for Vector2 """
        v = Vector2(1, 2)
        self.assertEqual(v[0], 1)
        self.assertEqual(v[1], 2)
        self.assertEqual(v.x, 1)
        self.assertEqual(v.y, 2)
        self.assertEqual(str(v), "Vector2( 1, 2 )")
        v.x = 2
        v.y = 3
        self.assertEqual(v.x, 2)
        self.assertEqual(v.y, 3)
        v[0] = 3
        v[1] = 4
        self.assertEqual(v[0], 3)
        self.assertEqual(v[1], 4)

    def test_vector3(self):
        """ Test for Vector3 """
        v = Vector3(1, 2, 3)
        self.assertEqual(v[0], 1)
        self.assertEqual(v[1], 2)
        self.assertEqual(v[2], 3)
        self.assertEqual(v.x, 1)
        self.assertEqual(v.y, 2)
        self.assertEqual(v.z, 3)
        self.assertEqual(str(v), "Vector3( 1, 2, 3 )")
        v.x = 2
        v.y = 3
        v.z = 4
        self.assertEqual(v.x, 2)
        self.assertEqual(v.y, 3)
        self.assertEqual(v.z, 4)
        v[0] = 3
        v[1] = 4
        v[2] = 5
        self.assertEqual(v[0], 3)
        self.assertEqual(v[1], 4)
        self.assertEqual(v[2], 5)

    def test_color(self):
        """ Test for Color """
        c = Color(0.1, 0.2, 0.3, 0.4)
        self.assertEqual(c[0], 0.1)
        self.assertEqual(c[1], 0.2)
        self.assertEqual(c[2], 0.3)
        self.assertEqual(c[3], 0.4)
        self.assertEqual(c.r, 0.1)
        self.assertEqual(c.g, 0.2)
        self.assertEqual(c.b, 0.3)
        self.assertEqual(c.a, 0.4)
        self.assertEqual(str(c), "Color( 0.1, 0.2, 0.3, 0.4 )")
        c.r = 0.2
        c.g = 0.3
        c.b = 0.4
        c.a = 0.5
        self.assertEqual(c.r, 0.2)
        self.assertEqual(c.g, 0.3)
        self.assertEqual(c.b, 0.4)
        self.assertEqual(c.a, 0.5)
        c[0] = 0.3
        c[1] = 0.4
        c[2] = 0.5
        c[3] = 0.6
        self.assertEqual(c[0], 0.3)
        self.assertEqual(c[1], 0.4)
        self.assertEqual(c[2], 0.5)
        self.assertEqual(c[3], 0.6)

    def test_node_path(self):
        """ Test for NodePath """
        n = NodePath("../Sibling")
        self.assertEqual(n.path, "../Sibling")
        n.path = "../Other"
        self.assertEqual(n.path, "../Other")
        self.assertEqual(str(n), 'NodePath("../Other")')

    def test_ext_resource(self):
        """ Test for ExtResource """
        r = ExtResource(1)
        self.assertEqual(r.id, 1)
        r.id = 2
        self.assertEqual(r.id, 2)
        self.assertEqual(str(r), "ExtResource( 2 )")

    def test_sub_resource(self):
        """ Test for SubResource """
        r = SubResource(1)
        self.assertEqual(r.id, 1)
        r.id = 2
        self.assertEqual(r.id, 2)
        self.assertEqual(str(r), "SubResource( 2 )")

    def test_dunder(self):
        """ Test the __magic__ methods on GDObject """
        v = Vector2(1, 2)
        self.assertEqual(repr(v), "Vector2( 1, 2 )")
        v2 = Vector2(1, 2)
        self.assertEqual(v, v2)
        v2.x = 10
        self.assertNotEqual(v, v2)
        self.assertNotEqual(v, (1, 2))
