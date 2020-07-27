""" Helper API for working with the Godot scene tree structure """
from collections import OrderedDict
from typing import Any, List, Optional, Union

from .files import GDFile
from .sections import GDNodeSection

__all__ = ["Node", "TreeMutationException"]
SENTINEL = object()


class TreeMutationException(Exception):
    """ Raised when attempting to mutate the tree in an unsupported way """


class Node(object):
    """
    Wraps a GDNodeSection object

    Provides a way to access the node sections that is spatially-aware. It is stored in
    a tree structure instead of the flat list that the file format demands.
    """

    _children: List["Node"]
    _parent: Optional["Node"]
    _index: Optional[int]

    def __init__(
        self,
        name: str,
        type: str = None,
        instance: int = None,
        section: GDNodeSection = None,
        properties: dict = None,
    ):
        self._name = name
        self._type = type
        self._instance = instance
        self._parent = None
        self._index = None
        self.section = section or GDNodeSection(name)
        self.properties = (
            OrderedDict() if properties is None else OrderedDict(properties)
        )
        self._children = []  # type: ignore
        self._inherited_node: Optional["Node"] = None

    def _mark_inherited(self) -> None:
        clone = self.clone()
        clone._inherited_node = self._inherited_node
        self._inherited_node = clone
        self.properties.clear()
        self._type = None
        self._instance = None
        self.section = GDNodeSection(self.name)

    def clone(self) -> "Node":
        return Node(
            self.name, self.type, self.instance, properties=OrderedDict(self.properties)
        )

    @property
    def parent(self) -> Optional["Node"]:
        return self._parent

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, new_name: str) -> None:
        if self._inherited_node is not None:
            raise TreeMutationException("Cannot change the name of an inherited node")
        self._name = new_name

    @property
    def type(self) -> Optional[str]:
        if self._inherited_node is not None:
            return self._inherited_node.type
        return self._type

    @type.setter
    def type(self, new_type: Optional[str]) -> None:
        if self.is_inherited:
            raise TreeMutationException("Cannot change the type of an inherited node")
        if new_type is not None:
            self._instance = None
        self._type = new_type

    @property
    def instance(self) -> Optional[int]:
        if self._inherited_node is not None:
            return self._inherited_node.instance
        return self._instance

    @instance.setter
    def instance(self, new_instance: Optional[int]) -> None:
        if self.is_inherited:
            raise TreeMutationException(
                "Cannot change the instance of an inherited node"
            )
        if new_instance is not None:
            self._type = None
        self._instance = new_instance

    def __getitem__(self, k: str) -> Any:
        v = self.properties.get(k, SENTINEL)
        if v is SENTINEL:
            if self._inherited_node is not None:
                return self._inherited_node[k]
            raise KeyError("No property %s found on node %s" % (k, self.name))
        return v

    def __setitem__(self, k: str, v: Any) -> None:
        if self._inherited_node is not None and v == self._inherited_node.get(
            k, SENTINEL
        ):
            del self[k]
        else:
            self.properties[k] = v

    def __delitem__(self, k: str) -> None:
        try:
            del self.properties[k]
        except KeyError:
            pass

    def get(self, k: str, default: Any = None) -> Any:
        v = self.properties.get(k, SENTINEL)
        if v is SENTINEL:
            if self._inherited_node is not None:
                return self._inherited_node.get(k, default)
            return default
        return v

    @classmethod
    def from_section(cls, section: GDNodeSection):
        """ Create a Node from a GDNodeSection """
        return cls(
            section.name,
            section.type,
            section.instance,
            section,
            properties=section.properties,
        )

    def flatten(self, path: str = None):
        """
        Write values to GDNodeSection and iterate over children

        This call will copy the existing values on this node into the GDNodeSection and
        iterate over self and all child nodes, calling flatten on them as well.
        """

        self._update_section(path)

        yield self
        if path is None:
            child_path = "."
        elif path == ".":
            child_path = self.name
        else:
            child_path = path + "/" + self.name
        child_idx = 0
        # Assign an index to children if we were assigned one, or if we are the root
        # node of an inherited scene
        use_index = self._index is not None or (
            self.parent is None and self._instance is not None
        )
        for child in self._children:
            if use_index:
                child._index = child_idx
                child_idx += 1
            yield from child.flatten(child_path)

    def _update_section(self, path: str = None) -> None:
        self.section.name = self.name
        self.section.type = self._type
        self.section.parent = path
        self.section.instance = self._instance
        self.section.properties = self.properties
        if self._index is not None:
            self.section.index = self._index

    @property
    def is_inherited(self) -> bool:
        return self._inherited_node is not None

    @property
    def has_changes(self) -> bool:
        return bool(self.properties)

    def get_children(self) -> List["Node"]:
        """ Get all children of this node """
        return self._children

    def get_child(self, name_or_index: Union[int, str]) -> Optional["Node"]:
        """ Get a child by name or index """
        if isinstance(name_or_index, int):
            return self._children[name_or_index]
        for node in self._children:
            if node.name == name_or_index:
                return node
        return None

    def get_node(self, path: str) -> Optional["Node"]:
        """ Mimics the Godot get_node() behavior """
        if path in (".", ""):
            return self
        pieces = path.split("/")
        child = self.get_child(pieces[0])
        if child is None:
            return None
        return child.get_node("/".join(pieces[1:]))

    def add_child(self, node: "Node") -> None:
        """ Add a child to the current node """
        self._children.append(node)
        node._parent = self

    def insert_child(self, index: int, node: "Node") -> None:
        """ Add a child to the current node before the specified index """
        self._children.insert(index, node)
        node._parent = self

    def _merge_child(self, section: GDNodeSection) -> None:
        """ Add a child that may be an inherited node """
        for child in self._children:
            if child.name == section.name:
                child.section = section
                child.properties = section.properties
                return
        self.add_child(Node.from_section(section))

    def remove_from_parent(self) -> None:
        """ Remove this node from its parent """
        if self.parent is not None:
            self.parent.remove_child(self)

    def remove_child(self, node_or_name_or_index: Union[str, int, "Node"]) -> None:
        """
        Remove a child

        You can pass in a Node, the name of a Node, or the index of the child
        """
        if isinstance(node_or_name_or_index, str):
            for i, node in enumerate(self._children):
                if node.name == node_or_name_or_index:
                    if node.is_inherited:
                        raise TreeMutationException(
                            "Cannot remove inherited node %s" % node.name
                        )
                    child = self._children.pop(i)
                    break
        elif isinstance(node_or_name_or_index, int):
            child = self._children[node_or_name_or_index]
            if child.is_inherited:
                raise TreeMutationException(
                    "Cannot remove inherited node %s" % child.name
                )
            self._children.pop(node_or_name_or_index)
        else:
            child = node_or_name_or_index
            if child.is_inherited:
                raise TreeMutationException(
                    "Cannot remove inherited node %s" % child.name
                )
            self._children.remove(node_or_name_or_index)
        if child is not None:
            child._parent = None

    def __str__(self):
        return "Node(%s)" % self.name

    def __repr__(self):
        return str(self)


