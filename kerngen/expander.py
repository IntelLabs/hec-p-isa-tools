# Copyright (C) 2024 Intel Corporation

"""Module for expanders to exapnd p-isa symbols in common patterns"""

import itertools as it

from pisa_operations import PIsaOp


class Expander:
    """A class providing several expanders based on a given context"""

    def __init__(self, context):
        self.context = context

    def cartesian(self, command_cls, *ios) -> list[PIsaOp]:
        """Cartesian expansion"""
        rns = self.context.max_rns
        # TODO hardcoding needs removal
        parts = 2
        units = self.context.units
        expanded_ios = (
            ((io.expand(part, q, unit) for io in ios), q)
            for q, part, unit in it.product(range(rns), range(parts), range(units))
        )

        return [command_cls(*expand_io, rns) for expand_io, rns in expanded_ios]


# TODO Required for some of the pisa command expanding
def batch(n: int, bsize: int = 0):
    """
    return a generator of pairs of indices that will be used typically for NTT batching
    `n` slices will end at n and `bsize` batch size
    """
    UNIT_SIZE = 13
    NUNITS = 8
    N = 8192
    batch_size = 8 if N <= (UNIT_SIZE << 1) else max(1, 8 // NUNITS)
    b = batch_size if bsize == 0 else bsize
    nq, nr = divmod(n, b)
    us = range(nq + 1)
    ibs = (nr if u == nq else b for u in us)
    return ((u * b, u * b + ib) for u, ib in zip(us, ibs))
