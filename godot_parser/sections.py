from collections import OrderedDict
from functools import total_ordering
from typing import Type, TypeVar

from pyparsing import ParseBaseException

from .util import stringify_object

__all__ = [
    "GDSectionHeader",
    "GDSection",
    "GDExtResourceSection",
    "GDSubResourceSection",
]

GDSectionHeaderType = TypeVar("GDSectionHeaderType", bound="GDSectionHeader")

SCENE_ORDER = [
    "gd_scene",
    "gd_resource",
    "ext_resource",
    "sub_resource",
    "resource",
    "node",
    "connection",
    "editable",
]


class GodotParseException(ParseBaseException):
    pass


class GDSectionHeader(object):
    def __init__(self, _name: str, **kwargs) -> None:
        self.name = _name
        self.attributes = OrderedDict()
        for k, v in kwargs.items():
            self.attributes[k] = v

    def __getitem__(self, k: str):
        return self.attributes[k]

    def __setitem__(self, k: str, v):
        self.attributes[k] = v

    def __delitem__(self, k: str):
        del self.attributes[k]

    @classmethod
    def from_parser(
        cls: Type[GDSectionHeaderType], parse_result
    ) -> GDSectionHeaderType:
        header = cls(parse_result[0])
        for attribute in parse_result[1:]:
            header.attributes[attribute[0]] = attribute[1]
        return header

    def __str__(self) -> str:
        attribute_str = ""
        if self.attributes:
            attribute_str = " " + " ".join(
                ["%s=%s" % (k, stringify_object(v)) for k, v in self.attributes.items()]
            )
        return "[" + self.name + attribute_str + "]"

    def __repr__(self) -> str:
        return "GDSectionHeader(%s)" % self.__str__()

    def __eq__(self, other) -> bool:
        if not isinstance(other, GDSectionHeader):
            return False
        return self.name == other.name and self.attributes == other.attributes

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)


GDSectionType = TypeVar("GDSectionType", bound="GDSection")


@total_ordering
class GDSection(object):
    def __init__(self, header: GDSectionHeader, **kwargs) -> None:
        self.header = header
        self.keyvals = OrderedDict()
        for k, v in kwargs.items():
            self.keyvals[k] = v

    def __getitem__(self, k: str):
        return self.keyvals[k]

    def __setitem__(self, k: str, v):
        self.keyvals[k] = v

    def __delitem__(self, k: str):
        del self.keyvals[k]

    @classmethod
    def from_parser(cls: Type[GDSectionType], parse_result):
        header = parse_result[0]
        if header.name == "ext_resource":
            return GDExtResourceSection.from_parser(parse_result)
        section = cls(header)
        for k, v in parse_result[1:]:
            section[k] = v
        return section

    def __str__(self) -> str:
        ret = str(self.header)
        if self.keyvals:
            ret += "\n" + "\n".join(
                ["%s = %s" % (k, stringify_object(v)) for k, v in self.keyvals.items()]
            )
        return ret

    def __repr__(self) -> str:
        return "%s(%s)" % (type(self).__name__, self.__str__())

    def __lt__(self, other: GDSectionType) -> bool:
        i = SCENE_ORDER.index(self.header.name)
        other_i = SCENE_ORDER.index(other.header.name)
        if i != other_i:
            return i < other_i
        return id(self) < id(other)

    def __eq__(self, other) -> bool:
        if not isinstance(other, GDSection):
            return False
        return self.header == other.header and self.keyvals == other.keyvals

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)


class GDExtResourceSection(GDSection):
    def __init__(self, path: str, type: str, id: int):
        super().__init__(GDSectionHeader("ext_resource", path=path, type=type, id=id))

    @property
    def path(self) -> str:
        return self.header.attributes["path"]

    @path.setter
    def path(self, path: str) -> None:
        self.header.attributes["path"] = path

    @property
    def type(self) -> str:
        return self.header.attributes["type"]

    @type.setter
    def type(self, type: str) -> None:
        self.header.attributes["type"] = type

    @property
    def id(self) -> int:
        return self.header.attributes["id"]

    @id.setter
    def id(self, id: int) -> None:
        self.header.attributes["id"] = id

    @classmethod
    def from_parser(cls: Type[GDSectionType], parse_result):
        if len(parse_result) > 1:
            raise GodotParseException("ext_resource cannot have properties")
        header = parse_result[0]
        return cls(**header.attributes)


class GDSubResourceSection(GDSection):
    def __init__(self, type: str, id: int, **kwargs):
        super().__init__(GDSectionHeader("sub_resource", type=type, id=id), **kwargs)

    @property
    def type(self) -> str:
        return self.header.attributes["type"]

    @type.setter
    def type(self, type: str) -> None:
        self.header.attributes["type"] = type

    @property
    def id(self) -> int:
        return self.header.attributes["id"]

    @id.setter
    def id(self, id: int) -> None:
        self.header.attributes["id"] = id

    @classmethod
    def from_parser(cls: Type[GDSectionType], parse_result):
        header = parse_result[0]
        section = cls(**header.attributes)
        for k, v in parse_result[1:]:
            section[k] = v
        return section
