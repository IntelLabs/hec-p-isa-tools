# Copyright (C) 2024 Intel Corporation

"""Module contains abstractions for high operations / instructions"""

from abc import ABC, abstractmethod

from pisa_operations import PIsaOp


# pylint: disable=too-few-public-methods
class HighOp(ABC):
    """An abstract class to help define/enforce API"""

    @abstractmethod
    def to_pisa(self) -> list[PIsaOp]:
        """Returns a list of the p-isa operations / instructions"""

    @classmethod
    @abstractmethod
    def from_string(cls, context, args_line: str):
        """Construct HighOp from a string args"""
