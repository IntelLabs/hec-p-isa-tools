# Copyright (C) 2024 Intel Corporation

"""Module for parsing isa data components"""

from typing import NamedTuple


class Data(NamedTuple):
    """Class representing a data type with related attributes"""

    name: str

    @classmethod
    def from_string(cls, name: str):
        """Construct data from a string"""
        return cls(name=name)
