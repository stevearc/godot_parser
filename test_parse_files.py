#!/usr/bin/env python
import argparse
import os
import sys
from itertools import zip_longest

from godot_parser import parse


def _parse_and_test_file(filename: str) -> bool:
    print("Parsing %s" % filename)
    with open(filename, "r") as ifile:
        contents = ifile.read()
    try:
        data = parse(contents)
    except Exception:
        print("  Parsing error!")
        import traceback

        traceback.print_exc()
        return False
    data_lines = [l for l in str(data).split("\n") if l]
    content_lines = [l for l in contents.split("\n") if l]
    if data_lines != content_lines:
        print("  Error!")
        max_len = max([len(l) for l in content_lines])
        if max_len < 100:
            for orig, parsed in zip_longest(content_lines, data_lines, fillvalue=""):
                c = " " if orig == parsed else "x"
                print("%s <%s> %s" % (orig.ljust(max_len), c, parsed))
        else:
            for orig, parsed in zip_longest(
                content_lines, data_lines, fillvalue="----EMPTY----"
            ):
                c = "    " if orig == parsed else "XXX)"
                print("%s\n%s%s" % (orig, c, parsed))
        return False
    return True


def main():
    """Test the parsing of one tscn file or all files in directory"""
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("file_or_dir", help="Parse file or files under this directory")
    args = parser.parse_args()
    if os.path.isfile(args.file_or_dir):
        _parse_and_test_file(args.file_or_dir)
    else:
        for root, _dirs, files in os.walk(args.file_or_dir, topdown=False):
            for file in files:
                ext = os.path.splitext(file)[1]
                if ext not in [".tscn", ".tres"]:
                    continue
                filepath = os.path.join(root, file)
                if not _parse_and_test_file(filepath):
                    sys.exit(1)


if __name__ == "__main__":
    main()
