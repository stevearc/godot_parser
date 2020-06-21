from .files import *
from .objects import *
from .sections import *
from .tree import *

__version__ = "0.1"


def parse(string: str) -> GDFile:
    return GDFile.parse(string)


def load(fp) -> GDFile:
    return parse(fp.read())
