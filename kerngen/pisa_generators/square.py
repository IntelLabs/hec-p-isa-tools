# Copyright (C) 2024 Intel Corporation

"""Module containing conversions or operations from isa to p-isa."""

import itertools as it
from dataclasses import dataclass

import pisa_operations as pisa_op
from pisa_operations import PIsaOp
from high_parser import Context
from highop import HighOp
from polys import Polys

from .basic import Copy, Mul


@dataclass
class Square(HighOp):
    """Class representing the high-level squaring operation"""

    context: Context
    output: Polys
    input0: Polys

    def to_pisa(self) -> list[PIsaOp]:
        """Return the p-isa equivalent of an Add"""
        intermediate = Polys(name="inter", parts=self.input0.parts, rns=self.input0.rns)

        copy = Copy(self.context, intermediate, self.input0)
        mul = Mul(self.context, self.output, intermediate, self.input0)

        return [*copy.to_pisa(), *mul.to_pisa()]

    @classmethod
    def from_string(cls, context, polys_map, args_line: str):
        """Construct add operation from args string"""
        try:
            ios = (polys_map[io] for io in args_line.split())
            return cls(context, *ios)

        except ValueError as e:
            raise ValueError(f"Could not unpack command string `{args_line}`") from e
