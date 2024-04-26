# Copyright (C) 2024 Intel Corporation

"""Module for parsing isa commands"""

import math
import itertools as it
from abc import ABC, abstractmethod
from dataclasses import dataclass


from pydantic import BaseModel

from .pisa_operations import PIsaOp


class PolyOutOfBoundsError(Exception):
    """Exception for Poly attributes being out of bounds"""


@dataclass
class Polys:
    """helper object for handling polynomial expansion"""

    name: str
    parts: int
    rns: int
    start_parts: int = 0
    start_rns: int = 0

    def expand(self, part: int, q: int, unit: int) -> str:
        """Returns a string of the expanded symbol w.r.t. rns, part, and unit"""
        # Sanity bounds checks
        if self.start_parts > part >= self.parts or self.start_rns > q >= self.rns:
            raise PolyOutOfBoundsError(
                f"part `{part}` or q `{q}` are not within the poly's range `{self!r}`"
            )
        return f"{self.name}_{part}_{q}_{unit}"

    def __call__(self, part: int, q: int, unit: int) -> str:
        """Forward `expand` method"""
        return self.expand(part, q, unit)

    def __repr__(self) -> str:
        return self.name

    @classmethod
    def from_polys(cls, poly: "Polys", *, mode: str | None = None) -> "Polys":
        """Class method for creating a specific range of polys based on desired mode"""
        copy = Polys(**vars(poly))
        match mode:
            case "drop_last_rns":
                copy.rns -= 1
                return cls(**vars(copy))
            case "last_rns":
                copy.start_rns = copy.rns - 1
                return cls(**vars(copy))
            case None:
                return cls(**vars(copy))
            case _:
                raise ValueError("Unknown mode for Polys")


class HighOp(ABC):
    """An abstract class to help define/enforce API"""

    @abstractmethod
    def to_pisa(self) -> list[PIsaOp]:
        """Returns a list of the p-isa operations / instructions"""

    @classmethod
    def from_string(cls, context, polys_map, args_line: str, label: str = "0"):
        """Construct HighOp from a string args"""
        try:
            ios = (polys_map[io] for io in args_line.split())
            return cls(label, context, *ios)  # type: ignore

        except ValueError as e:
            raise ValueError(f"Could not unpack command string `{args_line}`") from e


# TODO should this live here?
def expand_ios(context, output, *inputs):
    """Return expanded polys based on rns, part, and unit"""
    return (
        (
            (io.expand(part, q, unit) for io in (output, *inputs)),
            q,
        )
        for q, part, unit in it.product(
            range(inputs[0].start_rns, inputs[0].rns),
            range(inputs[0].start_parts, inputs[0].parts),
            range(context.units),
        )
    )


class Comment(BaseModel):
    """Holder of a comment line"""

    comment: str


class EmptyLine(BaseModel):
    """Holder of an empty line"""


class Context(BaseModel):
    """Class representing a given context of the scheme"""

    scheme: str
    poly_order: int  # the N
    max_rns: int
    key_rns: int | None

    @classmethod
    def from_string(cls, line: str):
        """Construct context from a string"""
        scheme, poly_order, max_rns, *optional = line.split()
        krns, *rest = optional
        if rest != []:
            raise ValueError(f"too many parameters for context given: {line}")
        int_poly_order = int(poly_order)
        int_max_rns = int(max_rns)
        int_key_rns = int_max_rns + int(krns[0]) if krns else None
        return cls(
            scheme=scheme.upper(),
            poly_order=int_poly_order,
            max_rns=int_max_rns,
            key_rns=int_key_rns,
        )

    @property
    def ntt_stages(self):
        """Returns NTT stages (== log2(N))"""
        return int(math.log2(self.poly_order))

    @property
    def units(self):
        """units based on 8192 ~ 8K sized polynomials"""
        # TODO hardcoding will be removed soon
        native_poly_size = 8192
        return max(1, self.poly_order // native_poly_size)


class Data(BaseModel):
    """Class representing a data type with related attributes"""

    name: str
    parts: int

    @classmethod
    def from_string(cls, line: str):
        """Construct data from a string"""
        name, parts = line.split()
        return cls(name=name, parts=int(parts))


class Immediate(BaseModel):
    """Class representing a Immediate type with related attributes.
    Immediate in that it holds optional RNS"""

    name: str
    rns: int | None = None

    def __call__(self, *args, **kwargs):
        """Return the string of immediate with rns"""
        if self.rns is None:
            return self.name

        # Sanity bounds checks
        q, *_ = args
        if q > self.rns:
            raise PolyOutOfBoundsError(
                f"q `{q}` is more than the immediate with RNS `{self!r}`"
            )
        return f"{self.name}_{q}"

    @classmethod
    def from_string(cls, line: str):
        """Construct data from a string"""
        name, *rest = line.split()
        if len(rest) > 0:
            raise ValueError("Immediate only has a name; no other arguments")
        return cls(name=name)


ParserType = Context | Data | EmptyLine | Comment | HighOp
