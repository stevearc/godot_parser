from typing import List, Type, TypeVar

from .sections import (
    GDExtResourceSection,
    GDSection,
    GDSectionHeader,
    GDSubResourceSection,
)

__all__ = ["GDFile", "GDScene", "GDResource"]

GDFileType = TypeVar("GDFileType", bound="GDFile")


class GDFile(object):
    """ Base class representing the contents of a Godot file """

    def __init__(self, *sections: GDSection) -> None:
        self._sections = list(sections)

    def add_section(self, new_section: GDSection):
        idx = 0
        for i, section in enumerate(self._sections):
            if new_section < section:  # type: ignore
                self._sections.insert(i, new_section)
                break
        self._sections.append(new_section)
        return self

    def remove_section(self, section: GDSection) -> bool:
        idx = -1
        for i, s in enumerate(self._sections):
            if section == s:
                idx = i
                break
        if idx == -1:
            return False
        self.remove_at(idx)
        return True

    def remove_at(self, index: int):
        section = self._sections.pop(index)

    def get_sections(self, name: str = None) -> List[GDSection]:
        if name is None:
            return self._sections
        return [s for s in self._sections if s.header.name == name]

    def add_ext_resource(self, path: str, type: str):
        next_id = 1 + max(
            [s.id for s in self.get_sections("ext_resource")]  # type: ignore
            + [0]
        )
        self.add_section(GDExtResourceSection(path, type, next_id))
        return self

    def add_sub_resource(self, type: str):
        next_id = 1 + max(
            [s.id for s in self.get_sections("sub_resource")]  # type: ignore
            + [0]
        )
        self.add_section(GDSubResourceSection(type, next_id))
        return self

    @classmethod
    def from_parser(cls: Type[GDFileType], parse_result):
        if not parse_result:
            return cls()
        first_section = parse_result[0]
        if first_section.header.name == "gd_scene":
            scene = GDScene.__new__(GDScene)
            scene._sections = list(parse_result)
            return scene
        elif first_section.header.name == "gd_scene":
            resource = GDResource.__new__(GDResource)
            resource._sections = list(parse_result)
            return resource
        return cls(*parse_result)

    def write(self, filename):
        """ Writes this to a file """
        with open(filename, "w") as ofile:
            ofile.write(str(self))

    def __str__(self) -> str:
        return "\n\n".join([str(s) for s in self._sections])

    def __repr__(self) -> str:
        return "%s(%s)" % (type(self).__name__, self.__str__())

    def __eq__(self, other) -> bool:
        if not isinstance(other, GDFile):
            return False
        return self._sections == other._sections

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)


class GDCommonFile(GDFile):
    """ Base class with common application logic for all Godot file types """

    def __init__(self, name: str, *sections: GDSection) -> None:
        super().__init__(
            GDSection(GDSectionHeader(name, load_steps=1, format=2)), *sections
        )
        self.load_steps = (
            1
            + len(self.get_sections("ext_resource"))
            + len(self.get_sections("sub_resource"))
        )

    @property
    def load_steps(self) -> int:
        return self._sections[0].header["load_steps"]

    @load_steps.setter
    def load_steps(self, steps: int):
        self._sections[0].header["load_steps"] = steps

    def add_section(self, new_section: GDSection) -> None:
        super().add_section(new_section)
        if new_section.header.name in ["ext_resource", "sub_resource"]:
            self.load_steps += 1

    def remove_at(self, index: int):
        section = self._sections.pop(index)
        if section.header.name in ["ext_resource", "sub_resource"]:
            self.load_steps -= 1


class GDScene(GDCommonFile):
    def __init__(self, *sections: GDSection) -> None:
        super().__init__("gd_scene", *sections)


class GDResource(GDCommonFile):
    def __init__(self, *sections: GDSection) -> None:
        super().__init__("gd_resource", *sections)
