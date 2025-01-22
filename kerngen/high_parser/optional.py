# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""A module to process optional context parameters"""

from abc import ABC, abstractmethod


class OptionalContext(ABC):
    """Abstract class to hold optional parameters for context"""

    op_name: str = ""
    op_value = None

    @abstractmethod
    def validate(self, value):
        """Abstract method, which defines how to valudate a value"""


class OptionalInt(OptionalContext):
    """Holds a key/value pair for optional context parameters of type Int"""

    def __init__(self, name: str, min_val: int, max_val: int):
        self.min_val = min_val
        self.max_val = max_val
        self._op_name = name

    def validate(self, value: int):
        """Validate numeric options with min/max range"""
        if self.min_val < value < self.max_val:
            return True
        return False

    @property
    def op_value(self):
        """Get op_value"""
        return self._op_value

    @op_value.setter
    def op_value(self, value: int):
        """Set op_value"""
        if self.validate(value):
            self._op_value = int(value)
        else:
            raise ValueError(
                "{self.op_name} must be in range ({self.min_val}, {self.max_val}): {self.op_name}={self.op_value}"
            )


class OptionalIntMinMax:
    """Holds min/max values for optional context parameters for type Int"""

    int_min: int
    int_max: int
    default: int | None

    def __init__(self, int_min: int, int_max: int, default: int | None):
        self.int_min = int_min
        self.int_max = int_max
        self.default = default


class OptionalFactory(ABC):
    """Abstract class that creates OptionaContext objects"""

    MAX_KRNS_DELTA = 128
    MAX_DIGIT = 3
    MIN_KRNS_DELTA = MIN_DIGIT = 0
    optionals = {
        "krns_delta": OptionalIntMinMax(MIN_KRNS_DELTA, MAX_KRNS_DELTA, 0),
        "num_digits": OptionalIntMinMax(MIN_DIGIT, MAX_DIGIT, None),
    }

    @staticmethod
    @abstractmethod
    def create(name: str, value) -> OptionalContext:
        """Abstract method, to define how to create an OptionalContext"""


class OptionalIntFactory(OptionalFactory):
    """Optional context parameter factory for Int types"""

    @staticmethod
    def create(name: str, value: int) -> OptionalInt:
        """Create a OptionalInt object based on key/value pair"""
        if name in OptionalIntFactory.optionals:
            if isinstance(OptionalIntFactory.optionals[name], OptionalIntMinMax):
                optional_int = OptionalInt(
                    name,
                    OptionalIntFactory.optionals[name].int_min,
                    OptionalIntFactory.optionals[name].int_max,
                )
                optional_int.op_value = value
            # add other optional types here
        else:
            raise KeyError(f"Invalid optional name for Context: '{name}'")
        return optional_int


class OptionalFactoryDispatcher:
    """An object dispatcher based on key/value pair for comptional context parameters"""

    @staticmethod
    def create(name: str, value) -> OptionalContext:
        """Creat an OptionalContext object based on the type of value passed in"""
        if value.isnumeric():
            value = int(value)
        match value:
            case int():
                return OptionalIntFactory.create(name, value)
            case _:
                raise ValueError(f"Current type '{type(value)}' is not supported.")


class OptionalsParser:
    """Parses key/value pairs and returns a dictionary of optiona parameters"""

    @staticmethod
    def __default_values():
        default_dict = {}
        for key, val in OptionalFactory.optionals.items():
            default_dict[key] = val.default
        return default_dict

    @staticmethod
    def parse(optionals: list[str]):
        """Parse the optional parameter list and return a dictionary with values"""
        output_dict = OptionalsParser.__default_values()
        for option in optionals:
            try:
                key, value = option.split("=")
                output_dict[key] = OptionalFactoryDispatcher.create(key, value).op_value
            except ValueError as err:
                raise ValueError(
                    f"Optional variables must be key/value pairs (e.g. krns_delta=1, num_digits=3): '{option}'"
                ) from err
        return output_dict
