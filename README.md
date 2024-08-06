# HERACLES Polynomial Instruction Set Architecture Tools
[![CodeQL](https://github.com/ossf/scorecard-action/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/IntelLabs/hec-p-isa-tools/actions/workflows/codeql-analysis.yml)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/IntelLabs/hec-p-isa-tools/badge)](https://scorecard.dev/viewer/?uri=github.com/IntelLabs/hec-p-isa-tools)
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/9276/badge)](https://www.bestpractices.dev/projects/9276)

## Overview
Intel’s [HERACLES accelerator technology](https://dl.acm.org/doi/10.1145/3560810.3565290)
aims at improving the computational performance of
[Fully Homomorphic Encryption (FHE)](https://en.wikipedia.org/wiki/Homomorphic_encryption).
FHE allows computation to be performed on
encrypted data without having to decrypt the data which brings in
profound and beneficial implications for data privacy and data confidentiality.
However, these benefits come with a significant performance cost which has so far
confined FHE based applications to specific use case archetypes primarily in use
by the regulated industries and government.

Most of the FHE schemes of today perform the computation using very large
polynomial rings, thus requiring considerable compute power and data
movement between main memory and the CPU's registers. HERACLES improves
the performance of FHE by accelerating the computation over the large 
polynomials and optimizing the data movement involved in the computation.

HERACLES introduces a new Polynomial Data type which does not exist in
today's traditional CPUs. For this new polynomial data type, it supports
a new set of novel and fundamental instructions, the Polynomial Instructions
Set Architecture (P-ISA), that operates directly on large polynomials in
a SIMD fashion. We at Intel Labs are developing a new compiler pipeline,
the Encrypted Computing SDK, to make it easier for developers to develop
new implementations of FHE schemes and also integrate with existing libraries.

<p>
<img src="docs/images/HERACLES_SDK_Integration_3rd_Party.png" align="left" width="600" />
  
The Encrypted Computing SDK (or HERACLES SDK) will realize a multistage
transformation (compiler) pipeline, inspired by the
[LLVM Compiler Infrastructure](https://llvm.org/). We have adopted a 
modular approach based on language independent intermediate
representations (IR) that promotes the separation of concerns at each
stage of the pipeline and allowing for dedicated transformations and
optimizations.

This approach also allows for integration with 3rd Party compilers and
transpilers.
<br clear="left">
<br/>
<br/>
</p>

## HERACLES SDK Roadmap: Phased Approach
<p>
<img src="docs/images/HERACLES_SDK_Phased_Approach.png" width=80% height=80% />
<br/>
<br/>
<br/>
</p>

### HERACLES SDK Phase 1: Components and Tasks
<p>
<img src="docs/images/HERACLES_SDK_Phase_1.png" width=80% height=80% />
<br>
<br/>
<br/>
</p>

We are currently at Phase 1, more specifically developing the P-ISA Tools
component which comprises three main tools, a) Kernel Generator, b) Program
Mapper, and c) Functional Modeler Simulator. 
Each tool in this repo is self contained and has its own local README.

Current development is focussed on the Kernel Generator.
Follow the instructions [here](./kerngen) to start experimenting with it.

# Contributing
Intel P-ISA Tools project welcomes external contributions through pull 
requests to the `main` branch.

Please refer to the [Contributing](CONTRIBUTING.md) and
[Code of Conduct](CODE_OF_CONDUCT) documents for additional information on
the contribution acceptance guidelines.

We use signed commits, please remember to sign your commits before making a 
pull request.  See instructions
[here](https://docs.github.com/en/github/authenticating-to-github/managing-commit-signature-verification/signing-commits)
for how to sign commits.

We also use `pre-commit`, so before contributing, please ensure that you run
[pre-commit](https://pre-commit.com) and make sure all checks pass with
```bash
pre-commit install
pre-commit run --all-files
```

Please run the tests provided in each of the components and make sure 
the tests pass.

# Feedback
We encourage feedback and suggestions via
[GitHub Issues](https://github.com/IntelLabs/hec-p-isa-tools/issues) as well
as via
[GitHub Discussions](https://github.com/IntelLabs/hec-p-isa-tools/discussions).
