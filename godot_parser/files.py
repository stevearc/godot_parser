import os
from contextlib import contextmanager
from typing import (
    Iterable,
    Iterator,
    List,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
    cast,
)

from .objects import ExtResource, GDObject, SubResource
from .sections import (
    GDExtResourceSection,
    GDNodeSection,
    GDSection,
    GDSectionHeader,
    GDSubResourceSection,
)
from .structure import scene_file
from .util import find_project_root, gdpath_to_filepath

__all__ = ["GDFile", "GDScene", "GDResource"]

# Scene and resource files seem to group the section types together and sort them.
# This is the order I've observed
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


class GodotFileException(Exception):
    """ Thrown when there are errors in a Godot file """


class GDFile(object):
    """ Base class representing the contents of a Godot file """

    project_root: Optional[str] = None

    def __init__(self, *sections: GDSection) -> None:
        self._sections = list(sections)

    def add_section(self, new_section: GDSection) -> int:
        """ Add a section to the file and return the index of that section """
        new_idx = SCENE_ORDER.index(new_section.header.name)
        for i, section in enumerate(self._sections):
            idx = SCENE_ORDER.index(section.header.name)
            if new_idx < idx:  # type: ignore
                self._sections.insert(i, new_section)
                return i
        self._sections.append(new_section)
        return len(self._sections) - 1

    def remove_section(self, section: GDSection) -> bool:
        """ Remove a section from the file """
        idx = -1
        for i, s in enumerate(self._sections):
            if section == s:
                idx = i
                break
        if idx == -1:
            return False
        self.remove_at(idx)
        return True

    def remove_at(self, index: int) -> GDSection:
        """ Remove a section at an index """
        return self._sections.pop(index)

    def get_sections(self, name: str = None) -> List[GDSection]:
        """ Get all sections, or all sections of a given type """
        if name is None:
            return self._sections
        return [s for s in self._sections if s.header.name == name]

    def get_nodes(self) -> List[GDNodeSection]:
        """ Get all [node] sections """
        return cast(List[GDNodeSection], self.get_sections("node"))

    def get_ext_resources(self) -> List[GDExtResourceSection]:
        """ Get all [ext_resource] sections """
        return cast(List[GDExtResourceSection], self.get_sections("ext_resource"))

    def get_sub_resources(self) -> List[GDSubResourceSection]:
        """ Get all [sub_resource] sections """
        return cast(List[GDSubResourceSection], self.get_sections("sub_resource"))

    def find_node(
        self, property_constraints: Optional[dict] = None, **constraints
    ) -> Optional[GDNodeSection]:
        """ Find first [node] section that matches (see find_section) """
        return cast(
            GDNodeSection,
            self.find_section("node", property_constraints, **constraints),
        )

    def find_ext_resource(
        self, property_constraints: Optional[dict] = None, **constraints
    ) -> Optional[GDExtResourceSection]:
        """ Find first [ext_resource] section that matches (see find_section) """
        return cast(
            GDExtResourceSection,
            self.find_section("ext_resource", property_constraints, **constraints),
        )

    def find_sub_resource(
        self, property_constraints: Optional[dict] = None, **constraints
    ) -> Optional[GDSubResourceSection]:
        """ Find first [sub_resource] section that matches (see find_section) """
        return cast(
            GDSubResourceSection,
            self.find_section("sub_resource", property_constraints, **constraints),
        )

    def find_section(
        self,
        section_name_: str = None,
        property_constraints: Optional[dict] = None,
        **constraints
    ) -> Optional[GDSection]:
        """
        Find the first section that matches

        You may pass in a section_name, which will match the header name (e.g. 'node').
        You may also pass in kwargs that act as filters. For example::

            # Find the first node
            scene.find_section('node')
            # Find the first Sprite
            scene.find_section('node', type='Sprite')
            # Find the first ext_resource that references Health.tscn
            scene.find_section('ext_resourcee', path='Health.tscn')
        """
        for section in self.find_all(
            section_name_, property_constraints=property_constraints, **constraints
        ):
            return section
        return None

    def find_all(
        self,
        section_name_: str = None,
        property_constraints: Optional[dict] = None,
        **constraints
    ) -> Iterable[GDSection]:
        """ Same as find_section, but returns all matches """
        for section in self.get_sections(section_name_):
            found = True
            for k, v in constraints.items():
                if getattr(section, k, None) == v:
                    continue
                if section.header.get(k) == v:
                    continue
                found = False
                break
            if property_constraints is not None:
                for k, v in property_constraints.items():
                    if section.get(k) != v:
                        found = False
                        break
            if found:
                yield section

    def add_ext_resource(self, path: str, type: str) -> GDExtResourceSection:
        """ Add an ext_resource """
        next_id = 1 + max([s.id for s in self.get_ext_resources()] + [0])
        section = GDExtResourceSection(path, type, next_id)
        self.add_section(section)
        return section

    def add_sub_resource(self, type: str, **kwargs) -> GDSubResourceSection:
        """ Add a sub_resource """
        next_id = 1 + max([s.id for s in self.get_sub_resources()] + [0])
        section = GDSubResourceSection(type, next_id, **kwargs)
        self.add_section(section)
        return section

    def add_node(
        self, name: str, type: str = None, parent: str = None, index: int = None
    ) -> GDNodeSection:
        """
        Simple API for adding a node

        For a friendlier, tree-oriented API use use_tree()
        """
        node = GDNodeSection(name, type=type, parent=parent, index=index)
        self.add_section(node)
        return node

    def add_ext_node(
        self, name: str, instance: int, parent: str = None, index: int = None
    ) -> GDNodeSection:
        """
        Simple API for adding a node that instances an ext_resource

        For a friendlier, tree-oriented API use use_tree()
        """
        node = GDNodeSection.ext_node(name, instance, parent=parent, index=index)
        self.add_section(node)
        return node

    @property
    def is_inherited(self) -> bool:
        root = self.find_node(parent=None)
        if root is None:
            return False
        return root.instance is not None

    def get_parent_scene(self) -> Optional[str]:
        root = self.find_node(parent=None)
        if root is None or root.instance is None:
            return None
        parent_res = self.find_ext_resource(id=root.instance)
        if parent_res is None:
            return None
        return parent_res.path

    def load_parent_scene(self) -> "GDScene":
        if self.project_root is None:
            raise RuntimeError(
                "load_parent_scene() requires a project_root on the GDFile"
            )
        root = self.find_node(parent=None)
        if root is None or root.instance is None:
            raise RuntimeError("Cannot load parent scene; scene is not inherited")
        parent_res = self.find_ext_resource(id=root.instance)
        if parent_res is None:
            raise RuntimeError(
                "Could not find parent scene resource id(%d)" % root.instance
            )
        return GDScene.load(gdpath_to_filepath(self.project_root, parent_res.path))

    @contextmanager
    def use_tree(self):
        """
        Helper API for working with the nodes in a tree structure

        This temporarily builds the nodes into a tree, and flattens them back into the
        GD file format when done.

        Example::

            with scene.use_tree() as tree:
                tree.root = Node('MyScene')
                tree.root.add_child(Node('Sensor', type='Area2D'))
                tree.root.add_child(Node('HealthBar', instance=1))
            scene.write("MyScene.tscn")
        """
        from .tree import Tree

        tree = Tree.build(self)
        yield tree
        for i in range(len(self._sections) - 1, -1, -1):
            section = self._sections[i]
            if section.header.name == "node":
                self._sections.pop(i)
        nodes = tree.flatten()
        if not nodes:
            return
        # Let's find out where the root node belongs and then bulk add the rest at that
        # index
        i = self.add_section(nodes[0])
        self._sections[i + 1 : i + 1] = nodes[1:]

    def get_node(self, path: str = ".") -> Optional[GDNodeSection]:
        """ Mimics the Godot get_node API """
        with self.use_tree() as tree:
            if tree.root is None:
                return None
            node = tree.root.get_node(path)
        return node.section if node is not None else None

    @classmethod
    def parse(cls: Type[GDFileType], contents: str) -> GDFileType:
        """ Parse the contents of a Godot file """
        return cls.from_parser(scene_file.parseString(contents, parseAll=True))

    @classmethod
    def load(cls: Type[GDFileType], filepath: str) -> GDFileType:
        with open(filepath, "r") as ifile:
            file = cls.parse(ifile.read())
        file.project_root = find_project_root(filepath)
        return file

    @classmethod
    def from_parser(cls: Type[GDFileType], parse_result):
        first_section = parse_result[0]
        if first_section.header.name == "gd_scene":
            scene = GDScene.__new__(GDScene)
            scene._sections = list(parse_result)
            return scene
        elif first_section.header.name == "gd_resource":
            resource = GDResource.__new__(GDResource)
            resource._sections = list(parse_result)
            return resource
        return cls(*parse_result)

    def write(self, filename: str):
        """ Writes this to a file """
        os.makedirs(os.path.dirname(filename), exist_ok=True)
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
            1 + len(self.get_ext_resources()) + len(self.get_sub_resources())
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

    def remove_unused_resources(self):
        self._remove_unused_resources(self.get_ext_resources(), ExtResource)
        self._remove_unused_resources(self.get_sub_resources(), SubResource)

    def _remove_unused_resources(
        self,
        sections: Sequence[Union[GDExtResourceSection, GDSubResourceSection]],
        reference_type: Type[Union[ExtResource, SubResource]],
    ) -> None:
        seen = set()
        for ref in self._iter_node_resource_references():
            if isinstance(ref, reference_type):
                seen.add(ref.id)
        if len(seen) < len(sections):
            to_remove = [s for s in sections if s.id not in seen]
            for s in to_remove:
                self.remove_section(s)

    def renumber_resource_ids(self):
        """ Refactor all resource IDs to be sequential with no gaps """
        self._renumber_resource_ids(self.get_ext_resources(), ExtResource)
        self._renumber_resource_ids(self.get_sub_resources(), SubResource)

    def _iter_node_resource_references(
        self,
    ) -> Iterator[Union[ExtResource, SubResource]]:
        def iter_resources(value):
            if isinstance(value, (ExtResource, SubResource)):
                yield value
            elif isinstance(value, list):
                for v in value:
                    yield from iter_resources(v)
            elif isinstance(value, dict):
                for v in value.values():
                    yield from iter_resources(v)
            elif isinstance(value, GDObject):
                for v in value.args:
                    yield from iter_resources(v)

        for node in self.get_nodes():
            yield from iter_resources(node.header.attributes)
            yield from iter_resources(node.properties)
        for resource in self.get_sections("resource"):
            yield from iter_resources(resource.properties)

    def _renumber_resource_ids(
        self,
        sections: Sequence[Union[GDExtResourceSection, GDSubResourceSection]],
        reference_type: Type[Union[ExtResource, SubResource]],
    ) -> None:
        id_map = {}
        # First we renumber all the resource IDs so there are no gaps
        for i, section in enumerate(sections):
            id_map[section.id] = i + 1
            section.id = i + 1

        # Now we update all references to use the new number
        for ref in self._iter_node_resource_references():
            if isinstance(ref, reference_type):
                try:
                    ref.id = id_map[ref.id]
                except KeyError:
                    raise GodotFileException("Unknown resource ID %d" % ref.id)


class GDScene(GDCommonFile):
    def __init__(self, *sections: GDSection) -> None:
        super().__init__("gd_scene", *sections)


class GDResource(GDCommonFile):
    def __init__(self, *sections: GDSection) -> None:
        super().__init__("gd_resource", *sections)
