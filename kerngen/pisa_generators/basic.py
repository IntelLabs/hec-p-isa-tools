# Copyright (C) 2024 Intel Corporation

"""Module containing conversions or operations from isa to p-isa."""

from dataclasses import dataclass

from expander import Expander
import pisa_operations as pisa_op
from pisa_operations import PIsaOp
from polys import Polys
from high_parser import Context
from .highop import HighOp


@dataclass
class Add(HighOp):
    """Class representing the high-level addition operation"""

    context: Context
    output: str
    inputs: list[str]

    def to_pisa(self) -> list[PIsaOp]:
        """Return the p-isa  equivalent of an Add"""

        # TODO These need to be given by Data
        parts = 2

        rout = Polys(self.output, parts, self.context)
        rin0 = Polys(self.inputs[0], parts, self.context)
        rin1 = Polys(self.inputs[1], parts, self.context)

        return Expander(self.context).cartesian(pisa_op.Add, rout, rin0, rin1)

    @classmethod
    def from_string(cls, context, args_line: str):
        """Construct add operation from args string"""
        try:
            output, *inputs = args_line.split()
            return cls(context=context, output=output, inputs=inputs)
        except ValueError as e:
            raise ValueError(f"Could not unpack command string `{args_line}`") from e
