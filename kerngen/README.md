# Introduction

This is the kernel generator.


# Dependencies

python >= 3.10
pip

and what is listed in the [requirements](./requirements.txt) file. To install
the python dependencies and development tools.

```bash
pip -r requirements.txt
```


# Implementation

The design is a simplified interpreter pattern. A domain specific language
(DSL) is defined as `high language` ...


# Input high language

Context defines the global properties `(scheme, poly_order, max_rns)` of the
input script.

Data defines symbols to be used and their attributes.

All other commands are assumed to be operations. These are defined in the
[manifest.json](./pisa_generators/manifest.json) file.
Documentation on each command can be found in [COMMANDS.md]().
```
CONTEXT BGV 8192 2
DATA a
DATA b
DATA c
ADD c a b
```


# Adding new kernel generators

You can add new kernel generators that you have developed by creating a class
that inherits from the `HighOp` abstract class (interface) and implementing the
`to_pisa` method; turning this instruction into a p-isa instruction class.
Examples can be seen in the simpler implementations given in
[basic.py](./pisa_generators/basic.py). Also, provide a class method
`from_string` that will be passed the args for that command.

For `kerngen` to know of your class that represents a new command of the high
language, simply add an entry into the JSON object in the
[manifest.json](./pisa_generators/manifest.json) file. The key is the command
name and the value is a list containing the class name as the first entry and
the file it is located in as its second. e.g.
```
"OPNAME": ["ClassName", "filename.py"]
```

For kernel writers the reserved words that cannot be used as `OPNAME` are:
```
- CONTEXT
- DATA
```


# Running the tests
Tests are provided in the [tests](./tests) directory and use the
[pytest](https://pypi.org/project/pytest/) framework. To run the tests run the
following
```bash
cd tests
pytest .
```
