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

        one = Immediate(name="one")
        r_squared = Immediate(name="R2")
        t = Immediate(name="t_0")
        inverse_t = Immediate(name="t_inverse_mod_p_0")
        inverse_p = Immediate(name="pinv_q_0")
        delta = Polys("delta", parts=2, rns=1)
        coeffs = Polys("coeff", parts=2, rns=self.input0.rns)
        relin_key = Polys("rlk", parts=2, rns=self.context.key_rns)
        new_ctxt = Polys("c2_rlk", parts=2, rns=self.context.key_rns)
        input_last_part = Polys(
            "input",
            parts=self.input0.parts,
            rns=self.output.rns,
            start_parts=self.input0.parts - 1,
        )
        ctxt_extended = Polys("ct", parts=2, rns=self.context.key_rns)

        return mixed_to_pisa_ops(
            [
                Comment("Extend base from Q to PQ"),
                ModUp(self.label, self.context, ctxt_extended, input_last_part),
                Comment("Compute something"),
                Muli(self.label, self.context, ctxt_extended, ctxt_extended, one),
                Muli(self.label, self.context, coeffs, ctxt_extended, r_squared),
                Comment("Compute delta"),
                INTT(self.label, self.context, delta, delta),
                Muli(self.label, self.context, delta, delta, inverse_t),
                Muli(self.label, self.context, delta, delta, one),
                Muli(self.label, self.context, coeffs, delta, r_squared),
                Comment("Compute new ctxt mod Q"),
                Mod(self.label, self.context, coeffs, coeffs),
                Muli(self.label, self.context, coeffs, coeffs, t),
                Muli(self.label, self.context, coeffs, coeffs, inverse_p),
                Mul(self.label, self.context, new_ctxt, coeffs, relin_key),
                Comment("Add to original ctxt"),
                Add(self.label, self.context, coeffs, coeffs, new_ctxt),
                Add(self.label, self.context, self.output, coeffs, self.input0),
            ]
        )
