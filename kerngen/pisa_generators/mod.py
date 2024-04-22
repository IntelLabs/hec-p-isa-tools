# Copyright (C) 2024 Intel Corporation

"""Module containing conversions or operations from isa to p-isa."""

from dataclasses import dataclass
from typing import Iterable

import high_parser.pisa_operations as pisa_op
from high_parser.pisa_operations import PIsaOp
from high_parser import Context, Immediate, ImmediateWithQ, HighOp, Polys

from .basic import Add, Muli
from .ntt import INTT, NTT


# TODO move this to kernel utils
def mixed_to_pisa_ops(ops: list[PIsaOp | HighOp]) -> list[PIsaOp]:
    """Transform mixed list of op types to PIsaOp only"""

    def helper(op):
        if isinstance(op, PIsaOp):
            return [op]
        return op.to_pisa()

    ops_pisa_clusters: Iterable[list[PIsaOp | HighOp]] = map(helper, ops)
    # Flattens the list returned
    return [pisa_op for pisa_ops in ops_pisa_clusters for pisa_op in pisa_ops]


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
        y = Polys("y", self.input0.parts, last_q)
        x = Polys("x", self.input0.parts, last_q)

        # Inverse NTT, multiply by inverse of t,
        # Multiply by 2n-th roots, perform NTT, multiply by t,
        # add to input, scale by inverse of q

        # TODO was ever batching required?
        # Inverse NTT and multiply by inverse of t (plaintext modulus)
        input0 = Polys.from_polys(self.input0, mode="last_rns")
        # Drop down input rns
        input1 = Polys.from_polys(self.input0, mode="drop_last_rns")
        output = Polys.from_polys(self.output, mode="last_rns")

        return mixed_to_pisa_ops(
            [
                pisa_op.Comment("Start of mod kernel"),
                INTT(context, output, input0),
                Muli(context, y, y, it),
                Muli(context, y, y, one),
                pisa_op.Comment("The NTT bit"),
                Muli(context, x, y, r2),
                NTT(context, x, x),
                Muli(context, x, x, t),
                Add(context, x, x, input1),
                Muli(context, self.output, x, iq),
            ]
        )
