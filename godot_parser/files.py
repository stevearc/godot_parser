import os
from contextlib import contextmanager
from typing import List, Optional, Type, TypeVar

from .sections import (
    GDExtResourceSection,
    GDNodeSection,
    GDSection,
    GDSectionHeader,
    GDSubResourceSection,
)
from .tree import Tree

__all__ = ["GDFile", "GDScene", "GDResource"]

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


GDFileType = TypeVar("GDFileType", bound="GDFile")


class GDFile(object):
    """ Base class representing the contents of a Godot file """

    EXT = ".tscn"

    def __init__(self, *sections: GDSection) -> None:
        self._sections = list(sections)

    def add_section(self, new_section: GDSection) -> int:
        new_idx = SCENE_ORDER.index(new_section.header.name)
        for i, section in enumerate(self._sections):
            idx = SCENE_ORDER.index(section.header.name)
            if new_idx < idx:  # type: ignore
                self._sections.insert(i, new_section)
                return i
        self._sections.append(new_section)
        return len(self._sections) - 1

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

    def find_section(self, name: str = None, **constraints):
        for section in self.get_sections(name):
            found = True
            for k, v in constraints.items():
                if getattr(section, k, None) == v:
                    continue
                if section.header.get(k) == v:
                    continue
                found = False
                break
            if found:
                return section
        return None

    def add_ext_resource(self, path: str, type: str) -> int:
        next_id = 1 + max(
            [s.id for s in self.get_sections("ext_resource")]  # type: ignore
            + [0]
        )
        self.add_section(GDExtResourceSection(path, type, next_id))
        return next_id

    def add_sub_resource(self, type: str, **kwargs) -> int:
        next_id = 1 + max(
            [s.id for s in self.get_sections("sub_resource")]  # type: ignore
            + [0]
        )
        self.add_section(GDSubResourceSection(type, next_id, **kwargs))
        return next_id

    def add_node(
        self, name: str, type: str = None, parent: str = None, index: int = None,
    ) -> GDNodeSection:
        node = GDNodeSection(name, type=type, parent=parent, index=index)
        self.add_section(node)
        return node

    def add_ext_node(
        self, name: str, instance: int, parent: str = None, index: int = None,
    ) -> GDNodeSection:
        node = GDNodeSection.ext_node(name, instance, parent=parent, index=index)
        self.add_section(node)
        return node

    @contextmanager
    def use_tree(self):
        nodes = self.get_sections("node")
        tree = Tree.build(nodes)
        yield tree
        for i in range(len(self._sections) - 1, -1, -1):
            section = self._sections[i]
            if section.header.name == "node":
                self._sections.pop(i)
        nodes = tree.flatten()
        # add_section messes with ordering. Let's find out where the root node belongs
        # and then bulk add the rest at that index
        i = self.add_section(nodes[0])
        self._sections[i + 1 : i + 1] = nodes[1:]

    def get_node(self, path: str = ".") -> Optional[GDNodeSection]:
        with self.use_tree() as tree:
            if tree.root is None:
                return None
            return tree.root.get_node(path)

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
        ext = os.path.splitext(filename)[1]
        if not ext:
            filename += self.EXT
        with open(filename, "w") as ofile:
            ofile.write(str(self))

    def __str__(self) -> str:
        return "\n\n".join([str(s) for s in self._sections]) + "\n"

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

    def add_section(self, new_section: GDSection) -> int:
        idx = super().add_section(new_section)
        if new_section.header.name in ["ext_resource", "sub_resource"]:
            self.load_steps += 1
        return idx

    def remove_at(self, index: int):
        section = self._sections.pop(index)
        if section.header.name in ["ext_resource", "sub_resource"]:
            self.load_steps -= 1


class GDScene(GDCommonFile):
    def __init__(self, *sections: GDSection) -> None:
        super().__init__("gd_scene", *sections)


class GDResource(GDCommonFile):
    EXT = ".tres"

    def __init__(self, *sections: GDSection) -> None:
        super().__init__("gd_resource", *sections)
