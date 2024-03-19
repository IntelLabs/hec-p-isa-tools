#! /usr/bin/env python3

# Copyright (C) 2024 Intel Corporation

"""Module for generating p-isa kernels"""

import sys
from high_parser import parse_inputs, Command
from generators import Generators


MANIFEST_PATH = "./pisa_generators/manifest.json"


def main():
    """Main entrypoint. Load available p-isa ops and parse isa instructions."""
    generators = Generators.from_manifest(MANIFEST_PATH)
    #     print("Available p-isa ops\n", generators.available_pisa_ops(), sep="")

    inputs = parse_inputs(sys.stdin.readlines())

    commands = [command for command in inputs if isinstance(command, Command)]
    he_ops = [
        generators.get_pisa_op(op)(inputs, output) for op, inputs, output in commands
    ]

    # string blocks of the p-isa instructions
    pisa_ops = ["\n".join(map(str, he_op.to_pisa())) for he_op in he_ops]

    hashes = "#" * 3
    for kernel_no, (pisa_op, he_op) in enumerate(zip(pisa_ops, he_ops)):
        print(hashes, f"Kernel ({kernel_no}):", he_op, hashes)
        print(pisa_op)


if __name__ == "__main__":
    main()
