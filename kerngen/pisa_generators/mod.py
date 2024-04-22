# Copyright (C) 2024 Intel Corporation

"""Module containing conversions or operations from isa to p-isa."""

from dataclasses import dataclass

from high_parser.pisa_operations import PIsaOp, Comment
from high_parser import Context, Immediate, ImmediateWithQ, HighOp, Polys

from .basic import Add, Muli, mixed_to_pisa_ops
from .ntt import INTT, NTT


@dataclass
class Mod(HighOp):
    """Class representing mod down operation"""

    context: Context
    output: Polys
    input0: Polys

    def to_pisa(self) -> list[PIsaOp]:
        """Return the p-isa code to perform an mod switch down"""
        context = self.context
        last_q = self.input0.rns - 1

        # Defining immediates
        it = Immediate(name="it")
        one = Immediate(name="one")
        r2 = ImmediateWithQ(name="R2", rns=last_q)
        iq = ImmediateWithQ(name="iq", rns=last_q)
        t = ImmediateWithQ(name="t", rns=last_q)

        # Temp.
        y = Polys.from_polys(self.input0, mode="last_rns")
        y.name = "y"
        x = Polys("x", self.input0.parts, last_q)

        # Compute the `delta_i = t * [-t^-1 * c_i] mod ql` where `i` are the parts
        # The `one` acts as a select flag as whether or not R2 the Montgomery factor should be applied

        input0 = Polys.from_polys(self.input0, mode="last_rns")
        # Drop down input rns
        input1 = Polys.from_polys(self.input0, mode="drop_last_rns")

        return mixed_to_pisa_ops(
            [
                Comment("Start of mod kernel"),
                Comment("Compute the delta from last rns"),
                INTT(context, y, input0),
                Muli(context, y, y, it),
                Muli(context, y, y, one),
                Comment("Compute the remaining rns"),
                Muli(context, x, y, r2),
                NTT(context, x, x),
                Muli(context, x, x, t),
                Comment("Add the delta correction to mod down polys"),
                Add(context, x, x, input1),
                Muli(context, self.output, x, iq),
            ]
        )
