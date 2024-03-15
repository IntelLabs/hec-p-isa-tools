# Copyright (C) 2024 Intel Corporation

import json

class Generators:
    def __init__(self, op_to_object_map: dict[str, str]):
        self.map = op_to_object_map

    @classmethod
    def from_manifest(cls, filepath: str):
        """"""
        with open(filepath) as manifest_file:
            return cls(json.load(manifest_file))

    def available_pisa_ops(self) -> str:
        return "\n".join(f"{op}" for op in self.map.keys())
