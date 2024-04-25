# Copyright (C) 2024 Intel Corporation

"""Module containing conversions or operations from isa to p-isa."""

from dataclasses import dataclass

from high_parser.pisa_operations import PIsaOp
from high_parser import Context, HighOp, Polys

from .basic import Copy, Mul


@dataclass
class Square(HighOp):
    """Class representing the high-level squaring operation"""

    label: str
    context: Context
    output: Polys
    input0: Polys

    def to_pisa(self) -> list[PIsaOp]:
        """Return the p-isa equivalent of an Add"""
        intermediate = Polys(name="inter", parts=self.input0.parts, rns=self.input0.rns)

        copy = Copy(self.label, self.context, intermediate, self.input0)
        mul = Mul(self.label, self.context, self.output, intermediate, self.input0)

        return [*copy.to_pisa(), *mul.to_pisa()]
