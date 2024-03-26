# Copyright (C) 2024 Intel Corporation

"""Module containing conversions or operations from isa to p-isa for the
subtraction operation."""

import itertools as it
from dataclasses import dataclass

import pisa_operations as pisa_op
from pisa_operations import PIsaOp
from high_parser import Context
from highop import HighOp, expand_ios
from polys import Polys


@dataclass
class Sub(HighOp):
    """Class represneting the high-level subtraction operation"""

    context: Context
    output: Polys
    input0: Polys
    input1: Polys

    def to_pisa(self) -> list[PIsaOp]:
        """Return the p-isa equivalent of a Sub"""
        if self.input0.parts == self.input1.parts:
            return [
                pisa_op.Sub(*expand_io, rns)
                for expand_io, rns in expand_ios(
                    self.context, self.output, self.input0, self.input1
                )
            ]

        # Not the same number of parts
        first, second = (
            (self.input0, self.input1)
            if self.input0.parts < self.input1.parts
            else (self.input1, self.input0)
        )

        ls: list[PIsaOp] = []
        for unit, q in it.product(range(self.context.units), range(self.input0.rns)):
            ls.extend(
                pisa_op.Sub(
                    self.output(part, q, unit),
                    first(part, q, unit),
                    second(0, q, unit),
                    q,
                )
                for part in range(first.parts)
            )
            ls.extend(
                pisa_op.Copy(self.output(part, q, unit), second(part, q, unit))
                for part in range(first.parts, second.parts)
            )
        return ls
