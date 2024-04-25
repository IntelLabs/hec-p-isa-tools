# Copyright (C) 2024 Intel Corporation

"""Module containing conversions or operations from isa to p-isa."""

from dataclasses import dataclass

from high_parser.pisa_operations import PIsaOp, Comment, Muli as pisa_op_muli
from high_parser import Context, Immediate, HighOp, Polys

from .basic import Add, Muli, mixed_to_pisa_ops
from .ntt import INTT, NTT
from .mod import Mod


@dataclass
class ModUp(HighOp):
    """Class representing relinearization operation"""

    label: str
    context: Context
    output: Polys
    input0: Polys

    def to_pisa(self) -> list[PIsaOp]:
        """Return the p-isa code to perform a modulus switch up (modup)"""
        return []
