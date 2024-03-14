#! /usr/bin/env python3

# Copyright (C) 2024 Intel Corporation

from pisa_generators.add import Add

if __name__ == "__main__":
    print("hello world")

    he_ops: list = [Add(["a", "b"], "c"), Add(["c", "d"], "e")]
    pisa_ops = (he_op.to_pisa() for he_op in he_ops)

    for pisa_op in pisa_ops:
        print("\n".join(map(str, pisa_op)))
