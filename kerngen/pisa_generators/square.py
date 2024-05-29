# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""Module containing conversions or operations from isa to p-isa."""

from dataclasses import dataclass

from high_parser.pisa_operations import PIsaOp
from high_parser import Context, HighOp, Polys

from .basic import Mul


@dataclass
class Square(HighOp):
    """Class representing the high-level squaring operation"""

    context: Context
    output: Polys
    input0: Polys

    def to_pisa(self) -> list[PIsaOp]:
        """Return the p-isa equivalent of an Add"""

        return Mul(self.context, self.output, self.input0, self.input0).to_pisa()
