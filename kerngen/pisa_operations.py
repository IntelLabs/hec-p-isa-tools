# Copyright (C) 2024 Intel Corporation

"""Module containing the low level p-isa operations"""

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


class PIsaOp(Protocol):
    """Protocol for p-isa operation"""

    def __str__(self) -> str:
        """Return the p-isa instructions of the operation"""


@dataclass
class Add(PIsaOp):
    """Class representing the p-isa addition operation"""

    output: str
    input0: str
    input1: str
    q: str

    def __str__(self) -> str:
        """Return the p-isa instructions of an addition"""

        return f"13, add, {self.output}, {self.input0}, {self.input1}, {self.q}"
