# Introduction

This is the kernel generator (`kerngen`) responsible for producing HERACLES ISA
kernels for various polynomial operations that occur in cryptography (or
elsewhere) such as in homomorphic encryption (HE). A kernel is a code snippet
of p-ISA instructions with the purpose of implementing some high level
polynomial operation.


# Dependencies
`kerngen` is written as a pure python program. Requirements required to be
installed,

- python >= 3.10
- pip (recommend >= 24.0)
- and python [requirements](./requirements.txt).

To install the python dependencies and development tools simply run,

```bash
pip -r requirements.txt
```


# Implementation

## Overview

The design is a simplified interpreter pattern. A domain specific language
defined as a 'kernel language' is received as input to the kernel generator.
This kernel language describes (which can be used for HE schemes) operations on
polynomials with given context parameters. This language is interpreted as a
`high level instruction` which is then mapped to its corresponding `low level
p-ISA instruction`. `kerngen` uses a common unix command line utility
convention and the resulting p-ISA kernel is sent to `stdout`.

## Internals

Under the `high_parser` directory is the core of the `kerngen` logic with the
principal classes being `Parser` and `Generator`. For completeness, we take a
quick look through the files.

- `config.py` is a minor file primarily containing the `Config` class. The
  class itself is used as global singleton object to hold congiuration
  information of `kerngen`. It was introduced to not disturb the existing
  APIs while changing global behaviour i.e. a legacy mode.

- `generators.py` contains the `Generator` class responsible for dealing
  with the manifest file and loading the appropriate kernel class. Instances of
  `Parser` have an instance of this class for a given manifest file.
  Instances should be created using the factory class method
  `from_manifest` and providing the path to the manifest file and a `scheme`.
  Although it is referred to as `scheme` it is fact just a key label to
  mapping of a collection of grouped kernels.
  Lookup can then be performed using `get_kernel` given a valid kernel
  operation name.
- `parser.py` contains `Parser` responsible for parsing the input kernel
  language and creating the correct corresponding command objects for the
  interpreter to process.

- `pisa_operations.py`

- `types.py`


# Input kernel language

There are several kinds of commands. Keywords that cannot be used for kernel
names,
```
- `CONTEXT`
- `DATA`
- `IMM`
```

All other commands are assumed to be operations. All operations are case
insensitive, but the convention we use is the operations are capitalized. These
are defined in the [manifest.json](./pisa_generators/manifest.json) file.
```
CONTEXT BGV 8192 4
DATA a 2
DATA b 2
DATA c 2
ADD c a b
```

## CONTEXT
Context defines the global properties `(scheme, poly_order, max_rns,
key_rns(optional))` of the input script.
`CONTEXT` sets a global context for properties required by the kernels.
- first field defines what we call scheme. In reality, it specifies the set of
kernel instructions given in the manifest file, see []().
- second field defines the polynomial size. This is required to when generating
kernels how many units (multiples of the native polynomial size) are required
and handled.
- third field defines the max RNS, the global max number of how many moduli that
the kernels can have or need to handle.
- (optional) fourth field defines the key RNS, the number of additional moduli
that the relinearization key has relative to the third field. i.e. If `max_rns`
is 3 and `key_rns` is 1 the total max RNS of the relinearization key will be 4.
Note this field is only required for calling the `relin` kernel.

## DATA
`DATA` defines symbols to be used and their attribute(s) (`num_parts`) where
`num_parts` is the number of polynomials that comprise the data variable.

## IMMEDIATE
`IMM` declares a fixed symbol name that can be used for operations that
expect and immediate value(s).


# Generating kernels

The main entry point to the kernel generator is [kerngen.py](kerngen.py). This
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
`to_pisa` method; turning this instruction into a p-ISA instruction class.
Examples can be seen in the simpler implementations given in
[basic.py](./pisa_generators/basic.py). Also, provide a class method
`from_string` that will be passed the args for that command.

For `kerngen` to know of your class that represents a new command of the high
language, simply add an entry into the JSON object in the
[manifest.json](./pisa_generators/manifest.json) file. The key of the outermost
JSON object is the FHE scheme `{BGV, CKKS, ...}`; this key corresponds to a set
of associated operations. Each operation (inner JSON object) consists of the
operation name `OPNAME` as its key and a list containing the class name as the
first entry and the file it is located in as its second. e.g.
```
{
  "SCHEME": {
    "OPNAME": ["ClassName", "filename.py"]
  }
}
```

For kernel writers the reserved words that cannot be used as `OPNAME` are:
```
- CONTEXT
- DATA
- IMM
```


# Writing kernels

The kernel generator has been designed to make it easy to add new kernels.
Kernel files are typically placed in the [pisa_generators](./pisa_generators)
directory to simplify the manifest file as the paths are relative to this
directory.

Before writing the kernel you will require to import the `pisa_operations`
module and any relevant types from the `high_parser` such as the `HighOp` and
`Context`
```python
import high_parser.pisa_operations as pisa_op
from high_parser.pisa_operations import PIsaOp
from high_parser import Context, HighOp, Polys
```

The `Polys` class will be the most commonly used type in most kernels to
represent the inputs and outputs of the operation. This type represents the
polynomials and holds information such as the `name` of symbol that represents
the polynomial, the number of `parts`, and the `rns`.

At a high level kernels convert high-level operations into low-level p-ISA
operations, thus all kernels will need to inherit from `HighOp` and define the
conversion function `to_pisa` as follows
```python
@dataclass
class NewKernel(HighOp):
    """Class representing the high-level NewKernel operation"""

    context: Context
    output: Polys
    input0: Polys

    def to_pisa(self) -> list[PIsaOp]:
        """Return the p-ISA equivalent of the NewKernel operation"""
```

If the kernel consists of an algorithm already represented by an existing
kernel it is possible to import the necessary kernel and compose the new kernel
using existing kernels. For example the `Square` kernel requires a `Mul`
operation
```python
from .basic import Mul

class Square(HighOp):
...
mul = Mul(...)
```
see [square.py](./pisa_generators/square.py) for a complete example of this.

# Mixed operations
You will find that during kernel writing, you will end up with a collection of
either p-ISA operation objects, other kernel objects, or a mixture of both. For
your convenience a useful function `mixed_to_pisa_ops` is provided that can
take all of these sequentially and outputs the required `list[PIsaOp]`.


# Running the tests
Tests are provided in the [tests](./tests) directory and use the
[pytest](https://pypi.org/project/pytest/) framework. To run the tests run the
following
```bash
pytest <test-directory>
```
