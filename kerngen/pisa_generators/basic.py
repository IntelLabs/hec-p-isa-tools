# Copyright (C) 2024 Intel Corporation

"""Module containing conversions or operations from isa to p-isa."""

import itertools as it
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

    context: Context
    output: Polys
    input0: Polys
    input1: Polys

    def to_pisa(self) -> list[PIsaOp]:
        """Return the p-isa  equivalent of a Mul"""

        ls = []
        for unit, q in it.product(
            range(self.context.units), range(self.context.max_rns)
        ):
            ls.extend(
                [
                    pisa_op.Mul(
                        self.output(0, q, unit),
                        self.input0(0, q, unit),
                        self.input1(0, q, unit),
                        q,
                    ),
                    pisa_op.Mul(
                        self.output(1, q, unit),
                        self.input0(0, q, unit),
                        self.input1(1, q, unit),
                        q,
                    ),
                    pisa_op.Mac(
                        self.output(1, q, unit),
                        self.input0(1, q, unit),
                        self.input1(0, q, unit),
                        q,
                    ),
                    pisa_op.Mul(
                        self.output(2, q, unit),
                        self.input0(1, q, unit),
                        self.input1(1, q, unit),
                        q,
                    ),
                ]
            )

        return ls

    @classmethod
    def from_string(cls, context, polys_map, args_line: str):
        """Construct add operation from args string"""
        try:
            ios = (polys_map[io] for io in args_line.split())
            return cls(context, *ios)

        except ValueError as e:
            raise ValueError(f"Could not unpack command string `{args_line}`") from e
