# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

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

    # def expand(self, part: int, q: int, unit: int) -> str:
    def expand(self, *args) -> str:
        """Returns a string of the expanded symbol w.r.t. rns, part, and unit"""
        part, q, unit = args
        # Sanity bounds checks
        if self.start_parts > part >= self.parts or self.start_rns > q >= self.rns:
            raise PolyOutOfBoundsError(
                f"part `{part}` or q `{q}` are not within the poly's range `{self!r}`"
            )
        return f"{self.name}_{part}_{q}_{unit}"

    def __call__(self, *args) -> str:
        """Forward `expand` method"""
        return self.expand(*args)

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
            case "single_rns":
                copy.rns = 1
                return cls(**vars(copy))
            case "last_part":
                copy.start_parts = copy.parts - 1
                return cls(**vars(copy))
            case None:
                return cls(**vars(copy))
            case _:
                raise ValueError("Unknown mode for Polys")


class KeyPolys(Polys):
    """A Polys object for Keys"""

    def __init__(self, *args, **kwargs):
        digits = "digits"
        self.digits = kwargs.get(digits, 1)
        super().__init__(*args, **{k: v for k, v in kwargs.items() if k != digits})

    # def expand(self, digit: int, part: int, q: int, unit: int) -> str:
    def expand(self, *args) -> str:
        """Returns a string of the expanded symbol w.r.t. digit, rns, part, and unit"""
        digit, part, q, unit = args
        # Sanity bounds checks
        if (
            self.start_parts > part >= self.parts
            or self.start_rns > q >= self.rns
            or digit > self.digits
        ):
            raise PolyOutOfBoundsError(
                f"part `{digit}` or `{part}` or q `{q}` are not within the key poly's range `{self!r}`"
            )
        return f"{self.name}_{part}_{digit}_{q}_{unit}"


class HighOp(ABC):
    """An abstract class to help define/enforce API"""

    @abstractmethod
    def to_pisa(self) -> list[PIsaOp]:
        """Returns a list of the p-isa operations / instructions"""

    @classmethod
    def from_string(cls, context, polys_map, args_line: str):
        """Construct HighOp from a string args"""
        try:
            ios = (polys_map[io] for io in args_line.split())
            return cls(context, *ios)  # type: ignore

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


# TODO remove hardcoding. Maybe move this to Config?
NATIVE_POLY_SIZE = 8192
MIN_POLY_SIZE = 16384
MAX_POLY_SIZE = 131072
MAX_KRNS_DELTA = 128
MAX_DIGIT = 3
MIN_KRNS_DELTA = MIN_DIGIT = 0


def _parse_optional(optionals: list[str]):
    """Parse optional key/value pairs"""
    krns_delta = None
    num_digits = None

    def valid_num_option(value: str, min_val: int, max_val: int):
        """Validate numeric options with min/max range"""
        if value.isnumeric() and int(value) > min_val and int(value) < max_val:
            return True
        return False

    for option in optionals:
        try:
            key, value = option.split("=")
            match key:
                case "krns_delta":
                    if not valid_num_option(value, MIN_KRNS_DELTA, MAX_KRNS_DELTA):
                        raise ValueError(
                            f"krns_delta must be in range ({MIN_KRNS_DELTA}, {MAX_KRNS_DELTA}): krns_delta={krns_delta}"
                        )
                    krns_delta = int(value)
                case "num_digits":
                    if not valid_num_option(value, MIN_DIGIT, MAX_DIGIT):
                        raise ValueError(
                            f"num_digits must be in range ({MIN_DIGIT}, {MAX_DIGIT}): num_digits={num_digits}"
                        )
                    num_digits = int(value)
                case _:
                    raise KeyError(f"Invalid optional key for Context: {key}")
        except ValueError as err:
            raise ValueError(
                f"Optional variables must be key/value pairs (e.g. krns_delta=1, num_digits=3): '{option}'"
            ) from err

    return krns_delta, num_digits


class Context(BaseModel):
    """Class representing a given context of the scheme"""

    scheme: str
    poly_order: int  # the N
    max_rns: int
    # optional vars for context
    key_rns: int | None
    num_digits: int | None

    @classmethod
    def from_string(cls, line: str):
        """Construct context from a string"""
        scheme, poly_order, max_rns, *optional = line.split()
        krns_delta, num_digits = _parse_optional(optional)
        int_poly_order = int(poly_order)
        if (
            int_poly_order < MIN_POLY_SIZE
            or int_poly_order > MAX_POLY_SIZE
            or not math.log2(int_poly_order).is_integer()
        ):
            raise ValueError(
                f"Poly order `{int_poly_order}` must be power of two >= {MIN_POLY_SIZE} and < {MAX_POLY_SIZE}"
            )

        int_max_rns = int(max_rns)
        int_key_rns = int_max_rns + krns_delta if krns_delta else None
        int_num_digits = num_digits if num_digits else None
        return cls(
            scheme=scheme.upper(),
            poly_order=int_poly_order,
            max_rns=int_max_rns,
            key_rns=int_key_rns,
            num_digits=int_num_digits,
        )

    @property
    def ntt_stages(self):
        """Returns NTT stages (== log2(N))"""
        return int(math.log2(self.poly_order))

    @property
    def units(self):
        """units based on 8192 ~ 8K sized polynomials"""
        return max(1, self.poly_order // NATIVE_POLY_SIZE)


class KernelContext(Context):
    """Class representing a kernel context"""

    # Recall that Context inherits from BaseModel
    label: str

    @classmethod
    def from_context(cls, context: Context, label: str = "0") -> "KernelContext":
        """Create a kernel context froma  context (and optionally a label)"""
        return cls(label=label, **vars(context))


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
        q = args[1]
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


ParserType = Context | Data | EmptyLine | Comment | Immediate | HighOp
