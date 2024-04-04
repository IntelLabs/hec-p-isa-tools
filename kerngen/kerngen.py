#! /usr/bin/env python3

# Copyright (C) 2024 Intel Corporation

"""Module for generating p-isa kernels"""

import argparse
import sys
from typing import Iterable

from high_parser.parser import Parser


def parse_args():
    """Parse arguments from the commandline"""
    parser = argparse.ArgumentParser(description="Kernel Generator")
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="disable comments in output"
    )
    return parser.parse_args()


def to_string_block(iterable: Iterable[str]) -> str:
    """helper to string block"""
    return "\n".join(map(str, iterable))


def main(args):
    """Main entrypoint. Load available p-isa ops and parse isa instructions."""

    parse_results = Parser().parse_inputs(sys.stdin.readlines())

    # String blocks of the p-isa instructions (forward the Nones)
    pisa_ops: list[str] = list(
        to_string_block(op) if op is not None else None
        for op in parse_results.get_pisa_ops()
    )

    filtered = (t for t in zip(pisa_ops, parse_results.commands) if t[0] is not None)
    hashes = "#" * 3
    if not args.quiet:
        context = parse_results.context
        print(hashes, "Context:", context, hashes)

    if not args.quiet:
        for kernel_no, (pisa_op, command) in enumerate(filtered):
            print(hashes, f"Kernel ({kernel_no}):", command, hashes)
            print(pisa_op)
    else:
        for pisa_op, _ in filtered:
            print(pisa_op)


if __name__ == "__main__":
    cmdline_args = parse_args()
    main(cmdline_args)
