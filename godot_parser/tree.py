""" Helper API for working with the Godot scene tree structure """
from collections import OrderedDict
from typing import Union

from .sections import GDNodeSection

__all__ = ["Node"]


class Node(object):
    """
    Wraps a GDNodeSection object

    Provides a way to access the node sections that is spatially-aware. It is stored in
    a tree structure instead of the flat list that the file format demands.
    """

    def __init__(
        self,
        name: str,
        type: str = None,
        instance: int = None,
        section: GDNodeSection = None,
        properties: dict = None,
    ):
        self.name = name
        self.type = type
        self.instance = instance
        self.parent = None
        self.section = section or GDNodeSection(name)
        self.properties = (
            OrderedDict() if properties is None else OrderedDict(properties)
        )
        self._children = []  # type: ignore

    def __getitem__(self, k: str):
        return self.properties[k]

    def __setitem__(self, k: str, v):
        self.properties[k] = v

    def __delitem__(self, k: str):
        try:
            del self.properties[k]
        except KeyError:
            pass

    def get(self, k: str, default=None):
        return self.properties.get(k, default)

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
        for child in self._children:
            yield from child.flatten(child_path)

    def _update_section(self, path: str = None):
        self.section.name = self.name
        self.section.type = self.type
        self.section.parent = path
        self.section.instance = self.instance
        self.section.properties = self.properties
        return self.section

    def get_children(self):
        """ Get all children of this node """
        return self._children

    def get_child(self, name_or_index: Union[int, str]):
        """ Get a child by name or index """
        if isinstance(name_or_index, int):
            return self._children[name_or_index]
        for node in self._children:
            if node.name == name_or_index:
                return node

    def get_node(self, path):
        """ Mimics the Godot get_node() behavior """
        if path in (".", ""):
            return self
        pieces = path.split("/")
        child = self.get_child(pieces[0])
        if child is None:
            return None
        return child.get_node("/".join(pieces[1:]))

    def add_child(self, node):
        """ Add a child to the current node """
        self._children.append(node)
        node.parent = self

    def remove_from_parent(self):
        """ Remove this node from its parent """
        self.parent.remove_child(self)

    def remove_child(self, node_or_name_or_index):
        """
        Remove a child

        You can pass in a Node, the name of a Node, or the index of the child
        """
        if isinstance(node_or_name_or_index, str):
            for i, node in enumerate(self._children):
                if node.name == node_or_name_or_index:
                    child = self._children.pop(i)
                    return
        elif isinstance(node_or_name_or_index, int):
            child = self._children.pop(node_or_name_or_index)
        else:
            self._children.remove(node_or_name_or_index)
            child = node_or_name_or_index
        if child is not None:
            child.parent = None

    def __str__(self):
        return "Node(%s)" % self.name

    def __repr__(self):
        return str(self)


class Tree(object):
    """ Container for the scene tree """

    def __init__(self, root=None):
        self.root = root

    @classmethod
    def build(cls, nodes):
        """ Build the Tree from a flat list of [node]'s """
        tree = cls()
        # Makes assumptions that the nodes are well-ordered
        for node in nodes:
            if node.parent is None:
                tree.root = Node.from_section(node)
            else:
                parent = tree.root.get_node(node.parent)
                parent.add_child(Node.from_section(node))
        return tree

    def flatten(self):
        """ Flatten the tree back into a list of GDNodeSection """
        ret = []
        if self.root is None:
            return ret
        for node in self.root.flatten():
            ret.append(node.section)
        return ret
