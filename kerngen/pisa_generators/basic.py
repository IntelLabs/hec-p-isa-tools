# Copyright (C) 2024 Intel Corporation

"""Module containing conversions or operations from isa to p-isa."""

from dataclasses import dataclass

from expander import Expander
import pisa_operations as pisa_op
from pisa_operations import PIsaOp
from high_parser import Context
from highop import HighOp
from polys import Polys


@dataclass
class Add(HighOp):
    """Class representing the high-level addition operation"""

    context: Context
    output: Polys
    input0: Polys
    input1: Polys

    def to_pisa(self) -> list[PIsaOp]:
        """Return the p-isa  equivalent of an Add"""
        return Expander(self.context).cartesian(
            pisa_op.Add, self.output, self.input0, self.input1
        )

    @classmethod
    def from_string(cls, context, polys_map, args_line: str):
        """Construct add operation from args string"""
        try:
            ios = (polys_map[io] for io in args_line.split())
            return cls(context, *ios)

        except ValueError as e:
            raise ValueError(f"Could not unpack command string `{args_line}`") from e


@dataclass
class Mul(HighOp):
    """Class representing the high-level multiplication operation"""


#    def to_pisa(self):
#        for q in range(self.nrns):
#            pisa_op.Mul(rout[1][q], rin0[0][q], rin1[1][q], q)
#            pisa_op.Mul(rout[0][q], rin0[0][q], rin1[0][q], q)
#            pisa_op.Mul(rout[2][q], rin0[1][q], rin1[1][q], q)
#            pisa_op.Mac(rout[1][q], rin0[1][q], rin1[0][q], q)
