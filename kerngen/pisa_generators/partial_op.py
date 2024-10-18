# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""Module containing helper methods to support binary operations using partial polys (last RNS and/or last part)"""
from dataclasses import dataclass
from itertools import product

from high_parser import KernelContext, Polys

from high_parser.pisa_operations import Sub as pisa_op_sub
from high_parser.pisa_operations import Add as pisa_op_add
from high_parser.pisa_operations import Muli as pisa_op_muli

# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments


@dataclass
class PartialOpOptions:
    """Optional arguments for partial_op helper function"""

    output_last_q: bool = False
    input0_last_q: bool = False
    input1_last_q: bool = False
    input1_first_part: bool = False
    op_last_q: bool = False


@dataclass
class PartialOpPolys:
    """Polynomials used in partial ops"""

    output: Polys
    input0: Polys
    input1: Polys
    input_remaining_rns: Polys


def partial_op(
    context: KernelContext,
    op,
    polys: PartialOpPolys,
    options: PartialOpOptions,
    last_q: int,
):
    """ "A helper function to perform partial operation, such as add/sub on last half (input1) to all of input0"""
    return [
        op(
            context.label,
            polys.output(part, last_q if options.output_last_q else q, unit),
            polys.input0(part, last_q if options.input0_last_q else q, unit),
            polys.input1(
                0 if options.input1_first_part else part,
                last_q if options.input1_last_q else q,
                unit,
            ),
            last_q if options.op_last_q else q,
        )
        for part, q, unit in product(
            range(polys.input_remaining_rns.parts),
            range(polys.input_remaining_rns.rns),
            range(context.units),
        )
    ]


def add_last_half(
    context: KernelContext,
    output: Polys,
    input0: Polys,
    input1: Polys,
    input_remaining_rns: Polys,
    last_q: int,
):
    """Add input0 to input1 (first part)"""
    return partial_op(
        context,
        pisa_op_add,
        PartialOpPolys(output, input0, input1, input_remaining_rns),
        PartialOpOptions(
            output_last_q=True,
            input0_last_q=True,
            input1_last_q=True,
            input1_first_part=True,
            op_last_q=True,
        ),
        last_q,
    )


def sub_last_half(
    context: KernelContext,
    output: Polys,
    input0: Polys,
    input1: Polys,
    input_remaining_rns: Polys,
    last_q: int,
):
    """Subtract input1 (first part) with input0 (last RNS)"""
    return partial_op(
        context,
        pisa_op_sub,
        PartialOpPolys(output, input0, input1, input_remaining_rns),
        PartialOpOptions(input0_last_q=True, input1_first_part=True),
        last_q,
    )


def muli_last_half(
    context: KernelContext,
    output: Polys,
    input0: Polys,
    input1: Polys,
    input_remaining_rns: Polys,
    last_q: int,
):
    """Muli input0/1 w/input0 last RNS"""
    return partial_op(
        context,
        pisa_op_muli,
        PartialOpPolys(output, input0, input1, input_remaining_rns),
        PartialOpOptions(input0_last_q=True),
        last_q,
    )
