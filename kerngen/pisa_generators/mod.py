# Copyright (C) 2024 Intel Corporation

"""Module containing conversions or operations from isa to p-isa."""

from dataclasses import dataclass
from itertools import product

import high_parser.pisa_operations as pisa_op
from high_parser.pisa_operations import PIsaOp
from high_parser import Context, Immediate, ImmediateWithQ, HighOp, Polys

from .basic import Add, Muli
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
        iN = Immediate(name="iN")
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

        # Inverse NTT and multiply by inverse of t (plaintext modulus)
        input0 = Polys.from_polys(self.input0, mode="last_rns")
        output = Polys.from_polys(self.output, mode="last_rns")
        ls = [pisa_op.Comment("Start of mod kernel")]
        ls.extend(INTT(context, output, input0).to_pisa())

        units = context.units
        for part in range(self.input0.parts):
            ls.extend(
                pisa_op.Muli(
                    y(part, last_q, unit), y(part, last_q, unit), immediate.name, last_q
                )
                for immediate, unit in product((it, one), range(units))
            )

        # Drop down input rns
        input1 = Polys.from_polys(self.input0, mode="drop_last_rns")

        # TODO was ever batching required?
        ls.append(pisa_op.Comment("The NTT bit"))
        ls.extend(Muli(context, x, y, r2).to_pisa())
        ls.extend(NTT(context, x, x).to_pisa())
        ls.extend(Muli(context, x, x, t).to_pisa())
        ls.extend(Add(context, x, x, input1).to_pisa())
        ls.extend(Muli(context, self.output, x, iq).to_pisa())

        return ls
