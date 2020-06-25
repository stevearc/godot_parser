""" Wrappers for Godot's non-primitive object types """

from functools import partial
from typing import Type, TypeVar

from .util import stringify_object

__all__ = [
    "GDObject",
    "Vector2",
    "Vector3",
    "Color",
    "NodePath",
    "ExtResource",
    "SubResource",
]

GD_OBJECT_REGISTRY = {}


class GDObjectMeta(type):
    """
    This is me trying to be too clever for my own good

    Odds are high that it'll cause some weird hard-to-debug issues at some point, but
    isn't it neeeeeat? -_-
    """

    def __new__(cls, name, bases, dct):
        x = super().__new__(cls, name, bases, dct)
        GD_OBJECT_REGISTRY[name] = x
        return x


GDObjectType = TypeVar("GDObjectType", bound="GDObject")


class GDObject(metaclass=GDObjectMeta):
    """
    Base class for all GD Object types

    Can be used to represent any GD type. For example::

        GDObject('Vector2', 1, 2) == Vector2(1, 2)
    """

    def __init__(self, name, *args) -> None:
        self.name = name
        self.args = list(args)

    @classmethod
    def from_parser(cls: Type[GDObjectType], parse_result) -> GDObjectType:
        name = parse_result[0]
        factory = GD_OBJECT_REGISTRY.get(name, partial(GDObject, name))
        return factory(*parse_result[1:])

    def __str__(self) -> str:
        return "%s( %s )" % (
            self.name,
            ", ".join([stringify_object(v) for v in self.args]),
        )

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other) -> bool:
        if not isinstance(other, GDObject):
            return False
        return self.name == other.name and self.args == other.args

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)


class Vector2(GDObject):
    def __init__(self, x: float, y: float) -> None:
        super().__init__("Vector2", x, y)

    def __getitem__(self, idx) -> float:
        return self.args[idx]

    def __setitem__(self, idx: int, value: float):
        self.args[idx] = value

    @property
    def x(self) -> float:
        """ Getter for x """
        return self.args[0]

    @x.setter
    def x(self, x: float) -> None:
        """ Setter for x """
        self.args[0] = x

    @property
    def y(self) -> float:
        """ Getter for y """
        return self.args[1]

    @y.setter
    def y(self, y: float) -> None:
        """ Setter for y """
        self.args[1] = y


class Vector3(GDObject):
    def __init__(self, x: float, y: float, z: float) -> None:
        super().__init__("Vector3", x, y, z)

    def __getitem__(self, idx: int) -> float:
        return self.args[idx]

    def __setitem__(self, idx: int, value: float) -> None:
        self.args[idx] = value

    @property
    def x(self) -> float:
        """ Getter for x """
        return self.args[0]

    @x.setter
    def x(self, x: float) -> None:
        """ Setter for x """
        self.args[0] = x

    @property
    def y(self) -> float:
        """ Getter for y """
        return self.args[1]

    @y.setter
    def y(self, y: float) -> None:
        """ Setter for y """
        self.args[1] = y

    @property
    def z(self) -> float:
        """ Getter for z """
        return self.args[2]

    @z.setter
    def z(self, z: float) -> None:
        """ Setter for z """
        self.args[2] = z


class Color(GDObject):
    def __init__(self, r: float, g: float, b: float, a: float) -> None:
        assert 0 <= r <= 1
        assert 0 <= g <= 1
        assert 0 <= b <= 1
        assert 0 <= a <= 1
        super().__init__("Color", r, g, b, a)

    def __getitem__(self, idx: int) -> float:
        return self.args[idx]

    def __setitem__(self, idx: int, value: float) -> None:
        self.args[idx] = value

    @property
    def r(self) -> float:
        """ Getter for r """
        return self.args[0]

    @r.setter
    def r(self, r: float) -> None:
        """ Setter for r """
        self.args[0] = r

    @property
    def g(self) -> float:
        """ Getter for g """
        return self.args[1]

    @g.setter
    def g(self, g: float) -> None:
        """ Setter for g """
        self.args[1] = g

    @property
    def b(self) -> float:
        """ Getter for b """
        return self.args[2]

    @b.setter
    def b(self, b: float) -> None:
        """ Setter for b """
        self.args[2] = b

    @property
    def a(self) -> float:
        """ Getter for a """
        return self.args[3]

    @a.setter
    def a(self, a: float) -> None:
        """ Setter for a """
        self.args[3] = a


class NodePath(GDObject):
    def __init__(self, path: str) -> None:
        super().__init__("NodePath", path)

    @property
    def path(self) -> str:
        """ Getter for path """
        return self.args[0]

    @path.setter
    def path(self, path: str) -> None:
        """ Setter for path """
        self.args[0] = path

    def __str__(self) -> str:
        return '%s("%s")' % (self.name, self.path)


class ExtResource(GDObject):
    def __init__(self, id: int) -> None:
        super().__init__("ExtResource", id)

    @property
    def id(self) -> int:
        """ Getter for id """
        return self.args[0]

    @id.setter
    def id(self, id: int) -> None:
        """ Setter for id """
        self.args[0] = id


class SubResource(GDObject):
    def __init__(self, id: int) -> None:
        super().__init__("SubResource", id)

    @property
    def id(self) -> int:
        """ Getter for id """
        return self.args[0]

    @id.setter
    def id(self, id: int) -> None:
        """ Setter for id """
        self.args[0] = id
