#! /usr/bin/env python3

# Copyright (C) 2024 Intel Corporation

"""Module for generating p-isa kernels"""

import sys

from polys import Polys
from high_parser import parse_inputs, Context, Data


def find_context(iterable) -> Context:
    """Return found context"""
    g = (context for context in iterable if isinstance(context, Context))
    return next(g)


Symbol = str


def main():
    """Main entrypoint. Load available p-isa ops and parse isa instructions."""

    commands = parse_inputs(sys.stdin.readlines())

    # Find context should only be one at the top
    context = find_context(commands)

    # Units computation
    # TODO
    units = 1

    # Populate the data symbols
    polys_map: dict[Symbol, Polys] = {
        data.name: Polys(symbol=data.name, parts=context.max_rns, units=units)
        for data in commands
        if isinstance(data, Data)
    }

    # String blocks of the p-isa instructions
    pisa_ops: list[str] = [
        "\n".join(map(str, command.to_pisa())) if hasattr(command, "to_pisa") else None
        for command in commands
    ]

    filtered = (t for t in zip(pisa_ops, commands) if t[0] is not None)
    hashes = "#" * 3
    for kernel_no, (pisa_op, command) in enumerate(filtered):
        print(hashes, f"Kernel ({kernel_no}):", command, hashes)
        print(pisa_op)


if __name__ == "__main__":
    main()
