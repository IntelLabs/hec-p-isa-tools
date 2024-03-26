# Copyright (C) 2024 Intel Corporation

"""Module contains abstractions for high operations / instructions"""

from abc import ABC, abstractmethod
import itertools as it

from pisa_operations import PIsaOp


# pylint: disable=too-few-public-methods
class HighOp(ABC):
    """An abstract class to help define/enforce API"""

    @abstractmethod
    def to_pisa(self) -> list[PIsaOp]:
        """Returns a list of the p-isa operations / instructions"""

    # FIXME mypy error
    @classmethod
    def from_string(cls, context, polys_map, args_line: str):
        """Construct HighOp from a string args"""
        try:
            ios = (polys_map[io] for io in args_line.split())
            return cls(context, *ios)

        except ValueError as e:
            raise ValueError(f"Could not unpack command string `{args_line}`") from e


def expand_ios(context, output, *inputs):
    """Return expanded polys based on rns, part, and unit"""
    return (
        (
            (io.expand(part, q, unit) for io in (output, *inputs)),
            q,
        )
        for q, part, unit in it.product(
            range(inputs[0].rns),
            range(inputs[0].parts),
            range(context.units),
        )
    )
