#! /usr/bin/env python3
# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""
kerngraph.py

This script provides a command-line tool for parsing kernel strings from standard input using the KernelParser class.
Future improvements may include graph representation of the parsed kernels and optimization.

Functions:
    parse_args():
        Parses command-line arguments.
        Returns:
            argparse.Namespace: Parsed arguments including debug flag.

    main(args):
        Reads lines from standard input, parses each line as a kernel string using KernelParser,
        and prints the successfully parsed kernel objects. If parsing fails for a line, an error
        message is printed if debug mode is enabled.

Usage:
    Run the script and provide kernel strings via standard input. Use the '-d' or '--debug' flag
    to enable debug output for parsing errors.

Example:
    $ cat bgv.add.high | ./kerngen.py | ./kerngraph.py
"""


import argparse
import sys
from kernel_parser.parser import KernelParser


def parse_args():
    """Parse arguments from the commandline"""
    parser = argparse.ArgumentParser(description="Kernel Graph Parser")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable Debug Print")
    return parser.parse_args()


def main(args):
    """Main function to read input and parse each line with KernelParser."""
    input_lines = sys.stdin.read().strip().splitlines()
    valid_kernels = []

    for line in input_lines:
        try:
            kernel = KernelParser.parse_kernel(line)
            valid_kernels.append(kernel)
        except ValueError as e:
            if args.debug:
                print(f"Error parsing line: {line}\nReason: {e}")
            continue  # Skip invalid lines

    if not valid_kernels:
        print("No valid kernel strings were parsed.")
    else:
        print("Successfully parsed kernel objects:")
        for kernel in valid_kernels:
            print(kernel)


if __name__ == "__main__":
    cmdline_args = parse_args()
    main(cmdline_args)
