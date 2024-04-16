# Copyright (C) 2024 Intel Corporation

"""Module containing conversions or operations from isa to p-isa."""

from copy import copy
from dataclasses import dataclass
from itertools import pairwise, product

import high_parser.pisa_operations as pisa_op
from high_parser.pisa_operations import PIsaOp
from high_parser import Context, Immediate, ImmediateWithQ, HighOp, Polys

from .basic import Add, Muli
from .ntt import NTT


# TODO need to rethink this
def butterflies_ops_single_q(
    op: pisa_op.NTT | pisa_op.INTT,
    context: Context,
    output: Polys,
    outtmp: Polys,
    input0: Polys,
    *,  # only kwargs after
    q: int,
    init_input: bool = False,
) -> list[PIsaOp]:
    """Helper to return butterflies pisa operations for NTT/INTT"""
    ntt_stages = context.ntt_stages
    ntt_stages_div_by_two = ntt_stages % 2

    stage_dst_srcs = [
        (
            (stage, outtmp, output)
            if ntt_stages_div_by_two == stage % 2
            else (stage, output, outtmp)
        )
        for stage in range(ntt_stages)
    ]

    if init_input is True:
        stage_dst_srcs[0] = (
            (0, outtmp, input0) if ntt_stages_div_by_two == 0 else (0, input0, outtmp)
        )

    return [
        op(
            ntt_stages,
            dst(part, q, unit),
            dst(part, q, next_unit),
            src(part, q, unit),
            src(part, q, next_unit),
            (q, stage, unit),
            q,
        )
        # units for omegas (aka w) taken from 16K onwards
        for part, (stage, dst, src), (unit, next_unit) in product(
            range(input0.parts),
            stage_dst_srcs,
            pairwise(range(context.units)),
        )
    ]


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
        ls = [pisa_op.Comment("Start of mod kernel")]
        ls.extend(
            butterflies_ops_single_q(
                pisa_op.INTT,
                context=context,
                output=self.output,
                outtmp=y,
                input0=self.input0,
                q=last_q,
                init_input=True,
            )
        )

        units = context.units
        for part in range(self.input0.parts):
            ls.extend(
                pisa_op.Muli(
                    y(part, last_q, unit), y(part, last_q, unit), immediate.name, last_q
                )
                for immediate, unit in product((it, one), range(units))
            )

        # Drop down input rns
        input0 = copy(self.input0)
        input0.rns -= 1

        # TODO was batching required?
        ls.append(pisa_op.Comment("The NTT bit"))
        ls.extend(Muli(context, x, y, r2).to_pisa())
        ls.extend(NTT(context, x, x).to_pisa())
        ls.extend(Muli(context, x, x, t).to_pisa())
        ls.extend(Add(context, x, x, input0).to_pisa())
        ls.extend(Muli(context, self.output, x, iq).to_pisa())

        return ls
