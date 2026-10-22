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

1. bare 300 mm barrel with the muzzle clamp as drawn (the default since
   2026-10-21, a collar of two halves on four M3 screws over a wrap of tape; the reference);
2. the same barrel with the muzzle sleeve (`muzzle_sleeve.stl`) in place of
   the clamp: Ø30 bore 215 mm ahead of the barrel, four vents at its root;
   it takes the muzzle ring's rods, 362 mm (the clamp's are 358);
3. a 535 mm barrel: `OVERRIDE = {"BARREL_LEN": 535.0, "MUZZLE_CLAMP": True, "NAME": "stage3v4_long_barrel"}`,
   held by the muzzle clamp (a collar of two halves on four M3 screws, over a wrap of tape)
   300 mm from the shoulder; the rods stay 358 mm.

Same pressure, same balls, at least 10 shots each, the module clamped in the
same rest. Measure:

- the group at 5 m and at 10 m (centre and spread), against the bare barrel;
- velocity, if a chronograph is at hand (otherwise penetration into a
  repeatable target);
- the sleeve's bore after the shots: a marker line drawn along it shows any
  ball touching it;
- the vents: no ball rubbing at their edges, no cracks at the slots;
- the clamp after each barrel's shots: a mark on the barrel at the
  clamp's face shows any slip; then slide the clamp off and check the bore
  under it with a ball (it must pass as freely as elsewhere).

The sleeve's safe length (215 mm) assumes 0.1 mm play in its 25 mm socket,
0.2 mm of bow, and up to 5 mrad of sideways scatter as the ball leaves the
barrel; that last figure is a guess, and this test is what checks it.

---

## Stage 3 v4.4 — charge time and the quiet dump

*Test article: `module/stage3v4_coaxial_chamber.py`* (bleed Ø1.0, as v1.1) — the
mitrailleuse's distributor (`mitrailleuse/mitrailleuse_concepts.py`, concept A)
charges a module only shortly before it fires, and its dump valve empties the
charged ones without firing them. Both rest on numbers to check:

1. **Charge time.** Pilot from 0 to 2 bar through a valve, no ball; time how
   long until a shot is as strong as a fully charged one (a gauge on the
   chamber if one fits, otherwise velocity or penetration against the delay
   between charging and venting: 0.2, 0.3, 0.5, 1 s). The sketch takes 0.5 s
   (the v1.1 bench); its rate (~3.1 shots/s, two barrels charged ahead)
   scales with it.
2. **Quiet dump.** Charge the module through a tyre valve core (pressed),
   let the core go, shut the supply, then vent the supply line through a
   Ø0.5 jet: the pilot must flow back through the core (a check valve that
   way) and out through the jet. The module must not fire:
   the chamber should empty back through the bleed in ~5 s with no pop at the
   muzzle (ball in place, pointed safely). Repeat with Ø0.7 and Ø1.0 to find
   where it starts to fire; the model says Ø1.0 still holds with two modules
   on the jet but not with one, so the jet in the sketch is Ø0.5.

## Mitrailleuse head, bench B — one barrel on a hand slider

*Test article: `mitrailleuse/head_bench.py`* with a v4.4 module: one port of
concept A's firing head (two tyre valve cores, pushers with return springs,
the printed channels) and the rotor's cam laid flat on a slider that clicks
into six stops. Supply on the block's side through a tee with the dump valve
(G1/8 ball valve into a plug drilled Ø0.5), pilot from the top to the
module's pilot port (4 mm hose, ~110 mm as in the gun), gauge on the end.

0. **Set the pins.** Slider at "ждёт", no air: slide each pin up to the
   core's pin, back off 0.5 mm (a feeler), tighten the grub screw. Push the
   slider by hand to where each core starts to hiss (supply on, module off)
   and note the pin travel: the cam gives 1.5 mm, the cores open at ~1.2
   (typical) and must not bottom before 1.8.
