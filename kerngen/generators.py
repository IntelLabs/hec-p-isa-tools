# Copyright (C) 2024 Intel Corporation

"""Module providing an interface to pisa generators"""

import json
from importlib import import_module
from pathlib import Path


class GeneratorError(Exception):
    """Class representing errors raised by the Generators class"""


class Generators:
    """Class responsible for obtaining pisa ops from the pisa generators"""

    def __init__(self, dirpath: str, op_to_object_map: dict[str, str]):
        """Initializer. Expects a path to a manifest JSON file and dictionary
        `{op : filename}`"""
        self.map = op_to_object_map
        self.directory = dirpath

    @classmethod
    def from_manifest(cls, filepath: str):
        """Creates a `Generators` object given a manifest JSON file. Parses the
        manifest file as a python dictionary and stores it in `self.map`"""
        filepath = Path(filepath)
        dirpath = str(filepath.parent)
        with open(filepath, encoding="utf-8") as manifest_file:
            return cls(dirpath, json.load(manifest_file))

    def available_pisa_ops(self) -> str:
        """Returns a list of available pisa ops."""
        return "\n".join(f"{op}" for op in self.map.keys())

    def get_pisa_op(self, opname: str):
        """Returns the pisa op object given a valid op name"""
        try:
            filepath = self.directory + "/" + Path(self.map[opname]).stem
            module_path = filepath.replace("/", ".")
            module = import_module(module_path)
            return getattr(module, opname)
        except KeyError as e:
            raise GeneratorError(f"Op name not found: {opname}") from e
        except AttributeError as e:
            raise GeneratorError(f"Op not found in module: {opname}") from e
        except ImportError as e:
            raise GeneratorError(f"Unable to import module: {module_path}") from e