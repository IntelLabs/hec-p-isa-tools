# Copyright (C) 2024 Intel Corporation

"""Module containing conversions or operations from isa to p-isa."""

from dataclasses import dataclass

from pisa_operations import Add as PisaAdd

from polys import Polys
from .highop import HighOp


@dataclass
class Add(HighOp):
    """Class representing the high-level addition operation"""

    output: str
    inputs: list[str]

    def to_pisa(self) -> list:
        """Return the p-isa equivalent of Add"""

        # TODO These need to be given by Context
        units = 1
        quantity = 2
        rns = 4

        rout = Polys(self.output, quantity, units)
        rin0 = Polys(self.inputs[0], quantity, units)
        rin1 = Polys(self.inputs[1], quantity, units)

        return [PisaAdd(rout, [rin0, rin1])]
