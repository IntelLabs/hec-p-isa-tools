# Introduction

This is the kernel generator responsible for producing HERACLES ISA kernels for
various polynomial operations that occur in FHE.


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
(DSL) defined as `high language` is recieved as input to the kernel generator.
This `high language` describes FHE scheme and context parameters, as well as
the operation with relative operands. This language is interpreted as a `high
level instruction` which is then mapped to its corresponding `low level p-ISA
instruction`. The resulting ISA kernel is sent to `stdout`.


# Input high language

Context defines the global properties `(scheme, poly_order, max_rns)` of the
input script.

Data defines symbols to be used and their attribute(s) (`num_parts`) where
`num_parts` is the number of polynomials that comprise the data variable.

All other commands are assumed to be operations. These are defined in the
[manifest.json](./pisa_generators/manifest.json) file.
Documentation on each command can be found in [COMMANDS.md]().
```
CONTEXT BGV 8192 4
DATA a 2
DATA b 2
DATA c 2
ADD c a b
```


# Generating kernels

The main entrypoint to the kernel generator is [kerngen.py](kerngen.py). This
script expects input from `stdin` in the form of the input high language
described above. It can be called with
```bash
./kerngen.py < addition.data
```
where `addition.data` is a text file containing the high language for an `ADD`
operation.

The kernel generator prints two comments, a context and kernel descriptor
respectively, followed by the p-ISA kernel. If desired, the comments can be
disabled by passing the `-q` or `--quiet` flag to the kernel generator, i.e.,
```bash
./kerngen.py -q < addition.data
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
[manifest.json](./pisa_generators/manifest.json) file. The key of the outermost
JSON object is the FHE scheme `{BGV, CKKS, ...}` which corresponds to a set of
operations of which it is associated with.  Each operation (inner JSON object)
consists of the an operation name `OPNAME` as its key and a list containing the
class name as the first entry and the file it is located in as its second. e.g.
```
\{
  "SCHEME": \{
    "OPNAME": ["ClassName", "filename.py"]
  \}
\}
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
