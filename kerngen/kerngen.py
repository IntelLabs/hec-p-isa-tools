#! /usr/bin/env python3

# Copyright (C) 2024 Intel Corporation

"""Module for generating p-isa kernels"""

from typing import NamedTuple

from generators import Generators

MANIFEST_PATH = "./pisa_generators/manifest.json"


class Command(NamedTuple):
    """Class representing a command consiting of an operation with input(s) and
    output"""

    op: str
    inputs: list[str]
    output: str


class Data(NamedTuple):
    """Class representing a data type with related attributes"""

    name: str


def main():
    """Main entrypoint. Load available p-isa ops and parse isa instructions."""
    generators = Generators.from_manifest(MANIFEST_PATH)
    print("Available p-isa ops\n", generators.available_pisa_ops(), sep="")

    commands = [Command("Add", ["a", "b"], "c"), Command("Add", ["c", "d"], "e")]
    he_ops = [
        generators.get_pisa_op(op)(inputs, output) for op, inputs, output in commands
    ]

    # string blocks of the p-isa instructions
    pisa_ops = ("\n".join(map(str, he_op.to_pisa())) for he_op in he_ops)

    for pisa_op in pisa_ops:
        print(pisa_op)


if __name__ == "__main__":
    main()