1. **Hold.** 2 bar, slider at "ждёт": the gauge stays at 0 (the charge core
   holds the supply). At "зарядка": the gauge rises to the supply; soap
   round the charge pin (its O-ring) and the block's faces.
2. **Charge time.** Hold the slider at a "зарядка" stop for 0.2, 0.3, 0.5,
   1 s, then push straight through to "сброс": compare the shots (velocity
   or penetration). The rotor charges each barrel ~1.55 shot intervals.
3. **Both shut.** Charge, stop at "оба закрыты" for 10 s: the gauge holds
   and the module does not fire; then "сброс" fires it.
4. **Snap.** From "оба закрыты" to "сброс": the module must fire as
   cleanly as from a 2/2 valve on the bench (v1.1). If it is soft, the
   vent core or the Ø4 exhaust is too small, or the pilot volume (block
   0.4 cm3 + hose 0.5 cm3) too large.
5. **Quiet dump.** Charge, stop at "оба закрыты", shut the supply and open
   the dump valve: the gauge falls over ~5 s and the module does not fire
   (as above, now through the real head).
6. **Pressure.** 1-5 repeated at 3 and 4 bar (the rotor's limit is 4 bar
   working).
7. **Life.** 500 strokes "ждёт" -> "выстрелил" and back with a module
   on, then 1 again: no leak at the cores or the O-ring.

## Mitrailleuse head, bench C — the rotor under a quarter of the head, by crank

*Test article: `mitrailleuse/rotor_bench.py`*: the 16-barrel rotor turning
under one quarter of the core block (four ports), cranked through a 1:1
bevel pair and 5:1 spur gears. The stop lever holds a Ø4 steel pin in the
stop disc's notches; the trigger's arm drives it through a coupling pin
that a trip cam under the gear knocks out once a turn (one volley a pull);
the pinion slips on the layshaft between rubber washers while the rotor is
stopped. All but the base, the lever and the
bevel box are the final head's parts. Do bench B first: the pushers and
cores are set the same way.

0. **Slip.** No cores. Trigger held, crank: the rotor turns. Let go: it
   stops and the crank slips. Set the nut so it does not slip while
   turning, and read the slipping force at the knob with a spring scale
   (the model: 6 N; turning a full 16-port head takes up to 4.6 N).
1. **Stop on a step.** Let the trigger go at random points, 50 times, slow
   and fast: the rotor must stop with every pusher either fully up or
   fully down (mark the pins), never on a ramp. Note if the pin ever
   fails to drop in at full crank speed (~1 turn/s).
1a. **One volley a pull.** Hold the trigger and crank: the rotor must stop
   at home after one turn (16 steps; 19 on the 19's disc) with the trigger
   still held, the crank slipping. Let go, pull again: one more turn. 20
   volleys slow and fast, plus a few with the crank jerked hard into the
   stop: it never stops a step early or late, never runs on into a second
   turn, and the coupling pin always pops back up when let go. Read the
   force on the knob as the cam pushes the push pin (the model: ~0.3 N m
   more at the rotor) and the trigger's holding force (the model: 8.4 N).
2. **Pushers.** Cores in, gaps set as on bench B, 2 bar, plugs or gauges
   on the four pilots. Step the crank: each pilot rises two steps ahead
   and drops on its vent step, in order 0, 1, 2, 3.
3. **Crank force.** Spring scale on the knob while turning, at 2 and 4
   bar: the most it takes, against the model's (four ports here, scale to
   16).
4. **Thrust.** Nothing rubs or tilts: the rotor stays clear of the posts,
   the block does not lift on its three screws, the stack runs true on the
   housing's upper 608, the bevels do not climb out of mesh.
5. **Firing.** A v4.4 module on port 0: hold the trigger, crank, it fires
   on its step; let go before it, it does not.
6. **Life.** 1000 steps by crank with stops in between; then 1 and 2
   again.
