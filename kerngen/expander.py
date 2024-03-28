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
def batch(batch_size, n):
    """Batch. Return tuple."""
    nq, nr = divmod(n, batch_size)
    yield from (
        (u, v) for u, v in it.pairwise(range(0, nq * batch_size + 1, batch_size))
    )
    if nr != 0:
        u = nq * batch_size
        yield (u, u + nr)
