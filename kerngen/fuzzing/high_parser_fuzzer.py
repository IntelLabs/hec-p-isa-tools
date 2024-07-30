#! /usr/bin/env python3

# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""Basic fuzzer for kerngen/Parser() class"""
import sys
from pathlib import Path
from typing import Iterable

import atheris

sys.path.insert(0, str(Path("../").resolve()))

with atheris.instrument_imports():
    from high_parser.parser import Parser
    from high_parser.config import Config


def to_string_block(iterable: Iterable[str], *, ignore_comments: bool) -> str:
    """helper to string block"""
    strs = map(str, iterable)
    if ignore_comments is True:
        return "\n".join(i for i in strs if not i.rstrip().startswith("#"))
    return "\n".join(strs)


def fuzz_parser(data):
    """Main entrypoint. Load available p-isa ops and parse isa instructions."""

    parse_results = Parser().parse_inputs(data)
    Config.legacy_mode = False

    # String blocks of the p-isa instructions (forward the Nones)
    pisa_ops: list[str | None] = list(
        to_string_block(op, ignore_comments=True) if op is not None else None
        for op in parse_results.get_pisa_ops()
    )

    filtered = (t for t in zip(pisa_ops, parse_results.commands) if t[0] is not None)

    hashes = "#" * 3

    # pylint: disable=unused-variable
    context = parse_results.context

    for kernel_no, (pisa_op, command) in enumerate(filtered):
        print(hashes, f"Kernel ({kernel_no}):", command, hashes)
        print(pisa_op)


def test_one_input(input_bytes):
    """Main fuzzing entrypoint - Format input data and call fuzz function"""

    fdp = atheris.FuzzedDataProvider(input_bytes).ConsumeUnicodeNoSurrogates(512)

    fuzz_parser(fdp)


def main():
    """Main - Setup Atheris to fuzz target"""
    # Initialize Atheris with any command-line arguments
    atheris.Setup(sys.argv, test_one_input)
    # Start the fuzzer
    atheris.Fuzz()


if __name__ == "__main__":
    main()
