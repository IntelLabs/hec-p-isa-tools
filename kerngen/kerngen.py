#! /usr/bin/env python3

# Copyright (C) 2024 Intel Corporation

from generators import Generators
from pisa_generators.add import Add


MANIFEST_PATH = "./pisa_generators/manifest.json"


def main():
    generators = Generators.from_manifest(MANIFEST_PATH)
    print("Available p-isa ops\n", generators.available_pisa_ops())

    Klass = generators.get_pisa_op("Add")

    # TODO dynamic creation
    he_ops: list = [Add(["a", "b"], "c"), Add(["c", "d"], "e")]

    # string blocks of the p-isa instructions
    pisa_ops = ("\n".join(map(str, he_op.to_pisa())) for he_op in he_ops)

    for pisa_op in pisa_ops:
        print(pisa_op)


if __name__ == "__main__":
    main()
