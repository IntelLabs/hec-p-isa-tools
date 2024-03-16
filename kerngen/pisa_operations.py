# Copyright (C) 2024 Intel Corporation

"""Module containing the low level p-isa operations"""

from dataclasses import dataclass
from typing import Generator


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

    def expand(self) -> str:
        """Returns a string of the expanded symbol and ..."""
        return ""


@dataclass
class Add:
    """Class representing the p-isa addition operation"""

    inputs: list[str]
    output: str

    def __str__(self) -> str:
        """Return the p-isa instructions of an addition"""
        return "add TBD"
