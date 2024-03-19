# Copyright (C) 2024 Intel Corporation

"""Convenience class for polynomials"""

from dataclasses import dataclass


@dataclass
class Polys:
    """helper object for handling polynomial expansion"""

    symbol: str
    parts: int
    units: int

    def expand(self, part: int, q: int, unit: int) -> str:
        """Returns a string of the expanded symbol and ..."""
        # TODO some sanity check code for bounds
        return f"{self.symbol}_{q}_{part}_{unit}"
