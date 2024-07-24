# Copyright (C) 2024 Intel Corporation

"""Module containing conversions or operations from isa to p-isa."""

from dataclasses import dataclass
from itertools import product

from high_parser.pisa_operations import PIsaOp, Comment, Sub
from high_parser.pisa_operations import Muli as pisa_op_muli
from high_parser.pisa_operations import Sub as pisa_op_sub

from high_parser import KernelContext, Immediate, HighOp, Polys

from .basic import Add, Muli, mixed_to_pisa_ops
from .ntt import INTT, NTT


@dataclass
class Rescale(HighOp):
    """Class representing mod down operation"""

    context: KernelContext
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
        qLastHalf = Polys("qLastHalf", 1, self.input0.rns)
        qiLastHalf = Immediate(name="qiLastHalf", rns=last_q)

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
                INTT(context, y, input_last_rns),
                Muli(context, y, y, one),
                Add(context, y, y, qLastHalf),
                [
                    pisa_op_sub(
                        self.context.label,
                        x(part, q, unit),
                        y(part, last_q, unit),
                        qiLastHalf(part, q, unit),
                        q,
                    )
                    for part, q, unit in product(
                        range(input_remaining_rns.parts),
                        range(input_remaining_rns.rns),
                        range(context.units),
                    )
                ],
                Muli(context, x, x, r2),
                NTT(context, x, x),
                [
                    pisa_op_sub(
                        self.context.label,
                        x(part, q, unit),
                        self.input0(part, last_q, unit),
                        x(part, q, unit),
                        q,
                    )
                    for part, q, unit in product(
                        range(input_remaining_rns.parts),
                        range(input_remaining_rns.rns),
                        range(context.units),
                    )
                ],
                Muli(context, self.output, x, iq)
            ]
            )