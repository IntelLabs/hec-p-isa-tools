# Copyright (C) 2024 Intel Corporation

"""Module containing conversions or operations from isa to p-isa."""

from dataclasses import dataclass
from itertools import product

import high_parser.pisa_operations as pisa_op
from high_parser.pisa_operations import PIsaOp, Comment
from high_parser import KernelContext, HighOp, KeyPolys, Polys

from .basic import Add, mixed_to_pisa_ops
from .mod import Mod, ModUp


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

        ls: list[pisa_op] = []
        for digit, op in get_pisa_op(self.input1.digits):
            for part, q, unit in product(
                range(self.input0.start_parts, self.input0.parts),
                range(self.input0.start_rns, self.input0.rns),
                range(self.context.units),
            ):
                ls.append(
                    op(
                        self.context.label,
                        self.output(part, q, unit),
                        self.input0(part, q, unit),
                        self.input1(digit, part, q, unit),
                        q,
                    )
                )

        return ls


@dataclass
class Relin(HighOp):
    """Class representing relinearization operation"""

    context: KernelContext
    output: Polys
    input0: Polys

    def to_pisa(self) -> list[PIsaOp]:
        """Return the p-isa code to perform a relinearization (relin)"""
        # Step 1: Extend basis with special primes (ModSwitchUp)
        # Step 2: Calculate something
        # Step 3: Compute delta (rounding error correction)
        # Step 4: Compute new ctxt mod Q
        # Step 5: Add to original ctxt

        relin_key = KeyPolys(
            "rlk", parts=2, rns=self.context.key_rns, digits=self.input0.rns
        )
        mul_by_rlk = Polys("c2_rlk", parts=2, rns=self.context.key_rns)
        mul_by_rlk_modded_down = Polys.from_polys(mul_by_rlk)
        mul_by_rlk_modded_down.rns = self.input0.rns
        input_last_part = Polys(
            "input",
            parts=self.input0.parts,
            rns=self.output.rns,
            start_parts=self.input0.parts - 1,
        )

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
            Comment("Extend base from Q to PQ"),
            ModUp(self.context, last_coeff, input_last_part),
            Comment("Multiply by relin key"),
            KeyMul(self.context, mul_by_rlk, upto_last_coeffs, relin_key),
            Comment("Mod switch down"),
            Mod(self.context, mul_by_rlk_modded_down, mul_by_rlk),
            Comment("Add to original poly"),
            Add(self.context, self.output, mul_by_rlk_modded_down, add_original),
            Comment("End of relin kernel"),
        )
