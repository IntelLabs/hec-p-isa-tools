# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""Module containing conversions or operations from isa to p-isa."""

from dataclasses import dataclass

from high_parser.pisa_operations import PIsaOp, Comment
from high_parser import KernelContext, Immediate, HighOp, Polys

from .basic import (
    Add,
    Muli,
    mixed_to_pisa_ops,
    split_last_rns_polys,
    duplicate_polys,
    common_immediates,
    muli_last_half,
)
from .ntt import INTT, NTT


@dataclass
class Mod(HighOp):
    """Class representing mod down operation"""

    context: KernelContext
    output: Polys
    input0: Polys

    def to_pisa(self) -> list[PIsaOp]:
        """Return the p-isa code to perform an mod switch down"""
        # Immediates
        last_q = self.input0.rns - 1
        it = Immediate(name="it")
        t = Immediate(name="t", rns=last_q)
        one, r2, iq = common_immediates(r2_rns=last_q, iq_rns=last_q)

        # Drop down input rns
        input_last_rns, input_remaining_rns = split_last_rns_polys(self.input0)

        # Temp.
        temp_input_last_rns = duplicate_polys(input_last_rns, "y")
        temp_input_remaining_rns = duplicate_polys(input_remaining_rns, "x")

        # Compute the `delta_i = t * [-t^-1 * c_i] mod ql` where `i` are the parts
        # The `one` acts as a select flag as whether or not R2 the Montgomery
        # factor should be applied
        return mixed_to_pisa_ops(
            [
                Comment("Start of mod kernel"),
                Comment("Compute the delta from last rns"),
                INTT(self.context, temp_input_last_rns, input_last_rns),
                Muli(self.context, temp_input_last_rns, temp_input_last_rns, it),
                Muli(self.context, temp_input_last_rns, temp_input_last_rns, one),
                Comment("Compute the remaining rns"),
                # drop down to pisa ops to use correct rns q
                muli_last_half(
                    self.context,
                    temp_input_remaining_rns,
                    temp_input_last_rns,
                    r2,
                    input_remaining_rns,
                    last_q,
                ),
                NTT(self.context, temp_input_remaining_rns, temp_input_remaining_rns),
                Muli(
                    self.context, temp_input_remaining_rns, temp_input_remaining_rns, t
                ),
                Comment("Add the delta correction to mod down polys"),
                Add(
                    self.context,
                    temp_input_remaining_rns,
                    temp_input_remaining_rns,
                    input_remaining_rns,
                ),
                Muli(self.context, self.output, temp_input_remaining_rns, iq),
                Comment("End of mod kernel"),
            ]
        )


@dataclass
class ModUp(HighOp):
    """Class representing mod switch up operation"""

    context: KernelContext
    output: Polys
    input0: Polys

    def to_pisa(self) -> list[PIsaOp]:
        """Return the p-isa code to perform a modulus switch up (modup)"""

        one = Immediate(name="one")
        r_squared = Immediate(name="R2", rns=self.output.rns)

        # extended_poly like input_last_part will have only the last `part`
        extended_poly = Polys.from_polys(self.input0)
        extended_poly.name = "ct"

        return mixed_to_pisa_ops(
            [
                Comment("Start of modup kernel"),
                INTT(self.context, extended_poly, self.input0),
                Comment("Multiply Montgomery"),
                Muli(self.context, self.output, extended_poly, one),
                Muli(self.context, self.output, self.output, r_squared),
                Comment("Transform back to residue domain"),
                NTT(self.context, self.output, self.output),
                Comment("End of modup kernel"),
            ]
        )
