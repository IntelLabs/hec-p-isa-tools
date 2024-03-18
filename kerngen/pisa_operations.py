# Copyright (C) 2024 Intel Corporation

"""Module containing the low level p-isa operations"""

import itertools as it
from dataclasses import dataclass
from typing import Generator, Protocol


# TODO Required for some of the pisa command expanding
def batch(n: int, bsize: int = 0) -> Generator:
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


# TODO helper object for handling polynomial expansion
@dataclass(frozen=True)
class Polys:
    """helper object for handling polynomial expansion"""

    symbol: str
    number: int
    units: int

    def expand(self, which: int, q: int, part: int) -> str:
        """Returns a string of the expanded symbol and ..."""
        # TODO some sanity check code for bounds
        return f"{self.symbol}_{q}_{which}_{part}"


class PIsaOp(Protocol):
    """Protocol for p-isa operation"""

    def __str__(self) -> str:
        """Return the p-isa instructions of the operation"""


@dataclass
class Add(PIsaOp):
    """Class representing the p-isa addition operation"""

    inputs: list[str]
    output: str

    def __str__(self) -> str:
        """Return the p-isa instructions of an addition"""

        units = 1
        quantity = 2
        rns = 4
        rin0 = Polys("c", quantity, units)
        rin1 = Polys("d", quantity, units)
        rout = Polys("output", quantity, units)

        lines = (
            f"13, add, {rout.expand(q, o, part)}, {rin0.expand(q, o, part)}, {rin1.expand(q, o, part)}, {q}"
            for q, o, part in it.product(range(rns), range(quantity), range(units))
        )
        return "\n".join(lines)
