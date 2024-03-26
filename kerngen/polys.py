# Copyright (C) 2024 Intel Corporation

"""Convenience class for polynomials"""

from dataclasses import dataclass


class PolyOutOfBoundsError(Exception):
    """Exception for Poly attributes being out of bounds"""


@dataclass
class Polys:
    """helper object for handling polynomial expansion"""

    name: str
    parts: int
    rns: int

    def expand(self, part: int, q: int, unit: int) -> str:
        """Returns a string of the expanded symbol w.r.t. rns, part, and unit"""
        # Sanity bounds checks
        if part > self.parts or q > self.rns:
            raise PolyOutOfBoundsError(
                f"part `{part}` or q `{q}` is more than the poly's `{self}`"
            )
        return f"{self.name}_{part}_{q}_{unit}"

    def __call__(self, part: int, q: int, unit: int) -> str:
        """Forward `expand` method"""
        return self.expand(part, q, unit)

    def __repr__(self) -> str:
        return self.name
