# Prototype Test Plan

The project should validate the pneumatic routing concept incrementally, beginning with the smallest possible test article.

## Stage 0 — Single-channel flow fixture

Build a single stationary printed flow path before introducing any rotor or selector mechanism.

### Existing infrastructure

- workshop air compressor;
- compressor's integrated receiver.

No separate receiver is required for this stage.

### Test setup

Use the compressor's regulated output where suitable. The experimental printed part must remain downstream of pressure regulation and isolation hardware.

Suggested test-chain components:

- regulator and pressure gauge, if the compressor does not already provide a suitable regulated outlet;
- manual shut-off valve;
- rated pneumatic hose/tubing;
- standard metal push-in fittings;
- printed single-channel test fixture;
- replaceable seal where applicable;
- downstream attachment/interface fixture.

The downstream attachment is deliberately application-independent and is not specified by this repository. Its purpose in Stage 0 is simply to provide a repeatable mechanical connection at the output of the printed flow path.

### Stage 0 goals

Validate:

- fitting installation into the printed structure;
- gross leakage;
- leakage around inserts and seals;
- repeatable assembly/disassembly;
- behavior of candidate printed materials;
- downstream attachment stability;
- inspection after repeated pressure/depressure cycles.

Initial tests should vent to atmosphere and begin at the lowest practical regulated pressure.

---

## Stage 1 — Static rotor/stator interface

*Test article: `selector/stage1_interface.py`* — two bolted strips cut from
the real geometry, centre to port track, with the aligned port and both
neighbours. Stator variant A has a printed face, variant B a printed body
with a 3 mm face plate; rotor and shoe are shared.

Introduce the future sealing interface without rotation.

Use two printed mating parts representing rotor and stator with one aligned flow channel.

Compare candidate sealing approaches such as replaceable elastomeric seals while keeping all pressure supply hardware off-the-shelf and rated.

Validate:

- face sealing;
- required clamping/preload;
- leakage across the interface;
- surface wear;
- sensitivity to print finish and flatness.

---

## Stage 2 — Single-channel rotating interface

*Test article: `selector/stage2_rotary.py`* — full-size unit: 25-port
stator, rotor arm with the shoe, rear frame with bearings, bevel pair and
crank. It already carries the valve cam, the pulse valve and the detent, so
indexing and pulse timing can be checked here; Stage 3 then needs no new
mechanism, only more ports fitted.

Add:

- central shaft;
- bearings;
- crank;
- rotor rotation;
- one functional selectable flow path.

The objective is to isolate the mechanical problems of a rotating sealed interface before adding multiple outputs.

Validate:

- crank torque;
- seal drag;
- alignment repeatability;
- leakage while indexed;
- wear after repeated rotations;
- serviceability.

---

## Stage 3 — Small multi-channel selector

Scale the validated interface to 4–6 outputs and add a discrete indexer/detent.

Validate:

- port-to-port isolation;
- indexing accuracy;
- repeatability;
- adjacent-port leakage;
- hose/fitting packaging;
- behavior over repeated selection cycles.

Only after Stage 3 succeeds should the design be scaled toward the 25-channel target.
