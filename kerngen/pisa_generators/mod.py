# Copyright (C) 2024 Intel Corporation

"""Module containing conversions or operations from isa to p-isa."""

from dataclasses import dataclass
from itertools import product

from high_parser.pisa_operations import PIsaOp, Comment, Muli as pisa_op_muli
from high_parser import Context, Immediate, HighOp, Polys

from .basic import Add, Muli, mixed_to_pisa_ops
from .ntt import INTT, NTT


@dataclass
class Mod(HighOp):
    """Class representing mod down operation"""

    label: str
    context: Context
    output: Polys
    input0: Polys

    def to_pisa(self) -> list[PIsaOp]:
        """Return the p-isa code to perform an mod switch down"""
        # Convenience and Immediates
        context = self.context
        last_q = self.input0.rns - 1
        it = Immediate(name="it")
        one = Immediate(name="one")
        r2 = Immediate(name="R2", rns=last_q)
        iq = Immediate(name="iq", rns=last_q)
        t = Immediate(name="t", rns=last_q)

        # Drop down input rns
        input_last_rns = Polys.from_polys(self.input0, mode="last_rns")
        input_remaining_rns = Polys.from_polys(self.input0, mode="drop_last_rns")

        # Temp.
        y = Polys(
            "y",
            input_last_rns.parts,
            input_last_rns.rns,
            start_rns=input_last_rns.start_rns,
        )
        x = Polys("x", input_remaining_rns.parts, input_remaining_rns.rns)

        # Compute the `delta_i = t * [-t^-1 * c_i] mod ql` where `i` are the parts
        # The `one` acts as a select flag as whether or not R2 the Montgomery
        # factor should be applied
        return mixed_to_pisa_ops(
            [
                Comment("Start of mod kernel"),
                Comment("Compute the delta from last rns"),
                INTT(self.label, context, y, input_last_rns),
                Muli(self.label, context, y, y, it),
                Muli(self.label, context, y, y, one),
                Comment("Compute the remaining rns"),
                # drop down to pisa ops to use correct rns q
                [
                    pisa_op_muli(
                        self.label, x(part, q, unit), y(part, last_q, unit), r2(q), q
                    )
                    for part, q, unit in product(
                        range(input_remaining_rns.parts),
                        range(input_remaining_rns.rns),
                        range(context.units),
                    )
                ],
                NTT(self.label, context, x, x),
                Muli(self.label, context, x, x, t),
                Comment("Add the delta correction to mod down polys"),
                Add(self.label, context, x, x, input_remaining_rns),
                Muli(self.label, context, self.output, x, iq),
            ]
        )


@dataclass
class ModUp(HighOp):
    """Class representing mod switch up operation"""

    label: str
    context: Context
    output: Polys
    input0: Polys

    def to_pisa(self) -> list[PIsaOp]:
        """Return the p-isa code to perform a modulus switch up (modup)"""
        coeffs = Polys("coeff", parts=2, rns=self.input0.rns)

        return mixed_to_pisa_ops(
            [
                Comment("Start of modup kernel"),
                INTT(self.label, self.context, coeffs, self.input0),
                NTT(self.label, self.context, self.output, coeffs),
            ]
        )
