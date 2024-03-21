#! /usr/bin/env python3

# Copyright (C) 2024 Intel Corporation

"""Module for generating p-isa kernels"""

import sys

from high_parser import parse_inputs, Context
from pisa_generators.highop import HighOp


def find_context(iterable) -> Context:
    """Return found context"""
    g = (context for context in iterable if isinstance(context, Context))
    return next(g)


def to_string_block(iterable) -> str:
    """helper to string block"""
    return "\n".join(map(str, iterable))


def main():
    """Main entrypoint. Load available p-isa ops and parse isa instructions."""

    commands = parse_inputs(sys.stdin.readlines())

    # Find context should only be one at the top
    context = find_context(commands)

    # String blocks of the p-isa instructions
    pisa_ops: list[str] = [
        to_string_block(command.to_pisa()) if isinstance(command, HighOp) else None
        for command in commands
    ]

    filtered = (t for t in zip(pisa_ops, commands) if t[0] is not None)
    hashes = "#" * 3
    print(hashes, "Context:", context, hashes)
    for kernel_no, (pisa_op, command) in enumerate(filtered):
        print(hashes, f"Kernel ({kernel_no}):", command, hashes)
        print(pisa_op)


if __name__ == "__main__":
    main()