class Tree(object):
    """ Container for the scene tree """

    def __init__(self, root: Optional[Node] = None):
        self.root = root

    def get_node(self, path: str) -> Optional[Node]:
        """ Mimics the Godot get_node() behavior """
        if self.root is None:
            return None
        return self.root.get_node(path)

    @classmethod
    def build(cls, file: GDFile):
        """ Build the Tree from a flat list of [node]'s """
        tree = cls()
        # Makes assumptions that the nodes are well-ordered
        for section in file.get_nodes():
            if section.parent is None:
                root = Node.from_section(section)
                tree.root = root
                if root.instance is not None:
                    _load_parent_scene(root, file)
            else:
                parent = tree.get_node(section.parent)
                if parent is None:
                    raise TreeMutationException(
                        "Cannot find parent node %s of %s"
                        % (section.parent, section.name)
                    )
                parent._merge_child(section)
        return tree

    def flatten(self) -> List[GDNodeSection]:
        """ Flatten the tree back into a list of GDNodeSection """
        ret: List[GDNodeSection] = []
        if self.root is None:
            return ret
        for node in self.root.flatten():
            if node.is_inherited and not node.has_changes and node.parent is not None:
                continue
            ret.append(node.section)
        return ret


def _load_parent_scene(root: Node, file: GDFile):
    parent_file: GDFile = file.load_parent_scene()
    parent_tree = Tree.build(parent_file)
    # Transfer parent scene's children to this scene
    for child in parent_tree.root.get_children():
        root.add_child(child)
    # Mark the entire parent tree as inherited
    for node in parent_tree.root.flatten():
        node._mark_inherited()
    # Mark the root node as inherited
    root._inherited_node = parent_tree.root
