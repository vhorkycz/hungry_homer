#!/usr/bin/env python3

"""
Installation script for hungry_homer.
"""

from setuptools import setup, find_packages
import os

install_requires=[
        "enum34;python_version<'3.4'",
        "pywin32 >= 1.0;platform_system=='Windows'"
    ]


def main():
    setup(
        name="Hungry Homer",
        version="1.0",
        packages=find_packages(),
        package_data={"hungry_homer": [
            os.path.join("resources_dir", "*"),
            os.path.join("level_maps", "*")
            ]},
        install_requires=[
            "pyglet>=1.5.7",
            "importlib-resources;python_version<'3.7'"
            ],
        entry_points={
            "gui_scripts": ["hungry_homer=hungry_homer.__main__:main"],
        },
        author="Václav Horký",
        author_email="vacl@vhorky.cz",
        description="game inspired by Hungry Horace",
        keywords="game",
        url="https://github.com/vhorkycz/hungry_homer",
    )

if __name__ == "__main__":
    main()
