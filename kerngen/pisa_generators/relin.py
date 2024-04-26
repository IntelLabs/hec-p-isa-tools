# Copyright (C) 2024 Intel Corporation

"""Module containing conversions or operations from isa to p-isa."""

from dataclasses import dataclass

from high_parser.pisa_operations import PIsaOp, Comment, Muli as pisa_op_muli
from high_parser import Context, Immediate, HighOp, Polys

from .basic import Add, Muli, mixed_to_pisa_ops
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
        coeffs = Polys("coeff", parts=2, rns=self.input0.rns)
        relin_key = Polys("rlk", parts=2, rns=self.input0.rns)

        return mixed_to_pisa_ops(
            [
                Comment("Extend base from Q to PQ"),
                ModUp(self.label, self.context, self.output, self.input0),
                Comment("Compute something"),
                Muli(self.label, self.context, self.output, self.output, one),
                Comment("Compute delta"),
                NTT(self.label, self.context, coeffs, coeffs),
                Comment("Compute new ctxt mod Q"),
                Comment("Add to original ctxt"),
            ]
        )
