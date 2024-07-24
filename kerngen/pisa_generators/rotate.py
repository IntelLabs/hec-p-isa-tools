# Copyright (C) 2024 Intel Corporation

"""Module containing conversions or operations from isa to p-isa."""

from dataclasses import dataclass
from itertools import product

from high_parser.pisa_operations import PIsaOp, Comment
from high_parser import KernelContext, HighOp, Polys, KeyPolys

from .basic import Add, mixed_to_pisa_ops
from .relin import KeyMul, DigitDecompExtend
from .mod import Mod
from .ntt import INTT, NTT

@dataclass
class Rotate(HighOp):
    """Class representing rotate operation"""

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
            Comment("Start of rotate kernel - similar to relin, except missing final add"),
            DigitDecompExtend(self.context, last_coeff, input_last_part),
            Comment("Multiply by rotate key"),
            KeyMul(self.context, mul_by_rlk, upto_last_coeffs, relin_key),
            Comment("Mod switch down to Q"),
            Mod(self.context, mul_by_rlk_modded_down, mul_by_rlk),
            Comment("Start of new code for rotate"),
            INTT(self.context, mul_by_rlk_modded_down, add_original),
            NTT(self.context, mul_by_rlk_modded_down, mul_by_rlk_modded_down),
            Add(self.context, self.output, mul_by_rlk_modded_down, add_original),
            Comment("End of rotate kernel")
        )


        