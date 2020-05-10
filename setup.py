# -*- coding: utf-8 -*-
from setuptools import setup

from logcraft import __VERSION__


def get_long_description():
    with open("README.md") as f:
        long_description = f.read()
    return long_description


def setup_package():
    _classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Logging",
        "License :: OSI Approved :: MIT License"
    ]

    setup(
        name="logcraft",
        version=__VERSION__,
        author="Ryan Lyn",
        author_email="",
        description="Python Macro-Generated Logging from Comments",
        long_description=get_long_description(),
        long_description_content_type='text/markdown',
        url="https://github.com/ryanlyn/logcraft",
        packages=["logcraft"],
        platforms='any',
        classifiers=_classifiers,
        license="MIT License",
        keywords=["logging", "macro"]
    )
    return None


if __name__ == "__main__":
    setup_package()
