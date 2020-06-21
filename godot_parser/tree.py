from collections import OrderedDict

from .sections import GDNodeSection

__all__ = ["Node"]


class Node(object):
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
        self.section = section or GDNodeSection(name)
        self.properties = (
            OrderedDict() if properties is None else OrderedDict(properties)
        )
        self._children = []  # type: ignore

    @classmethod
    def from_section(cls, section: GDNodeSection):
        return cls(
            section.name,
            section.type,
            section.instance,
            section,
            properties=section.keyvals,
        )

    def visit(self, path: str = None):
        self._update_section(path)

        yield self
        if path is None:
            child_path = "."
        elif path == ".":
            child_path = self.name
        else:
            child_path = path + "/" + self.name
        for child in self._children:
            yield from child.visit(child_path)

    def _update_section(self, path: str = None):
        self.section.name = self.name
        self.section.type = self.type
        self.section.parent = path
        self.section.instance = self.instance
        self.section.keyvals = self.properties
        return self.section

    def get_children(self):
        return self._children

    def get_child(self, name):
        for node in self._children:
            if node.name == name:
                return node

    def get_node(self, path):
        if path in (".", ""):
            return self
        pieces = path.split("/")
        child = self.get_child(pieces[0])
        if child is None:
            return None
        return child.get_node("/".join(pieces[1:]))

    def add_child(self, node):
        self._children.append(node)

    def remove_child(self, node_or_name_or_index):
        if isinstance(node_or_name_or_index, str):
            for i, node in enumerate(self._children):
                if node.name == node_or_name_or_index:
                    self._children.pop(i)
                    return
        elif isinstance(node_or_name_or_index, int):
            self._children.pop(node_or_name_or_index)
        else:
            self._children.remove(node_or_name_or_index)

    def __str__(self):
        return "Node(%s)" % self.name

    def __repr__(self):
        return str(self)


class Tree(object):
    def __init__(self, root=None):
        self.root = root

    @classmethod
    def build(cls, nodes):
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
        ret = []
        if self.root is None:
            return ret
        for node in self.root.visit():
            ret.append(node.section)
        return ret
