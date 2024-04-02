# Copyright (C) 2024 Intel Corporation

"""Module containing the low level p-isa operations"""

from dataclasses import dataclass
from typing import Protocol


class PIsaOp(Protocol):
    """Protocol for p-isa operation"""

    def __str__(self) -> str:
        """Return the p-isa instructions of the operation"""


@dataclass
class UnaryOp:
    """Class representing the p-isa common unary operation"""

    output: str
    input0: str
    q: str

    def _op_str(self, op: str) -> str:
        """Return the p-isa instructions of an addition"""

        return f"13, {op}, {self.output}, {self.input0}, {self.q}"


@dataclass
class BinaryOp:
    """Class representing the p-isa common binary operation"""

    output: str
    input0: str
    input1: str
    q: str

    def _op_str(self, op: str) -> str:
        """Return the p-isa instructions of operation `op`"""

        return f"13, {op}, {self.output}, {self.input0}, {self.input1}, {self.q}"


@dataclass
class Copy(PIsaOp):
    """Class representing the p-isa movement operation"""

    output: str
    input0: str
    # No q required

    def __str__(self) -> str:
        """Return the p-isa instructions of an movement"""
        return f"13, copy, {self.output}, {self.input0}"


@dataclass
class Mov(PIsaOp):
    """Class representing the p-isa movement operation"""

    output: str
    input0: str
    # No q required

    def __str__(self) -> str:
        """Return the p-isa instructions of an movement"""
        return f"13, move, {self.output}, {self.input0}"


class Add(BinaryOp, PIsaOp):
    """Class representing the p-isa addition operation"""

    def __str__(self) -> str:
        """Return the p-isa instructions of an addition"""
        return self._op_str("add")


class Sub(BinaryOp, PIsaOp):
    """Class representing the p-isa subtraction operation"""

    def __str__(self) -> str:
        """Return the p-isa instructions of an subtraction"""
        return self._op_str("sub")


class Mul(BinaryOp, PIsaOp):
    """Class representing the p-isa multiplication operation"""

    def __str__(self) -> str:
        """Return the p-isa instructions of an multiplication"""
        return self._op_str("mul")


class Muli(BinaryOp, PIsaOp):
    """Class representing the p-isa multiplication operation with immediates"""

    def __str__(self) -> str:
        """Return the p-isa instructions of an multiplication with immediates"""
        return self._op_str("mac")


class Mac(BinaryOp, PIsaOp):
    """Class representing the p-isa multiplication and accumulate operation"""

    def __str__(self) -> str:
        """Return the p-isa instructions of an multiplication and accumulate"""
        return self._op_str("mac")


class Maci(BinaryOp, PIsaOp):
    """Class representing the p-isa multiplication and accumulate operation with immediates"""

    def __str__(self) -> str:
        """Return the p-isa instructions of an multiply and accumulate with immediates"""
        return self._op_str("mac")


class Butterfly:
    """Common arguments for butterfly operations"""

    logN: int
    output0: str
    output1: str
    input0: str
    input1: str
    metas: tuple[int, int, int]
    q: int

    def _op_str(self, op) -> str:
        """Return the p-isa instructions of an multiplication and accumulate"""
        ws = "_".join(map(str, self.metas))
        return f"{self.logN}, {op}, {self.output0}, {self.output1}, {self.input0}, {self.input1}, w_{ws}, {self.q}"


class NTT(Butterfly, PIsaOp):
    """Class representing the p-isa NTT operation"""

    def __str__(self) -> str:
        """Return the p-isa instructions of an NTT"""
        return self._op_str("ntt")


class INTT(Butterfly, PIsaOp):
    """Class representing the p-isa INTT operation"""

    def __str__(self) -> str:
        """Return the p-isa instructions of an inverse NTT"""
        return self._op_str("intt")
