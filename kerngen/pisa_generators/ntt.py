# Copyright (C) 2024 Intel Corporation

"""Module containing conversions or operations from isa to p-isa."""

from dataclasses import dataclass

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
        ls = []
        for stage in range(ntt_stages):
            dst, src = (
                (outtmp, self.output)
                if ntt_stages % 2 == stage % 2
                else (self.output, outtmp)
            )
            for q in range(self.input0.rns):
                ls.append("Filler")
        #                PIsaOp.NTT(ntt_stages, dst(j), src., stage, q)

        return [*mul.to_pisa(), *ls]


@dataclass
class INTT(HighOp):
    """Class representing the INTT"""

    def to_pisa(self) -> list[PIsaOp]:
        """Return the p-isa code to perform an INTT"""
        return []
