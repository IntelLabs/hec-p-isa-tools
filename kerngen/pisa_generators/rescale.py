# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

# Copyright (C) 2024 Intel Corporation

"""Module containing conversions or operations from isa to p-isa."""

from dataclasses import dataclass
from itertools import product

from high_parser.pisa_operations import PIsaOp, Comment
from high_parser.pisa_operations import Sub as pisa_op_sub
from high_parser.pisa_operations import Add as pisa_op_add

from high_parser import KernelContext, Immediate, HighOp, Polys

from .basic import Muli, mixed_to_pisa_ops
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
        one = Immediate(name="one")
        r2 = Immediate(name="R2", rns=last_q)
        iq = Immediate(name="iq", rns=last_q)
        q_last_half = Polys("qLastHalf", 1, self.input0.rns)
        q_i_last_half = Polys("qiLastHalf", 1, rns=last_q)

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
                Comment("Start of Rescale kernel."),
                INTT(context, y, input_last_rns),
                Muli(context, y, y, one),
                [
                    pisa_op_add(
                        self.context.label,
                        y(part, last_q, unit),
                        y(part, last_q, unit),
                        q_last_half(0, last_q, unit),
                        last_q,
                    )
                    for part, q, unit in product(
                        range(input_remaining_rns.parts),
                        range(input_remaining_rns.rns),
                        range(context.units),
                    )
                ],
                [
                    pisa_op_sub(
                        self.context.label,
                        x(part, q, unit),
                        y(part, last_q, unit),
                        q_i_last_half(0, q, unit),
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
                        self.input0(part, q, unit),
                        x(part, q, unit),
                        q,
                    )
                    for part, q, unit in product(
                        range(input_remaining_rns.parts),
                        range(input_remaining_rns.rns),
                        range(context.units),
                    )
                ],
                Muli(context, self.output, x, iq),
                Comment("End of Rescale kernel."),
            ]
<<<<<<< HEAD
            )
=======
        )
>>>>>>> 2e51ccc (initial working version of rescale. Confirmed working for 16-128K poly order.)
