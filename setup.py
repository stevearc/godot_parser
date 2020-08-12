""" Setup file """
import os
import re

from setuptools import find_packages, setup

HERE = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(HERE, "README.md")).read()
CHANGES = open(os.path.join(HERE, "CHANGES.md")).read()
REQUIREMENTS_TEST = open(os.path.join(HERE, "requirements_test.txt")).readlines()

REQUIREMENTS = ["pyparsing"]


if __name__ == "__main__":
    setup(
        name="godot_parser",
        version="0.1.2",
        description="Python library for parsing Godot scene files",
        long_description=README + "\n\n" + CHANGES,
        long_description_content_type="text/markdown",
        classifiers=[
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
        ],
        license="MIT",
        author="Steven Arcangeli",
        author_email="stevearc@stevearc.com",
        url="https://github.com/stevearc/godot_parser",
        keywords="godot parse parser scene",
        platforms="any",
        zip_safe=False,
        include_package_data=True,
        python_requires=">=3.6",
        packages=find_packages(exclude=("tests",)),
        install_requires=REQUIREMENTS,
        tests_require=REQUIREMENTS + REQUIREMENTS_TEST,
        test_suite="tests",
    )
