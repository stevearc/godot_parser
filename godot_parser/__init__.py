from .files import *
from .objects import *
from .sections import *
from .structure import scene_file
from .tree import *


def parse(string: str) -> GDFile:
    return GDFile.from_parser(scene_file.parseString(string, parseAll=True))


def load(fp) -> GDFile:
    return parse(fp.read())
