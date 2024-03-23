# Copyright (C) 2024 Intel Corporation

"""Module containing the low level p-isa operations"""

from dataclasses import dataclass
from typing import Protocol


class PIsaOp(Protocol):
    """Protocol for p-isa operation"""

    def __str__(self) -> str:
        """Return the p-isa instructions of the operation"""


@dataclass
class NormalBinaryOp:
    """Class representing the p-isa addition operation"""

    output: str
    input0: str
    input1: str
    q: str


class Add(NormalBinaryOp, PIsaOp):
    """Class representing the p-isa addition operation"""

    def __str__(self) -> str:
        """Return the p-isa instructions of an addition"""

        return f"13, add, {self.output}, {self.input0}, {self.input1}, {self.q}"
