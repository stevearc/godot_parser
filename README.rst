Godot Parser
============
:Build: |build|_ |coverage|_
:Documentation: |docs|_
:PyPI: |downloads|_

.. |build| image:: https://travis-ci.com/stevearc/godot_parser.png?branch=master
.. _build: https://travis-ci.com/stevearc/godot_parser
.. |coverage| image:: https://coveralls.io/repos/stevearc/godot_parser/badge.png?branch=master
.. _coverage: https://coveralls.io/r/stevearc/godot_parser?branch=master
.. |downloads| image:: http://pepy.tech/badge/godot_parser
.. _downloads: https://pypi.org/pypi/godot_parser

This is a python library for parsing Godot scene (.tscn) and resource (.tres) files. It's not quite ready yet, but the basic usage looks like this:

::

  from godot_parser import load

  with open('Main.tscn', 'r') as ifile:
    scene = load(ifile)

  print(scene)


I've been testing this by running ``./test_parse_files.py <project>``. If it prints
any errors, then there's either a problem with parsing or a problem with
serialization.
