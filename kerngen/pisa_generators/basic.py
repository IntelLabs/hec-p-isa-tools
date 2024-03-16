# Copyright (C) 2024 Intel Corporation

"""Module containing conversions or operations from isa to p-isa."""

from dataclasses import dataclass

from pisa_operations import Add as PisaAdd

from .highop import HighOp


@dataclass
class Add(HighOp):
    """Class representing the high-level addition operation"""

    inputs: list[str]
    output: str

    def to_pisa(self) -> list:
        """Return the p-isa equivalent of Add"""
        return [PisaAdd(self.inputs, self.output)]
