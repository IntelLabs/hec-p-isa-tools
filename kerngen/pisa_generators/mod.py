# Copyright (C) 2024 Intel Corporation

"""Module containing conversions or operations from isa to p-isa."""

from dataclasses import dataclass
import itertools as it

import high_parser.pisa_operations as pisa_op
from high_parser.pisa_operations import PIsaOp
from high_parser import Context, Immediate, HighOp, Polys

from .basic import Mul, Muli
from .ntt import NTT, INTT


def batch(batch_size, n):
    """Batch. Return tuple."""
    nq, nr = divmod(n, batch_size)
    yield from (
        (u, v) for u, v in it.pairwise(range(0, nq * batch_size + 1, batch_size))
    )
    if nr != 0:
        u = nq * batch_size
        yield (u, u + nr)


@dataclass
class Mod(HighOp):
    """Class representing mod down operation"""

    context: Context
    output: Polys
    input0: Polys

    def to_pisa(self) -> list[PIsaOp]:
        """Return the p-isa code to perform an mod switch down"""
        od = self.order
        q = list(range(self.nrns))
        last_q = self.nrns - 1

        # Old comment: Defining registers
        # TODO not passed in?
        ipsi = Polys(f"ipsi_{last_q}", ..., 0)
        psi = Polys("psi", last_q, 0)
        # Temporary registers to hold results of transforming (e.g. iNTT) the last RNS term
        last_inp_inv = ["y1", "y2"]
        # Temporary registers to hold a batch of results that are finally put in the output
        out_interim = [f"x{self.batch_size}", "x2"]

        # Defining immediates
        iN = Immediate(name="iN")
        it = Immediate(name="it")
        one = Immediate(name="one")
        r2 = [Immediate(name=f"R2_{m}") for m in range(last_q)]
        t = [Immediate(name=f"t_{m}") for m in range(last_q)]
        iq = [Immediate(name=f"iq_{m}") for m in range(last_q)]

        # Prep for inverse NTT of the last RNS input
        intt_inp = [rinp[o][last_q] for o in range(od)]
        intt_psi = [ripsi for _ in range(od)]
        last_inp_inv_ext = [last_inp_inv[0][0] for _ in range(last_q)]

        # Inverse NTT, multiply by inverse of t,
        # Multiply by 2n-th roots, perform NTT, multiply by t,
        # add to input, scale by inverse of q
        ls: list[PIsaOp] = []
        for o in range(od):
            # Inverse NTT & Multiply by inverse of t
            ls.append(INTT(last_inp_inv, [intt_inp[o]], intt_psi, iN, q1))
            ls.append(Muli(last_inp_inv[0], last_inp_inv[0], it, q1))
            ls.append(Muli(last_inp_inv[0], last_inp_inv[0], one, q1))
            for s in self.batch(last_q):
                ls.append(Muli(out_interim[0], last_inp_inv_ext[s], r2[s], q[s]))
                ls.append(NTT(out_interim, out_interim[0], rpsi[s], q[s]))
                ls.append(Muli(out_interim[0], out_interim[0], t[s], q[s]))
                ls.append(Add(out_interim[0], out_interim[0], rinp[o][s], q[s]))
                ls.append(Muli(rout[o][s], out_interim[0], iq[s], q[s]))

        # TODO Needs flattening
        return [e.to_pisa() for e in ls]
