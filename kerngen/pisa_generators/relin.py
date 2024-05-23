# Copyright (C) 2024 Intel Corporation

"""Module containing conversions or operations from isa to p-isa."""

from dataclasses import dataclass
from itertools import product

import high_parser.pisa_operations as pisa_op
from high_parser.pisa_operations import PIsaOp, Comment
from high_parser import KernelContext, HighOp, Immediate, KeyPolys, Polys

from .basic import Add, Muli, mixed_to_pisa_ops
from .mod import Mod
from .ntt import INTT, NTT


@dataclass
class KeyMul(HighOp):
    """Class representing a key multiplication operation"""

    context: KernelContext
    output: Polys
    input0: Polys
    input1: KeyPolys

    def to_pisa(self) -> list[PIsaOp]:
        """Return the p-isa code to perform a key multiplication"""

        def get_pisa_op(num):
            yield 0, pisa_op.Mul
            yield from ((op, pisa_op.Mac) for op in range(1, num))

        return [
            op(
                self.context.label,
                self.output(part, q, unit),
                self.input0(part, q, unit),
                self.input1(digit, part, q, unit),
                q,
            )
            for digit, op in get_pisa_op(self.input1.digits)
            for part, q, unit in product(
                range(self.input1.start_parts, self.input1.parts),
                range(self.input0.start_rns, self.input0.rns),
                range(self.context.units),
            )
        ]


@dataclass
class DigitDecompExtend(HighOp):
    """Class representing Digit decomposition and base extension"""

    context: KernelContext
    output: Polys
    input0: Polys

    def to_pisa(self) -> list[PIsaOp]:
        """Return the p-isa code performing Digit decomposition followed by
        base extension"""

        rns_poly = Polys.from_polys(self.input0)
        rns_poly.name = "ct"

        one = Immediate(name="one")
        r2 = Immediate(name="R2", rns=self.context.key_rns)

        ls: list[pisa_op] = []
        for _ in range(self.input0.rns):
            ls.extend(
                pisa_op.Muli(
                    self.context.label,
                    self.output(part, pq, unit),
                    self.output(part, pq, unit),
                    r2(part, pq, unit),
                    pq,
                )
                for part, pq, unit in product(
                    range(self.input0.start_parts, self.input0.parts),
                    range(self.context.key_rns),
                    range(self.context.units),
                )
            )
            ls.extend(NTT(self.context, self.output, self.output).to_pisa())

        return mixed_to_pisa_ops(
            INTT(self.context, rns_poly, self.input0),
            Muli(self.context, self.output, rns_poly, one),
            ls,
        )


@dataclass
class Relin(HighOp):
    """Class representing relinearization operation"""

    context: KernelContext
    output: Polys
    input0: Polys

    def to_pisa(self) -> list[PIsaOp]:
        """Return the p-isa code to perform a relinearization (relin). Note:
        currently only supports polynomials with two parts. Currently only
        supports number of digits equal to the RNS size"""

        relin_key = KeyPolys(
            "rlk", parts=2, rns=self.context.key_rns, digits=self.input0.rns
        )
        mul_by_rlk = Polys("c2_rlk", parts=2, rns=self.context.key_rns)
        mul_by_rlk_modded_down = Polys.from_polys(mul_by_rlk)
        mul_by_rlk_modded_down.rns = self.input0.rns
        input_last_part = Polys.from_polys(self.input0, mode="last_part")
        input_last_part.name = "input"

        last_coeff = Polys.from_polys(input_last_part)
        last_coeff.name = "coeffs"
        last_coeff.rns = self.context.key_rns
        upto_last_coeffs = Polys.from_polys(last_coeff)
        upto_last_coeffs.parts = 1
        upto_last_coeffs.start_parts = 0

        add_original = Polys.from_polys(mul_by_rlk_modded_down)
        add_original.name = self.input0.name

        return mixed_to_pisa_ops(
            Comment("Start of relin kernel"),
            Comment("Digit decomposition and extend base from Q to PQ"),
            DigitDecompExtend(self.context, last_coeff, input_last_part),
            Comment("Multiply by relin key"),
            KeyMul(self.context, mul_by_rlk, upto_last_coeffs, relin_key),
            Comment("Mod switch down to Q"),
            Mod(self.context, mul_by_rlk_modded_down, mul_by_rlk),
            Comment("Add to original poly"),
            Add(self.context, self.output, mul_by_rlk_modded_down, add_original),
            Comment("End of relin kernel"),
        )
