# Copyright (C) 2024 Intel Corporation

"""Module contains abstractions for high operations / instructions"""

from abc import ABC, abstractmethod


# pylint: disable=too-few-public-methods
class HighOp(ABC):
    """An abstract class to help define/enforce API"""

    @abstractmethod
    def to_pisa(self) -> list:
        """Returns a list of the p-isa operations / instructions"""
