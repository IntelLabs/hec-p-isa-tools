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

from .basic import Muli, mixed_to_pisa_ops, Sub, split_last_rns_polys, duplicate_polys
from .ntt import INTT, NTT


@dataclass
class Rescale(HighOp):
    """Class representing mod down operation"""

    context: KernelContext
    output: Polys
    input0: Polys

    @dataclass
    class PartialOpOptions:
        """Optional arguments for partial_op helper function"""

        output_last_q: bool = False
        input0_last_q: bool = False
        input1_last_q: bool = False
        input1_first_part: bool = False
        op_last_q: bool = False

    @dataclass
    class PartialOpPolys:
        """Polynomials used in partial ops"""

        output: Polys
        input0: Polys
        input1: Polys
        input_remaining_rns: Polys

    def partial_op(
        self,
        op,
        polys: PartialOpPolys,
        options: PartialOpOptions,
    ):
        """ "A helper function to perform partial operation, such as add/sub on last half (input1) to all of input0"""
        last_q = self.input0.rns - 1
        return [
            op(
                self.context.label,
                polys.output(part, last_q if options.output_last_q else q, unit),
                polys.input0(part, last_q if options.input0_last_q else q, unit),
                polys.input1(
                    0 if options.input1_first_part else part,
                    last_q if options.input1_last_q else q,
                    unit,
                ),
                last_q if options.op_last_q else q,
            )
            for part, q, unit in product(
                range(polys.input_remaining_rns.parts),
                range(polys.input_remaining_rns.rns),
                range(self.context.units),
            )
        ]

    def add_last_half(self, output, input0, input1, input_remaining_rns):
        """Add input0 to input1 (first part)"""
        return self.partial_op(
            pisa_op_add,
            self.PartialOpPolys(output, input0, input1, input_remaining_rns),
            self.PartialOpOptions(
                output_last_q=True,
                input0_last_q=True,
                input1_last_q=True,
                input1_first_part=True,
                op_last_q=True,
            ),
        )

    def sub_last_half(self, output, input0, input1, input_remaining_rns):
        """Subtract input1 (first part) with input0 (last RNS)"""
        return self.partial_op(
            pisa_op_sub,
            self.PartialOpPolys(output, input0, input1, input_remaining_rns),
            self.PartialOpOptions(input0_last_q=True, input1_first_part=True),
        )

    def to_pisa(self) -> list[PIsaOp]:
        """Return the p-isa code to perform an mod switch down"""
        # Convenience and Immediates
        context = self.context
        last_q = self.input0.rns - 1

        # <common 1>
        one = Immediate(name="one")
        r2 = Immediate(name="R2", rns=last_q)
        iq = Immediate(name="iq", rns=last_q)
        # </common 1>
        q_last_half = Polys("qLastHalf", 1, self.input0.rns)
        q_i_last_half = Polys("qiLastHalf", 1, rns=last_q)

        # <common 2>
        # Drop down input rns
        input_last_rns, input_remaining_rns = split_last_rns_polys(self.input0)
        # Temp.
        y = duplicate_polys(input_last_rns, "y")
        x = duplicate_polys(input_remaining_rns, "x")

        # Compute the `delta_i = t * [-t^-1 * c_i] mod ql` where `i` are the parts
        # The `one` acts as a select flag as whether or not R2 the Montgomery
        # factor should be applied
        return mixed_to_pisa_ops(
            [
                Comment("Start of Rescale kernel."),
                INTT(context, y, input_last_rns),
                Muli(context, y, y, one),
                Comment("Add the last part of the input to y"),
                self.add_last_half(y, y, q_last_half, input_remaining_rns),
                Comment("Subtract q_i (last half/last rns) from y"),
                self.sub_last_half(x, y, q_i_last_half, input_remaining_rns),
                Muli(context, x, x, r2),
                NTT(context, x, x),
                Sub(context, x, Polys.from_polys(self.input0, mode="drop_last_rns"), x),
                Muli(context, self.output, x, iq),
                Comment("End of Rescale kernel."),
            ]
<<<<<<< HEAD
            )
=======
        )
>>>>>>> 2e51ccc (initial working version of rescale. Confirmed working for 16-128K poly order.)
