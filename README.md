# Godot Parser

[![Build Status](https://travis-ci.com/stevearc/godot_parser.svg?branch=master)](https://travis-ci.com/github/stevearc/godot_parser)
[![Coverage Status](https://coveralls.io/repos/github/stevearc/godot_parser/badge.svg?branch=master)](https://coveralls.io/github/stevearc/godot_parser?branch=master)
[![Downloads](http://pepy.tech/badge/godot_parser)](https://pypi.org/pypi/godot_parser)

This is a python library for parsing Godot scene (.tscn) and resource (.tres)
files. It's intended to make it easier to automate certain aspects of editing
scene files or resources in Godot.

## High-level API
godot_parser has roughly two levels of API. The low-level API has no
Godot-specific logic and is just a dumb wrapper for the file format.

The high-level API has a bit of application logic on top to mirror Godot
functionality and make it easier to perform certain tasks. Let's look at an
example by creating a new scene file for a Player:

```python
  from godot_parser import GDScene, Node

  scene = GDScene()
  res = scene.add_ext_resource("res://PlayerSprite.png", "PackedScene")
  with scene.use_tree() as tree:
      tree.root = Node("Player", type="KinematicBody2D")
      tree.root.add_child(
          Node(
              "Sprite",
              type="Sprite",
              properties={"texture": res.reference},
          )
      )
  scene.write("Player.tscn")
```

It's much easier to use the high-level API when it's available, but it doesn't
cover everything.

## Low-level API
Let's look at creating that same Player scene with the low-level API:

```python
  from godot_parser import GDFile, ExtResource, GDSection, GDSectionHeader

  scene = GDFile(
      GDSection(GDSectionHeader("gd_scene", load_steps=2, format=2))
  )
  scene.add_section(
      GDSection(GDSectionHeader("ext_resource", path="res://PlayerSprite.png", type="PackedScene", id=1))
  )
  scene.add_section(
      GDSection(GDSectionHeader("node", name="Player", type="KinematicBody2D"))
  )
  scene.add_section(
      GDSection(
          GDSectionHeader("node", name="Sprite", type="Sprite", parent="."),
          texture=ExtResource(1)
      )
  )
  scene.write("Player.tscn")
```

You can see that this requires you to manage more of the application logic
yourself, such as resource IDs and node structure, but it can be used to create
any kind of TSCN file.

## More Examples
Here are some more examples of how you can use this library.

Find all scenes in your project with a "Sensor" node and change the
`collision_layer`:

```python
  import os
  import sys
  from godot_parser import load

  def main(project):
      for root, _dirs, files in os.walk(project):
          for file in files:
              if os.path.splitext(file)[1] == '.tscn':
                  update_collision_layer(os.path.join(root, file))

  def update_collision_layer(filepath):
      scene = load(filepath)
      updated = False
      with scene.use_tree() as tree:
          sensor = tree.get_node('Sensor')
          if sensor is not None:
              sensor['collision_layer'] = 5
              updated = True

      if updated:
          scene.write(filepath)

  main(sys.argv[1])
```

## Caveats
This was written with the help of the [Godot TSCN
docs](https://godot-es-docs.readthedocs.io/en/latest/development/file_formats/tscn.html),
but it's still mostly based on visual inspection of the Godot files I'm working
on. If you find a situation godot_parser doesn't handle or a feature it doesn't
support, file an issue with the scene file and an explanation of the desired
behavior. If you want to dig in and submit a pull request, so much the better!

If you want to run a quick sanity check for this tool, you can use the
`test_parse_files.py` script. Pass in your root Godot directory and it will
verify that it can correctly parse and re-serialize all scene and resource files
in your project.
