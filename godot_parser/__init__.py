from .files import *
from .objects import *
from .sections import *
from .tree import *


def parse(string: str) -> GDFile:
    return GDFile.parse(string)


def load(fp) -> GDFile:
    return parse(fp.read())
