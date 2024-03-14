# Copyright (C) 2024 Intel Corporation

from dataclasses import dataclass

from pisa_operations import Add as PisaAdd

@dataclass
class Add:
    """"""
    inputs: list[str]
    output: str

    def to_pisa(self):
        return [PisaAdd(self.inputs, self.output)] 

