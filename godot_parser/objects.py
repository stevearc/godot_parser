"""Wrappers for Godot's non-primitive object types"""

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
    "StringName",
    "TypedArray",
    "TypedDictionary",
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
        return "%s(%s)" % (
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

    def __hash__(self):
        return hash(frozenset((self.name, *self.args)))


class Vector2(GDObject):
    def __init__(self, x: float, y: float) -> None:
        super().__init__("Vector2", x, y)

    def __getitem__(self, idx) -> float:
        return self.args[idx]

    def __setitem__(self, idx: int, value: float):
        self.args[idx] = value

    @property
    def x(self) -> float:
        """Getter for x"""
        return self.args[0]

    @x.setter
    def x(self, x: float) -> None:
        """Setter for x"""
        self.args[0] = x

    @property
    def y(self) -> float:
        """Getter for y"""
        return self.args[1]

    @y.setter
    def y(self, y: float) -> None:
        """Setter for y"""
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
        """Getter for x"""
        return self.args[0]

    @x.setter
    def x(self, x: float) -> None:
        """Setter for x"""
        self.args[0] = x

    @property
    def y(self) -> float:
        """Getter for y"""
        return self.args[1]

    @y.setter
    def y(self, y: float) -> None:
        """Setter for y"""
        self.args[1] = y

    @property
    def z(self) -> float:
        """Getter for z"""
        return self.args[2]

    @z.setter
    def z(self, z: float) -> None:
        """Setter for z"""
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
        """Getter for r"""
        return self.args[0]

    @r.setter
    def r(self, r: float) -> None:
        """Setter for r"""
        self.args[0] = r

    @property
    def g(self) -> float:
        """Getter for g"""
        return self.args[1]

    @g.setter
    def g(self, g: float) -> None:
        """Setter for g"""
        self.args[1] = g

    @property
    def b(self) -> float:
        """Getter for b"""
        return self.args[2]

    @b.setter
    def b(self, b: float) -> None:
        """Setter for b"""
        self.args[2] = b

    @property
    def a(self) -> float:
        """Getter for a"""
        return self.args[3]

    @a.setter
    def a(self, a: float) -> None:
        """Setter for a"""
        self.args[3] = a


class NodePath(GDObject):
    def __init__(self, path: str) -> None:
        super().__init__("NodePath", path)

    @property
    def path(self) -> str:
        """Getter for path"""
        return self.args[0]

    @path.setter
    def path(self, path: str) -> None:
        """Setter for path"""
        self.args[0] = path

    def __str__(self) -> str:
        return '%s("%s")' % (self.name, self.path)


class ExtResource(GDObject):
    def __init__(self, id: int) -> None:
        super().__init__("ExtResource", id)

    @property
    def id(self) -> int:
        """Getter for id"""
        return self.args[0]

    @id.setter
    def id(self, id: int) -> None:
        """Setter for id"""
        self.args[0] = id


class SubResource(GDObject):
    def __init__(self, id: int) -> None:
        super().__init__("SubResource", id)

    @property
    def id(self) -> int:
        """Getter for id"""
        return self.args[0]

    @id.setter
    def id(self, id: int) -> None:
        """Setter for id"""
        self.args[0] = id


class TypedArray:
    def __init__(self, type, list_) -> None:
        self.name = "Array"
        self.type = type
        self.list_ = list_

    @classmethod
    def WithCustomName(cls: Type["TypedArray"], name, type, list_) -> "TypedArray":
        custom_array = TypedArray(type, list_)
        custom_array.name = name
        return custom_array

    @classmethod
    def from_parser(cls: Type["TypedArray"], parse_result) -> "TypedArray":
        return TypedArray.WithCustomName(*parse_result)

    def __str__(self) -> str:
        return "%s[%s](%s)" % (self.name, self.type, stringify_object(self.list_))

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other) -> bool:
        if not isinstance(other, TypedArray):
            return False
        return (
            self.name == other.name
            and self.type == other.type
            and self.list_ == other.list_
        )

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __hash__(self):
        return hash(frozenset((self.name, self.type, self.list_)))


class TypedDictionary:
    def __init__(self, key_type, value_type, dict_) -> None:
        self.name = "Dictionary"
        self.key_type = key_type
        self.value_type = value_type
        self.dict_ = dict_

    @classmethod
    def WithCustomName(
        cls: Type["TypedDictionary"], name, key_type, value_type, dict_
    ) -> "TypedDictionary":
        custom_dict = TypedDictionary(key_type, value_type, dict_)
        custom_dict.name = name
        return custom_dict

    @classmethod
    def from_parser(cls: Type["TypedDictionary"], parse_result) -> "TypedDictionary":
        return TypedDictionary.WithCustomName(*parse_result)

    def __str__(self) -> str:
        return "%s[%s, %s](%s)" % (
            self.name,
            self.key_type,
            self.value_type,
            stringify_object(self.dict_),
        )

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other) -> bool:
        if not isinstance(other, TypedDictionary):
            return False
        return (
            self.name == other.name
            and self.key_type == other.key_type
            and self.value_type == other.value_type
            and self.dict_ == other.dict_
        )

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __hash__(self):
        return hash(frozenset((self.name, self.key_type, self.value_type, self.dict_)))


class StringName:
    def __init__(self, str) -> None:
        self.str = str

    @classmethod
    def from_parser(cls: Type["StringName"], parse_result) -> "StringName":
        return StringName(parse_result[0])

    def __str__(self) -> str:
        return "&" + stringify_object(self.str)

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other) -> bool:
        if not isinstance(other, StringName):
            return False
        return self.str == other.str

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.str)
