# Changelog

### 2024-07-11
- Updated SPAD capacity to reflect change from 64MB to 48MB.
- Updated the range of values for `cnop` parameters.
- Updated `rshuffle` to reflect slotting rules for 4KCE.

### 2024-01-23
- Updated `rshuffle` to reflect latency changes and rules for 4KCE.
- Updated `nload` to reflect the lack of support for multiple routing tables.
- Updated HBM capacity to reflect change from 64GB to 48GB.
- No keygen updates yet because the feature is work in progress.

### 2023-07-25
- Updated throughput for CInsts `cload`, and `nload`.
- Updated throughput and latency for `cstore`, and `bload`.
- Updated latency of `xstore`.
- Updated `rshuffle` to reflect the discontinuation of `wait_cyc` parameter.

### 2023-07-24
- Added XInstruction `sub`, required by CKKS scheme P-ISA kernels.

### 2023-06-30
- Updated latencies of XInstruction `rshuffle` based on Sim0.9 version.

### 2023-06-12
- XInstruction `exit` op name is now `bexit` to match the ISA spec, as required by Sim0.9.
- CInstructions `bload` and `bones` format changed to match philosophy of dests before sources.
