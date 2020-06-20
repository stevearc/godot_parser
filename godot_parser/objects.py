from functools import partial
from typing import Type, TypeVar

from .util import stringify_object

__all__ = ["GDObject", "Vector2", "Vector3", "NodePath"]

GD_OBJECT_REGISTRY = {}


class GDObjectMeta(type):
    def __new__(cls, name, bases, dct):
        x = super().__new__(cls, name, bases, dct)
        GD_OBJECT_REGISTRY[name] = x
        return x


GDObjectType = TypeVar("GDObjectType", bound="GDObject")


class GDObject(metaclass=GDObjectMeta):
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
        return self.args[0]

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
        return self.args[0]

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
