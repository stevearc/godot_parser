from io import BufferedReader

from .objects import *
from .sections import *
from .structure import scene_file


def parse(string: str) -> GDFile:
    return GDFile.from_parser(scene_file.parseString(string, parseAll=True))


def load(fp: BufferedReader) -> GDFile:
    return parse(fp.read().decode("utf8"))
