# Copyright (C) 2024 Intel Corporation

"""Module containing conversions or operations from isa to p-isa."""

from dataclasses import dataclass
import itertools as it

import high_parser.pisa_operations as pisa_op
from high_parser.pisa_operations import PIsaOp
from high_parser.parser import Context
from high_parser.highop import HighOp
from high_parser.polys import Polys

from .basic import Mul


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

        # Essentially a scalar mul since psi 1 part
        mul = Mul(self.context, self.output, self.input0, psi)

        outtmp = Polys("outtmp", self.output.parts, self.output.rns)

        ntt_stages = self.context.ntt_stages
        ntt_stages_div_by_two = ntt_stages % 2

        stage_dst_srcs = (
            (
                (stage, outtmp, self.output)
                if ntt_stages_div_by_two == stage % 2
                else (stage, self.output, outtmp)
            )
            for stage in range(ntt_stages)
        )

        ntts = [
            pisa_op.NTT(
                ntt_stages,
                dst(part, q, unit),
                dst(part, q, next_unit),
                src(part, q, unit),
                src(part, q, next_unit),
                (q, stage, unit),
                q,
            )
            # units for omegas (aka w) taken from 16K onwards
            for part, (stage, dst, src), q, (unit, next_unit) in it.product(
                range(self.input0.parts),
                stage_dst_srcs,
                range(self.input0.rns),
                it.pairwise(range(self.context.units)),
            )
        ]

        return [*mul.to_pisa(), *ntts]


@dataclass
class INTT(HighOp):
    """Class representing the INTT"""

    def to_pisa(self) -> list[PIsaOp]:
        """Return the p-isa code to perform an INTT"""
        return []
