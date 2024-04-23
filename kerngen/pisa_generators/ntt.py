# Copyright (C) 2024 Intel Corporation

"""Module containing conversions or operations from isa to p-isa."""

from dataclasses import dataclass
import itertools as it

import high_parser.pisa_operations as pisa_op
from high_parser.pisa_operations import PIsaOp
from high_parser import Context, Immediate, HighOp, Polys

from .basic import Mul, Muli


def butterflies_ops(
    op: pisa_op.NTT | pisa_op.INTT,
    context: Context,
    output: Polys,
    outtmp: Polys,
    input0: Polys,
    *,  # kwargs after
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
            stage,
            unit,
            q,
        )
        # units for omegas (aka w) taken from 16K onwards
        for part, (stage, dst, src), q, (unit, next_unit) in it.product(
            range(input0.parts),
            stage_dst_srcs,
            range(input0.rns),
            it.pairwise(range(context.units)),
        )
    ]


@dataclass
class NTT(HighOp):
    """Class representing the NTT"""

    context: Context
    output: Polys
    input0: Polys

    def to_pisa(self) -> list[PIsaOp]:
        """Return the p-isa code to perform an NTT"""
        # TODO Is this passed in?
        psi = Polys("psi", parts=1, rns=self.input0.rns)
        # TODO We need to decide whether output symbols need to be defined
        outtmp = Polys("outtmp", self.output.parts, self.output.rns)

        # Essentially a scalar mul since psi 1 part
        mul = Mul(self.context, self.output, self.input0, psi)

        butterflies = butterflies_ops(
            pisa_op.NTT,
            context=self.context,
            output=self.output,
            outtmp=outtmp,
            input0=self.input0,
        )

        return [*mul.to_pisa(), *butterflies]


@dataclass
class INTT(HighOp):
    """Class representing the INTT"""

    context: Context
    output: Polys
    input0: Polys

    def to_pisa(self) -> list[PIsaOp]:
        """Return the p-isa code to perform an INTT"""
        # TODO Is this passed in?
        ipsi = Polys("ipsi", parts=1, rns=self.input0.rns)
        # TODO We need to decide whether output symbols need to be defined
        outtmp = Polys("outtmp", self.output.parts, self.output.rns)
        iN = Immediate(name="iN")

        butterflies = butterflies_ops(
            pisa_op.INTT,
            context=self.context,
            output=self.output,
            outtmp=outtmp,
            input0=self.input0,
            init_input=True,
        )

        # Essentially a scalar mul since ipsi 1 part
        mul = Mul(self.context, self.output, self.output, ipsi)
        muli = Muli(self.context, self.output, self.output, iN)

        return [*butterflies, *mul.to_pisa(), *muli.to_pisa()]
