from collections import OrderedDict
from typing import Type, TypeVar

from .util import stringify_object

__all__ = ["GDSectionHeader", "GDSection", "GDFile", "GDScene", "GDResource"]
SCENE_ORDER = [
    "gd_scene",
    "ext_resource",
    "sub_resource",
    "node",
    "connection",
    "editable",
]

RESOURCE_ORDER = [
    "gd_resource",
    "ext_resource",
    "sub_resource",
    "resource",
]

GDSectionHeaderType = TypeVar("GDSectionHeaderType", bound="GDSectionHeader")


class GDSectionHeader(object):
    def __init__(self, _name: str, **kwargs) -> None:
        self.name = _name
        self.attributes = OrderedDict()
        for k, v in kwargs.items():
            self.attributes[k] = v

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


class GDSection(object):
    def __init__(self, header: GDSectionHeader, **kwargs) -> None:
        self.header = header
        self.keyvals = OrderedDict()
        for k, v in kwargs.items():
            self.keyvals[k] = v

    @classmethod
    def from_parser(cls: Type[GDSectionType], parse_result) -> GDSectionType:
        section = cls(parse_result[0])
        for k, v in parse_result[1:]:
            section.keyvals[k] = v
        return section

    def __str__(self) -> str:
        ret = str(self.header)
        if self.keyvals:
            ret += "\n" + "\n".join(
                ["%s = %s" % (k, stringify_object(v)) for k, v in self.keyvals.items()]
            )
        return ret

    def __repr__(self) -> str:
        return "GDSection(%s)" % self.__str__()

    def __eq__(self, other) -> bool:
        if not isinstance(other, GDSection):
            return False
        return self.header == other.header and self.keyvals == other.keyvals

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)


GDFileType = TypeVar("GDFileType", bound="GDFile")


class GDFile(object):
    """ Base class representing the contents of a Godot file """

    def __init__(self, *sections: GDSection) -> None:
        self.sections = sections

    @classmethod
    def from_parser(cls: Type[GDFileType], parse_result):
        if not parse_result:
            return cls()
        first_section = parse_result[0]
        if first_section.header.name == "gd_scene":
            return GDScene(*parse_result)
        elif first_section.header.name == "gd_scene":
            return GDResource(*parse_result)
        return cls(*parse_result)

    def __str__(self) -> str:
        return "\n\n".join([str(s) for s in self.sections])

    def __repr__(self) -> str:
        return "GDFile(%s)" % self.__str__()

    def __eq__(self, other) -> bool:
        if not isinstance(other, GDFile):
            return False
        return self.sections == other.sections

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)


class GDScene(GDFile):
    def __repr__(self) -> str:
        return "GDScene(%s)" % self.__str__()


class GDResource(GDFile):
    def __repr__(self) -> str:
        return "GDResource(%s)" % self.__str__()
