# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""A module to process optional key/value dictionary parameters"""

from abc import ABC, abstractmethod


class OptionalDict(ABC):
    """Abstract class to hold optional key/value pairs"""

    op_name: str = ""
    op_value = None

    @abstractmethod
    def validate(self, value):
        """Abstract method, which defines how to valudate a value"""


class OptionalIntDict(OptionalDict):
    """Holds a key/value pair for optional parameters of type Int"""

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


class OptionalIntBounds:
    """Holds min/max/default values for optional parameters for type Int"""

    int_min: int
    int_max: int
    default: int | None

    def __init__(self, int_min: int, int_max: int, default: int | None):
        self.int_min = int_min
        self.int_max = int_max
        self.default = default


class OptionalDictFactory(ABC):
    """Abstract class that creates OptionalDict objects"""

    MAX_KRNS_DELTA = 128
    MAX_DIGIT = 3
    MIN_KRNS_DELTA = MIN_DIGIT = 0
    optionals = {
        "krns_delta": OptionalIntBounds(MIN_KRNS_DELTA, MAX_KRNS_DELTA, 0),
        "num_digits": OptionalIntBounds(MIN_DIGIT, MAX_DIGIT, None),
    }

    @staticmethod
    @abstractmethod
    def create(name: str, value) -> OptionalDict:
        """Abstract method, to define how to create an OptionalDict"""


class OptionalIntDictFactory(OptionalDictFactory):
    """OptionalDict parameter factory for Int types"""

    @staticmethod
    def create(name: str, value: int) -> OptionalIntDict:
        """Create a OptionalInt object based on key/value pair"""
        if name in OptionalIntDictFactory.optionals:
            if isinstance(OptionalIntDictFactory.optionals[name], OptionalIntBounds):
                optional_int = OptionalIntDict(
                    name,
                    OptionalIntDictFactory.optionals[name].int_min,
                    OptionalIntDictFactory.optionals[name].int_max,
                )
                optional_int.op_value = value
            # add other optional types here
        else:
            raise KeyError(f"Invalid optional name: '{name}'")
        return optional_int


class OptionalDictFactoryDispatcher:
    """An object dispatcher based on key/value pair"""

    @staticmethod
    def create(name: str, value) -> OptionalDict:
        """Creat an OptionalDict object based on the type of value passed in"""
        if value.isnumeric():
            value = int(value)
        match value:
            case int():
                return OptionalIntDictFactory.create(name, value)
            case _:
                raise ValueError(f"Current type '{type(value)}' is not supported.")


class OptionalDictParser:
    """Parses key/value pairs and returns a dictionary of optional parameters"""

    @staticmethod
    def __default_values():
        default_dict = {}
        for key, val in OptionalDictFactory.optionals.items():
            default_dict[key] = val.default
        return default_dict

    @staticmethod
    def parse(optionals: list[str]):
        """Parse the optional parameter list and return a dictionary with values"""
        output_dict = OptionalDictParser.__default_values()
        for option in optionals:
            try:
                key, value = option.split("=")
                output_dict[key] = OptionalDictFactoryDispatcher.create(
                    key, value
                ).op_value
            except ValueError as err:
                raise ValueError(
                    f"Optional variables must be key/value pairs (e.g. krns_delta=1, num_digits=3): '{option}'"
                ) from err
        return output_dict
