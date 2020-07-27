""" Utils """
import os
from typing import Optional


def stringify_object(value):
    """ Serialize a value to the godot file format """
    if value is None:
        return "null"
    elif isinstance(value, str):
        return '"' + value + '"'
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, dict):
        return (
            "{\n"
            + ",\n".join(
                ['"%s": %s' % (k, stringify_object(v)) for k, v in value.items()]
            )
            + "\n}"
        )
    elif isinstance(value, list):
        return "[ " + ", ".join([stringify_object(v) for v in value]) + " ]"
    else:
        return str(value)


def find_project_root(start: str) -> Optional[str]:
    curdir = start
    if os.path.isfile(start):
        curdir = os.path.dirname(start)
    while True:
        if os.path.isfile(os.path.join(curdir, "project.godot")):
            return curdir
        next_dir = os.path.realpath(os.path.join(curdir, os.pardir))
        if next_dir == curdir:
            return None
        curdir = next_dir


def gdpath_to_filepath(root: str, path: str) -> str:
    if not path.startswith("res://"):
        raise ValueError("'%s' is not a godot resource path" % path)
    pieces = path[6:].split("/")
    return os.path.join(root, *pieces)


def filepath_to_gdpath(root: str, path: str) -> str:
    return "res://" + os.path.relpath(path, root).replace("\\", "/")


def is_gd_path(path: str) -> bool:
    return path.startswith("res://")
