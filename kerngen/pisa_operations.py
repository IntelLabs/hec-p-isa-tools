# Copyright (C) 2024 Intel Corporation

"""Module containing the low level p-isa operations"""

from dataclasses import dataclass


@dataclass
class Add:
    """Class representing the p-isa addition operation"""

    inputs: list[str]
    output: str

    def __str__(self) -> str:
        """Return the p-isa instructions of an addition"""
        return "add TBD"
