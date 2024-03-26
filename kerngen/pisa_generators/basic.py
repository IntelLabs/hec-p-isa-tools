# Copyright (C) 2024 Intel Corporation

"""Module containing conversions or operations from isa to p-isa."""

import itertools as it
from dataclasses import dataclass

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
        """Return the p-isa equivalent of an Add"""
        if self.input0.parts == self.input1.parts:
            expanded_ios = (
                (
                    (
                        io.expand(part, q, unit)
                        for io in (self.output, self.input0, self.input1)
                    ),
                    q,
                )
                for q, part, unit in it.product(
                    range(self.input0.rns),
                    range(self.input0.parts),
                    range(self.context.units),
                )
            )

            return [pisa_op.Add(*expand_io, rns) for expand_io, rns in expanded_ios]

        # Not the same number of parts
        first, second = (
            (self.input0, self.input1)
            if self.input0.parts < self.input1.parts
            else (self.input1, self.input0)
        )

        ls: list[PIsaOp] = []
        for unit, q in it.product(range(self.context.units), range(self.input0.rns)):
            ls.extend(
                pisa_op.Add(
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

    @classmethod
    def from_string(cls, context, polys_map, args_line: str):
        """Construct add operation from args string"""
        try:
            ios = (polys_map[io] for io in args_line.split())
            return cls(context, *ios)

        except ValueError as e:
            raise ValueError(f"Could not unpack command string `{args_line}`") from e


InIdxs = list[tuple[int, int]]


def convolution_indices(len_a, len_b) -> list[InIdxs]:
    """Helper gives convolution of parts indices"""
    # len_* is the deg + 1 of a polynomial (the vector)
    idxs: list[InIdxs] = [[] for _ in range(len_a + len_b - 1)]
    for t in it.product(range(len_a), range(len_b)):
        idxs[sum(t)].append(t)
    return idxs


@dataclass
class Mul(HighOp):
    """Class representing the high-level multiplication operation"""

    context: Context
    output: Polys
    input0: Polys
    input1: Polys

    def generate_unit(self, unit: int, q: int, out_idx: int, in_idxs: InIdxs):
        """Helper for a given unit and q generate the p-isa ops for a multiplication"""

        def get_pisa_op(num):
            yield pisa_op.Mul
            yield from (pisa_op.Mac for op in range(num - 1))

        return [
            op(
                self.output(out_idx, q, unit),
                self.input0(in0_idx, q, unit),
                self.input1(in1_idx, q, unit),
                q,
            )
            for (in0_idx, in1_idx), op in zip(in_idxs, get_pisa_op(len(in_idxs)))
        ]

    def to_pisa(self) -> list[PIsaOp]:
        """Return the p-isa  equivalent of a Mul"""

        all_idxs = convolution_indices(self.input0.parts, self.input1.parts)

        ls = []
        for unit, q in it.product(
            range(self.context.units), range(self.context.max_rns)
        ):
            for out_idx, in_idxs in enumerate(all_idxs):
                ls.extend(self.generate_unit(unit, q, out_idx, in_idxs))

        return ls

    @classmethod
    def from_string(cls, context, polys_map, args_line: str):
        """Construct add operation from args string"""
        try:
            ios = (polys_map[io] for io in args_line.split())
            return cls(context, *ios)

        except ValueError as e:
            raise ValueError(f"Could not unpack command string `{args_line}`") from e
