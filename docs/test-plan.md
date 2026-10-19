# Prototype Test Plan

> Selector test plan; the selector is frozen for now (see [status.md](status.md)).
> The `module/stage3*` files are barrel modules, not the Stage 3 selector below.

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

## Stage 1 — Rotor/stator interface on a pivot

*Test article: `selector/stage1_interface.py`* — a stator strip cut from the
real geometry (centre to port track, the aligned port and both neighbours)
and the real rotor arm, carried as in Stage 2: hub, Ø8 shaft, two 608 bearings
in a rear bridge on four columns. Stator variant A has a printed face,
variant B a printed body with a 3 mm face plate; rotor and shoe are shared.

The strips were first bolted together; that held the rotor flat at both ends,
stiffer than the arm on its bearings, and could not move the shoe. Bolts never
loaded the shoe itself (spring and line pressure do, as in Stage 2), so the
change is about stiffness and travel, not shoe force.

The rotor turns by hand ±16°, across both neighbours. A Ø3 pin through the arm
into the stator's index sector holds it at whole degrees and at ±14.4°
(the neighbours); degree k sits in row k mod 3. Shims (8×14) between hub and
front bearing set the gap: 0.5 → 2.0, 1.0 → 1.5 (nominal), 1.5 → 1.0,
2.0 → 0.5 mm.

Measure:

- leakage at the aligned port and at the neighbours against angle (0 … ±3°,
  the port leaves the shoe face at ±2.4°) and against gap — the misalignment
  the detent must hold to in Stage 2;
- torque to start and keep the rotor moving (spring scale on the arm end),
  with and without pressure;
- the shoe crossing a neighbouring port: catching on the chamfer, wear.

Compare candidate sealing approaches such as replaceable elastomeric seals while keeping all pressure supply hardware off-the-shelf and rated.

Validate:

- face sealing;
- leakage against misalignment and against gap;
- seal drag;
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

---

## Stage 3 v4.4 — barrel length and the muzzle sleeve

*Test article: `module/stage3v4_coaxial_chamber.py`* — one v4.4 module, shot
three ways, to choose how the mitrailleuse gets its length
(`mitrailleuse/mitrailleuse_concepts.py`, concept A):

1. bare 300 mm barrel, the muzzle ring as drawn (the reference);
2. the same barrel with the muzzle sleeve (`muzzle_sleeve.stl`) in place of
   the muzzle ring: Ø30 bore 215 mm ahead of the barrel, four vents at its
   root, same rods and nuts;
3. a 535 mm barrel: `OVERRIDE = {"BARREL_LEN": 535.0, "MUZZLE_CLAMP": True, "NAME": "stage3v4_long_barrel"}`,
   held by the muzzle clamp (a collar on two M3 screws, over a wrap of tape)
   300 mm from the shoulder; the rods stay 358 mm.

Same pressure, same balls, at least 10 shots each, the module clamped in the
same rest. Measure:

- the group at 5 m and at 10 m (centre and spread), against the bare barrel;
- velocity, if a chronograph is at hand (otherwise penetration into a
  repeatable target);
- the sleeve's bore after the shots: a marker line drawn along it shows any
  ball touching it;
- the vents: no ball rubbing at their edges, no cracks at the slots;
- the clamp after the long barrel's shots: a mark on the barrel at the
  clamp's face shows any slip; then slide the clamp off and check the bore
  under it with a ball (it must pass as freely as elsewhere).

The sleeve's safe length (215 mm) assumes 0.1 mm play in its 25 mm socket,
0.2 mm of bow, and up to 5 mrad of sideways scatter as the ball leaves the
barrel; that last figure is a guess, and this test is what checks it.
