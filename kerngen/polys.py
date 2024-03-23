# Copyright (C) 2024 Intel Corporation

"""Convenience class for polynomials"""

from dataclasses import dataclass


@dataclass
class Polys:
    """helper object for handling polynomial expansion"""

    name: str
    parts: int

    def expand(self, part: int, q: int, unit: int) -> str:
        """Returns a string of the expanded symbol w.r.t. rns, part, and unit"""
        # TODO some sanity check code for bounds
        return f"{self.name}_{part}_{q}_{unit}"
