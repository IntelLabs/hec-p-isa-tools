#! /usr/bin/env python3

# Copyright (C) 2024 Intel Corporation

"""Module for generating p-isa kernels"""

import sys
from high_parser import parse_inputs


def main():
    """Main entrypoint. Load available p-isa ops and parse isa instructions."""

    commands = parse_inputs(sys.stdin.readlines())

    # string blocks of the p-isa instructions
    pisa_ops = [
        "\n".join(map(str, command.to_pisa()))
        for command in commands
        if hasattr(command, "to_pisa")
    ]

    hashes = "#" * 3
    for kernel_no, (pisa_op, command) in enumerate(zip(pisa_ops, commands)):
        print(hashes, f"Kernel ({kernel_no}):", command, hashes)
        print(pisa_op)


if __name__ == "__main__":
    main()
