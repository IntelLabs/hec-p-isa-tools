# Copyright (C) 2024 Intel Corporation

import json
from importlib import import_module
from pathlib import Path


class GeneratorError(Exception):
    """"""


class Generators:
    def __init__(self, dirpath: str, op_to_object_map: dict[str, str]):
        self.map = op_to_object_map
        self.directory = dirpath

    @classmethod
    def from_manifest(cls, filepath: str):
        """"""
        dirpath = str(Path(filepath).parent)
        with open(filepath) as manifest_file:
            return cls(dirpath, json.load(manifest_file))

    def available_pisa_ops(self) -> str:
        return "\n".join(f"{op}" for op in self.map.keys())

    def get_pisa_op(self, opname: str):
        try:
            filepath = self.directory + "." + Path(self.map[opname]).stem
            module = import_module(filepath)
            return getattr(module, opname)
        except KeyError:
            raise GeneratorError(f"Op name not found: {opname}")
        except AttributeError:
            raise GeneratorError(f"Op not found in module: {opname}")
        # TODO import error
