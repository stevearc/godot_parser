import re
from collections import OrderedDict
from typing import Optional, Type, TypeVar

from pyparsing import ParseBaseException

from .objects import ExtResource
from .util import stringify_object

__all__ = [
    "GDSectionHeader",
    "GDSection",
    "GDExtResourceSection",
    "GDSubResourceSection",
]

GDSectionHeaderType = TypeVar("GDSectionHeaderType", bound="GDSectionHeader")

GD_SECTION_REGISTRY = {}


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
        try:
            del self.attributes[k]
        except KeyError:
            pass

    def get(self, k: str, default=None):
        return self.attributes.get(k, default)

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


class GDSectionMeta(type):
    def __new__(cls, name, bases, dct):
        x = super().__new__(cls, name, bases, dct)
        section_name_camel = name[2:-7]
        section_name = re.sub(r"(?<!^)(?=[A-Z])", "_", section_name_camel).lower()
        GD_SECTION_REGISTRY[section_name] = x
        return x


GDSectionType = TypeVar("GDSectionType", bound="GDSection")


class GDSection(metaclass=GDSectionMeta):
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
        factory = GD_SECTION_REGISTRY.get(header.name, cls)
        section = factory.__new__(factory)
        section.header = header
        section.keyvals = OrderedDict()
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

    def __eq__(self, other) -> bool:
        if not isinstance(other, GDSection):
            return False
        return self.header.name == other.header.name and self.keyvals == other.keyvals

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)


class GDExtResourceSection(GDSection):
    def __init__(self, path: str, type: str, id: int):
        super().__init__(GDSectionHeader("ext_resource", path=path, type=type, id=id))

    @property
    def path(self) -> str:
        return self.header["path"]

    @path.setter
    def path(self, path: str) -> None:
        self.header["path"] = path

    @property
    def type(self) -> str:
        return self.header["type"]

    @type.setter
    def type(self, type: str) -> None:
        self.header["type"] = type

    @property
    def id(self) -> int:
        return self.header["id"]

    @id.setter
    def id(self, id: int) -> None:
        self.header["id"] = id


class GDSubResourceSection(GDSection):
    def __init__(self, type: str, id: int, **kwargs):
        super().__init__(GDSectionHeader("sub_resource", type=type, id=id), **kwargs)

    @property
    def type(self) -> str:
        return self.header["type"]

    @type.setter
    def type(self, type: str) -> None:
        self.header["type"] = type

    @property
    def id(self) -> int:
        return self.header["id"]

    @id.setter
    def id(self, id: int) -> None:
        self.header["id"] = id


class GDNodeSection(GDSection):
    def __init__(
        self,
        name: str,
        type: str = None,
        parent: str = None,
        instance: int = None,
        index: int = None,
        # TODO: instance_placeholder, owner, groups
    ):
        kwargs = {
            "name": name,
            "type": type,
            "parent": parent,
            "instance": ExtResource(instance) if instance is not None else None,
            "index": str(index) if index is not None else None,
        }
        super().__init__(
            GDSectionHeader(
                "node", **{k: v for k, v in kwargs.items() if v is not None}
            )
        )

    @classmethod
    def ext_node(cls, name: str, instance: int, parent: str = None, index: int = None):
        return cls(name, parent=parent, instance=instance, index=index)

    @property
    def name(self) -> str:
        return self.header["name"]

    @name.setter
    def name(self, name: str) -> None:
        self.header["name"] = name

    @property
    def type(self) -> Optional[str]:
        return self.header.get("type")

    @type.setter
    def type(self, type: Optional[str]) -> None:
        if type is None:
            del self.header["type"]
        else:
            self.header["type"] = type
            self.instance = None

    @property
    def parent(self) -> Optional[str]:
        return self.header.get("parent")

    @parent.setter
    def parent(self, parent: Optional[str]) -> None:
        if parent is None:
            del self.header["parent"]
        else:
            self.header["parent"] = parent

    @property
    def instance(self) -> Optional[int]:
        resource = self.header.get("instance")
        if resource is not None:
            return resource.id
        return None

    @instance.setter
    def instance(self, instance: Optional[int]) -> None:
        if instance is None:
            del self.header["instance"]
        else:
            self.header["instance"] = ExtResource(instance)
            self.type = None

    @property
    def index(self) -> Optional[int]:
        idx = self.header.get("index")
        if idx is not None:
            return int(idx)
        return None

    @index.setter
    def index(self, index: Optional[int]) -> None:
        if index is None:
            del self.header["index"]
        else:
            self.header["index"] = str(index)
