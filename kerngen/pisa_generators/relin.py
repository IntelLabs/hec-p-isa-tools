# Copyright (C) 2024 Intel Corporation

"""Module containing conversions or operations from isa to p-isa."""

from dataclasses import dataclass

from high_parser.pisa_operations import PIsaOp, Comment
from high_parser import Context, Immediate, HighOp, Polys

from .basic import Add, Mul, Muli, mixed_to_pisa_ops
from .ntt import INTT, NTT
from .mod import Mod, ModUp


@dataclass
class Relin(HighOp):
    """Class representing relinearization operation"""

    label: str
    context: Context
    output: Polys
    input0: Polys

    def to_pisa(self) -> list[PIsaOp]:
        """Return the p-isa code to perform a relinearization (relin)"""
        # Step 1: Extend basis with special primes (ModSwitchUp)
        # Step 2: Calculate something
        # Step 3: Compute delta (rounding error correction)
        # Step 4: Compute new ctxt mod Q
        # Step 5: Add to original ctxt

        inverse_t = Immediate(name="t_inverse_mod_p_0")
        inverse_p = Immediate(name="pinv_q_0")
        delta = Polys("delta", parts=2, rns=1)
        relin_key = Polys("rlk", parts=2, rns=self.context.key_rns)
        mul_by_rlk = Polys("c2_rlk", parts=2, rns=self.context.key_rns)
        input_last_part = Polys(
            "input",
            parts=self.input0.parts,
            rns=self.output.rns,
            start_parts=self.input0.parts - 1,
        )

        last_coeff = Polys.from_polys(input_last_part)
        last_coeff.name = "coeffs"
        upto_last_coeffs = Polys.from_polys(last_coeff)
        upto_last_coeffs.parts -= 1
        upto_last_coeffs.start_parts = 0

        return mixed_to_pisa_ops(
            [
                Comment("Start of relin kernel"),
                Comment("Extend base from Q to PQ"),
                ModUp(self.label, self.context, last_coeff, input_last_part),
                Comment("Multiply by relin key"),
                Mul(self.label, self.context, mul_by_rlk, upto_last_coeffs, relin_key),
                Comment("Compute delta"),
                INTT(self.label, self.context, delta, delta),
                #                Muli(self.label, self.context, delta, delta, inverse_t),
                #                Muli(self.label, self.context, delta, delta, one),
                #                Muli(self.label, self.context, coeffs, delta, r_squared),
                #               Comment("Compute new ctxt mod Q"),
                #                Mod(self.label, self.context, coeffs, coeffs),
                #                Muli(self.label, self.context, coeffs, coeffs, t),
                #                Muli(self.label, self.context, coeffs, coeffs, inverse_p),
                #                Mul(self.label, self.context, new_ctxt, coeffs, relin_key),
                #                Comment("Add to original ctxt"),
                #                Add(self.label, self.context, coeffs, coeffs, new_ctxt),
                #                Add(self.label, self.context, self.output, coeffs, self.input0),
                Comment("End of relin kernel"),
            ]
        )
