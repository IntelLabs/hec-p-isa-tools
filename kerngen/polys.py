# Copyright (C) 2024 Intel Corporation

"""Convenience class for polynomials"""

from dataclasses import dataclass


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
