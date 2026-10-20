# -*- coding: utf-8 -*-
"""
Mitrailleuse concept A: the rear frame, the firing head on a head plate, the bevel box behind it, the rear grip
with the trigger (FreeCAD 1.0).

The head is bench C's (rotor_bench.py) as it is, four quarter blocks instead of one: what passes on the bench
goes into the gun unchanged. The bench's base becomes the head plate, its stop lever is turned so that a rod
reaches it from the grip, and its bevel box goes behind the plate, where the gun has room for it (on the bench it
stands where the head has no block). Frame as in pack_frame.py: z along the barrels (+z to the muzzle), y up,
x to the gunner's left; the bench's stator angles from +x are the gun's (the stop pin at 270 deg is underneath,
the layshaft at 180 deg on the crank's side, the gunner's right).

    head plate .. printed, common to 16 and 19: a disc on the four rails (lugs, M3 grub screws as the pack's
                  plates), its front face at Z0 is the bench base's top. On it, as on the base: the shaft
                  housing's three M4 with nuts behind, the layshaft's boss with its lower 608, the stop lever's
                  pivot post, and twelve posts on R78 (three a quarter) that carry the four guide plates and
                  blocks, an M4 through block and guide plate into each. A tab underneath takes the grip, an ear
                  at the right the bevel box.
    rails ....... pack_frame.py's, now from the head plate's back face (RAIL_Z0) to the front plate. Each grub
                  screw of the head plate and of the rear plate sits in a dimple drilled into the rail: the
                  grip's load goes through the frame as an axial pull in the rails, too much for a bare screw.
    bevel box ... the bench's, without its two columns: its floor (the layshaft's upper 608) on the head plate's
                  back face, two M4 through the plate. The layshaft (an M8 stud) runs from the slip clutch's nut
                  through the boss and the plate into the box; the crank comes out at the right.
    stop lever .. the bench's lever turned round: pivot, pin and the rod's end on one line through the pin
                  (the notch's push still goes through the pivot), the rod pulls its end down past the pin,
                  LEVER_END, between the posts underneath.
    trigger ..... printed, on an M3 pivot across the grip's housing: pulled back, its forward arm pulls the rod
                  down and the pin out of the stop disc. A spring from the grip's front pushes it back: the pin
                  drops into the next notch, the rotor stops on a step.
    rear grip ... printed, one part: a fork onto the head plate's tab (two M4 across), the trigger's housing
                  and guard in front, a raked pistol grip behind.

The trigger rod is a stub: bench C settles the stop (pin travel, the force to hold it); then the rod's ends, the
trigger's arms and a stop at the end of the pull (not drawn yet) get their final sizes. Only the head plate, grip, trigger, lever and bevel box are this
file's parts; the head's own parts are printed from exports/rotor_bench/ (four quarter blocks and guide plates).

Run inside FreeCAD (or freecadcmd):
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/mitrailleuse/rear_frame.py').read())
Prints a report with [OK ] / [FAIL] checks and writes exports/rear_frame/ (STEP, STL in print orientation,
FCStd).
"""

import math
import os

import FreeCAD as App
import Part

try:
    REPO
except NameError:
    try:
        REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        REPO = os.path.expanduser("~/ratling")
# the frame's parameters and functions, without its build, checks and export
PACK_FRAME_LIBRARY = True
exec(open(os.path.join(REPO, "mitrailleuse", "pack_frame.py"), encoding="utf-8").read()
     .split("\n# ---------------------------------------------------------------- build")[0])
# bench C's parts and levels (its frame: z up along the rotor's axis, z = 0 the base's top)
RB = {"REPO": REPO, "ROTOR_BENCH_LIBRARY": True}
exec(open(os.path.join(REPO, "mitrailleuse", "rotor_bench.py"), encoding="utf-8").read(), RB)

NAME = "rear_frame"
OUT_DIR = os.path.join(REPO, "exports", NAME)
Y = V(0, 1, 0)
O = V(0, 0, 0)

# ---------------------------------------------------------------- parameters
Z0 = -228.0                 # head plate's front face (the bench base's top): block's top at Z0 + 123 = -105
HP_T = 10.0
HP_R = 98.0                 # the disc; rail lugs outside it
TAB = (60.0, -124.0)        # grip tab underneath: width across x, lower edge
EAR = (-106.0, 17.0)        # under the bevel box's floor: its outer x, half width in y
BOX_BOLTS = ((-101.0, 10.0), (-101.0, -10.0))
GRIP_BOLTS = ((14.0, -114.0), (-14.0, -114.0))     # M4 along z across the fork and the tab
M4, M4_NUT = 4.5, (7.2, 3.5)
LEVER_END = (-22.0, -27.0)  # the rod's top: past the pin, on the pivot-pin line, its hook outside the stop disc
ROD_D = 2.5                 # steel wire, ends bent through the lever (along z) and the trigger (along x)
TRIG_PIVOT = (-128.0, 16.0)  # y, z; axis along x
TRIG_L1 = 22.0              # pivot to the rod's hole, forward
TRIG_FINGER = (-152.0, 19.0)  # where the finger pulls (y, z)
TRIG_T = 6.0                # thick across x, in a slot TRIG_SLOT wide
TRIG_SLOT = 12.0
OVERTRAVEL = 1.0            # past the pin's clear-of-the-rim point
FORK = (-136.0, -104.0, -16.0, 6.0)          # grip's fork: y0, y1, z0, z1 (the tab sits in z -10..0)
HOUSING = (10.0, -150.0, -120.0, 50.0, 56.0)  # trigger housing: half width, y0, y1, front wall z0, z1
GUARD_Y = (-184.0, -178.0)  # the guard's bottom bar
GRIP_SEC = (30.0, 44.0)     # pistol grip: across x, fore and aft
GRIP_LEN, GRIP_RAKE = 115.0, 20.0
GRIP_AT = (-146.0, -29.0)   # its axis passes here (y, z): the finger's height
TANG = (15.0, -140.0, -104.0, -52.0, -16.0)  # grip's top to the fork: half x, y0, y1, z0, z1
SPRING_AT = -148.0          # trigger return spring along z, from a pocket in the grip's front
F_GRIP = 150.0              # N on the grip (leaning on it, pulling it round), with the head at G_LOAD
DIMPLE = 2.5                # drilled under each grub screw (rail wall 1 mm)
TAB_STRESS_MAX = 15.0       # MPa, printed PETG in bending, half its strength
CLEAR = 0.5

LAY, BRG, PIN = RB["LAY"], RB["BRG"], RB["PIN"]
z_lev0, z_lev1 = RB["z_lev0"], RB["z_lev1"]
pivot, pin_xy = RB["pivot"], RB["pin_xy"]
POST_H = RB["z_plate0"]
post_xy = [polar(RB["POST_R"], a + q) for q in (0, 90, 180, 270) for a in RB["POST_ANGS"]]
DZ = RB["z_floor"][0] - HP_T                     # bench drive -> behind the plate: turned over x, shifted


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def drive_tf(s):
    """Bench drive parts (bevel box, bevels, crank) to behind the head plate: z -> -z, y -> -y."""
    s = s.copy()
    s.rotate(O, X, 180)
    s.translate(V(0, 0, DZ))
    return s


def turn4(s):
    return G.fuse_all([s.rotated(O, Z, q) for q in (0, 90, 180, 270)])


def yz_prism(circles, x0, x1):
    """Prism x0..x1 over the hull of circles (z, y, r) in the gun's y-z plane."""
    p = M["hull_prism"](circles, -x1, -x0)
    p.rotate(O, Y, -90)
    return p


def rod(d, a, b):
    a, b = V(*a), V(*b)
    return Part.makeCylinder(d / 2, (b - a).Length, a, b - a)


# ---------------------------------------------------------------- head plate (local: front face z = 0)
def head_plate():
    z0, z1 = -HP_T, 0.0
    outline = G.fuse_all([cyl(2 * HP_R, z0, z1)] + [M["hull_prism"](
        [(*polar(RAIL_R, a), LUG_R), (*polar(HP_R - 12, a), LUG_R + 4)], z0, z1) for a in RAIL_ANGLES]
        + [box(-TAB[0] / 2, TAB[0] / 2, TAB[1], 0, z0, z1), box(EAR[0], -60, -EAR[1], EAR[1], z0, z1)]).removeSplitter()
    face = bottom(outline, z0)
    holes = [disc(RAIL_HOLE / 2, *polar(RAIL_R, a), z=z0) for a in RAIL_ANGLES]
    holes += [disc(8.0, z=z0), disc(6.0, *LAY, z=z0)]                    # shaft's e-clip, layshaft
    holes += [disc(M4 / 2, *p, z=z0) for p in list(RB["hb_xy"]) + list(BOX_BOLTS) + list(GRIP_BOLTS)]
    s = face.cut(holes).extrude(V(0, 0, HP_T))
    add = [cyl(32.0, 0, RB["Z_BOSS"], *LAY), cyl(12.0, 0, z_lev0 - 0.5, *pivot)]
    add += [cyl(RB["POST_D"], 0, POST_H, *p) for p in post_xy]
    s = s.fuse(G.fuse_all(add))
    cuts = [cyl(BRG[0] + 0.2, RB["Z_BOSS"] - BRG[2], RB["Z_BOSS"] + 1, *LAY), cyl(12.0, -1, RB["Z_BOSS"] - BRG[2] + 0.01, *LAY),
            cyl(3.4, z_lev0 - 16, z_lev0, *pivot)]                     # pivot: M4 from the front
    cuts += [cyl(3.6, POST_H - 16, POST_H + 1, *p) for p in post_xy]    # block: M4 from its top
    cuts += [G.hex_prism(M4_NUT[0], z0 - 1, z0 + M4_NUT[1], *p) for p in RB["hb_xy"]]
    zm = (z0 + z1) / 2
    for a in RAIL_ANGLES:                                               # as pack_frame.plate(), nuts from the front
        rx, ry = polar(RAIL_R, a)
        cuts.append(Part.makeCylinder(GRUB[0] / 2, LUG_R + 2, V(rx, ry, zm), V(*polar(1, a), 0)))
        u0 = RAIL_HOLE / 2 + 1.2
        nut = Part.makeBox(NUT_T + 0.4, NUT_AF + 0.3, HP_T, V(u0, -(NUT_AF + 0.3) / 2, zm - (NUT_AF / math.sqrt(3) + 0.3)))
        nut.rotate(O, Z, a)
        nut.translate(V(rx, ry, 0))
        cuts.append(nut)
    return s.cut(G.fuse_all(cuts)).removeSplitter()


# ---------------------------------------------------------------- stop lever (the bench's, turned round)
def lever():
    py, t = pin_xy[1], RB["LEVER"][2]
    s = G.fuse_all([box(LEVER_END[0] - 5, pivot[0], py - t / 2, py + t / 2, z_lev0, z_lev1),
                    cyl(12.0, z_lev0, z_lev1, *pivot), cyl(10.0, z_lev0, z_lev1, *pin_xy), cyl(8.0, z_lev0, z_lev1, *LEVER_END)])
    return s.cut(G.fuse_all([cyl(4.3, z_lev0 - 1, z_lev1 + 1, *pivot), cyl(PIN[0] - 0.1, z_lev0 - 1, z_lev1 + 1, *pin_xy),
                             cyl(ROD_D + 0.3, z_lev0 - 1, z_lev1 + 1, *LEVER_END)])).removeSplitter()


# ---------------------------------------------------------------- trigger, rod, grip
tip = (TRIG_PIVOT[0], TRIG_PIVOT[1] + TRIG_L1)                          # rod's hole (y, z)


def trigger():
    py, pz = TRIG_PIVOT
    fy, fz = TRIG_FINGER
    s = G.fuse_all([yz_prism([(pz, py, 6.0), (tip[1], tip[0], 4.5)], -TRIG_T / 2, TRIG_T / 2),
                    yz_prism([(pz, py, 5.0), (fz, fy, 4.5), (fz + 1.0, fy - 8.0, 3.5)], -TRIG_T / 2, TRIG_T / 2)])
    hole = lambda d, y, z: rod(d, (-TRIG_T, y, z), (TRIG_T, y, z))
    return s.cut(hole(3.2, py, pz)).cut(hole(ROD_D + 0.3, *tip)).removeSplitter()


def trigger_rod(lever_end, tip_yz):
    """Straight wire from the lever to the trigger, its ends bent through them (stub until bench C)."""
    lx, ly = lever_end
    zl = z_lev0 - ROD_D / 2 - 0.3                       # under the lever, its hook up through it
    ty, tz = tip_yz
    return G.fuse_all([rod(ROD_D, (lx, ly, zl), (0, ty, tz)), rod(ROD_D, (lx, ly, zl), (lx, ly, z_lev1 + 0.5)),
                       rod(ROD_D, (-TRIG_T / 2 - 1.5, ty, tz), (0, ty, tz))])


def grip_axis_z(y):
    return GRIP_AT[1] + (y - GRIP_AT[0]) * math.tan(math.radians(GRIP_RAKE))


def grip():
    y0, y1, z0, z1 = FORK
    hw, hy0, hy1, hz0, hz1 = HOUSING
    w = TAB[0] / 2
    parts = [box(-w, w, y0, y1, z0, z1),
             box(-hw, hw, hy0, hy1, z1 - 0.01, hz1),                                       # housing
             box(-hw, hw, GUARD_Y[0], hy0 + 0.01, hz0, hz1),                               # guard: front
             box(-hw, hw, GUARD_Y[0], GUARD_Y[1], grip_axis_z(GUARD_Y[1]), hz1),           # guard: bottom bar
             box(-TANG[0], TANG[0], TANG[1], TANG[2], TANG[3], TANG[4] + 0.01)]            # grip's top to the fork
    r = GRIP_SEC[0] / 2
    d = (GRIP_SEC[1] - GRIP_SEC[0]) / 2
    g = M["hull_prism"]([(0, -d, r), (0, d, r)], 0, GRIP_LEN)
    g.rotate(O, X, 90 + GRIP_RAKE)
    yt = TANG[1] + 4.0
    g.translate(V(0, yt, grip_axis_z(yt)))
    parts.append(g)
    s = G.fuse_all(parts)
    cuts = [box(-w - 1, w + 1, TAB[1] - 0.2, y1 + 1, -HP_T - 0.2, 0.2),                     # the tab's slot
            box(-TRIG_SLOT / 2, TRIG_SLOT / 2, hy0 - 1, hy1 + 1, z1 - 1, hz0)]             # the trigger's slot
    cuts += [cyl(M4, z0 - 1, z1 + 1, *p) for p in GRIP_BOLTS]
    cuts += [G.hex_prism(M4_NUT[0], z0 - 1, z0 + M4_NUT[1], *p) for p in GRIP_BOLTS]
    cuts.append(rod(3.2, (-hw - 1, TRIG_PIVOT[0], TRIG_PIVOT[1]), (hw + 1, TRIG_PIVOT[0], TRIG_PIVOT[1])))
    zs = grip_axis_z(SPRING_AT) + GRIP_SEC[1] / 2
    cuts.append(rod(SPRING[0] + 0.5, (0, SPRING_AT, zs - SPRING[2]), (0, SPRING_AT, zs + 1)))
    return s.cut(G.fuse_all(cuts)).removeSplitter(), zs


SPRING = (5.0, 0.5, 8.0)    # trigger return spring: OD, wire, its pocket's depth in the grip


def turn_about_x(s, yz, deg):
    s = s.copy()
    s.rotate(V(0, yz[0], yz[1]), X, deg)
    return s


# ---------------------------------------------------------------- build (local, then shifted by Z0)
checks = []
check = lambda ok, text: checks.append((text, bool(ok)))
hp = head_plate()
lev = lever()
trig = trigger()
grip_part, z_spring = grip()

# the stop: the pin from R PIN[1] (in a notch) to PIN[2] (clear of the rim); the lever turns about its pivot
arm_pin = pivot[0] - pin_xy[0]
arm_end = pivot[0] - LEVER_END[0]
phi = math.degrees(math.asin((PIN[2] - PIN[1]) / arm_pin))
end_travel = (PIN[2] - PIN[1]) * arm_end / arm_pin
theta = math.degrees((end_travel + OVERTRAVEL) / TRIG_L1)
lev_on = lev.rotated(V(pivot[0], pivot[1], 0), Z, phi)
pin_on = RB["stop_pin"].rotated(V(pivot[0], pivot[1], 0), Z, phi)
end_on = (pivot[0] - arm_end * math.cos(math.radians(phi)), pivot[1] - arm_end * math.sin(math.radians(phi)))
trig_on = turn_about_x(trig, TRIG_PIVOT, theta)
c, s_ = math.cos(math.radians(theta)), math.sin(math.radians(theta))
tip_on = (TRIG_PIVOT[0] - TRIG_L1 * s_, TRIG_PIVOT[1] + TRIG_L1 * c)
rod_off = trigger_rod(LEVER_END, tip)
rod_on = trigger_rod(end_on, tip_on)
ff = TRIG_FINGER
r_f = math.hypot(ff[0] - TRIG_PIVOT[0], ff[1] - TRIG_PIVOT[1])
finger_travel = math.radians(theta) * r_f
spring_off = G.spring(0, z_spring - SPRING[2], TRIG_FINGER[1] - 4.0, SPRING[0], SPRING[1], 7).translated(V(0, SPRING_AT, 0))

# the head: bench C's parts, the quarters four times
head = {
    "housing": RB["housing"], "stop_disc": RB["stop_disc"], "gear": RB["gear"], "rotor": RB["rotor"],
    "pinion": RB["pinion"], "slip": RB["slip"], "shaft": RB["shaft"], "stop_pin": RB["stop_pin"],
    "blocks": turn4(RB["block"]), "guide_plates": turn4(RB["plate"]), "followers": turn4(RB["followers"]),
    "pins": turn4(RB["pins"]), "springs": turn4(RB["springs"]), "cores": turn4(RB["cores"]),
    "fittings": turn4(RB["fittings"]),
}
zf0, zf1 = RB["z_floor"]
drive_box_b = RB["box"].common(box(-300, 0, -50, 50, zf0, 300))                     # without the bench's columns
for x, y in BOX_BOLTS:
    drive_box_b = drive_box_b.cut(cyl(M4, zf0 - 1, zf1 + 1, x, -y)).cut(G.hex_prism(M4_NUT[0], zf1 - M4_NUT[1], zf1 + 1, x, -y))
drive_box_b = drive_box_b.removeSplitter()
x_b1, x_b2, z_apex, z_lb = RB["x_b1"], RB["x_b2"], RB["z_apex"], RB["z_lb"]
ring = RB["ring"]
drive = {"box": drive_tf(drive_box_b), "bevel_lay": drive_tf(RB["bev_lay"]), "bevel_crank": drive_tf(RB["bev_crank"]),
         "crank": drive_tf(RB["crank"]), "crank_shaft": drive_tf(RB["crank_shaft"]),
         "bearings": drive_tf(G.fuse_all([ring(BRG[0], BRG[1], (LAY[0], LAY[1], z_lb), (LAY[0], LAY[1], z_lb + BRG[2])),
                                          ring(BRG[0], BRG[1], (x_b1[0], 0, z_apex), (x_b1[1], 0, z_apex)),
                                          ring(BRG[0], BRG[1], (x_b2[0], 0, z_apex), (x_b2[1], 0, z_apex))]))}
z_lay_back = -(z_apex - RB["BI"]["small_end_z"] - 1.0) + DZ
z_lay_front = RB["z_nut1"] + 2.0
layshaft = cyl(8.0, z_lay_back, z_lay_front, *LAY)
head_brgs = G.fuse_all([ring(BRG[0], BRG[1], (0, 0, 0), (0, 0, BRG[2])),
                        ring(BRG[0], BRG[1], (0, 0, RB["z_hs"] - BRG[2]), (0, 0, RB["z_hs"])),
                        ring(BRG[0], BRG[1], (LAY[0], LAY[1], RB["Z_BOSS"] - BRG[2]), (LAY[0], LAY[1], RB["Z_BOSS"]))])
z_crank = -z_apex + DZ                                                              # crank shaft's axis, local

# rails in the gun's frame (pack_frame.py's RAIL_Z0 is the head plate's back face); everything else local -> gun by Z0
rail_parts = rails()
rails_local = [r.translated(V(0, 0, -Z0)) for r in rail_parts]

# ---------------------------------------------------------------- checks
wall = lambda a, b: a.distToShape(b)[0]
over = lambda a, b: a.common(b).Volume
bb = hp.BoundBox
check(abs(RAIL_Z0 - (Z0 - HP_T)) < 1e-6, "rails start at the head plate's back face, z %.0f (pack_frame.py's RAIL_Z0)" % RAIL_Z0)
check(G.single_solid(hp) and all(hp.isInside(V(*polar(RAIL_R, a), 0) + V(*polar(RAIL_HOLE / 2 + 1, a + sx * 90), -HP_T / 2),
                                             1e-3, True) for a in RAIL_ANGLES for sx in (-1, 1))
      and over(hp, G.fuse_all(rails_local)) < 1e-3, "head plate one solid, round every rail")
check(max(bb.XLength, bb.YLength) <= BED - 4 and bb.ZLength <= 250, "head plate %.0f x %.0f x %.0f (posts %.0f high) fits"
      " the %.0f bed" % (bb.XLength, bb.YLength, HP_T, POST_H, BED))
for nm, s in (("grip", grip_part), ("trigger", trig), ("lever", lev), ("bevel box", drive["box"])):
    check(G.single_solid(s), "%s one solid" % nm)
gb = grip_part.BoundBox
check(max(gb.XLength, gb.YLength, gb.ZLength) <= BED - 4, "grip %.0f x %.0f x %.0f fits the bed on its side"
      % (gb.XLength, gb.YLength, gb.ZLength))
# the head and the drive land on the plate, nothing in it
land_posts = hp.common(head["guide_plates"].translated(V(0, 0, -0.05))).Volume / 0.05 / len(post_xy)
land_housing = hp.common(RB["housing"].translated(V(0, 0, -0.05))).Volume / 0.05
land_box = hp.common(drive["box"].translated(V(0, 0, 0.05))).Volume / 0.05
check(land_posts >= 80 and land_housing >= 1000 and land_box >= 400,
      "on the plate: each guide plate on its posts over %.0f mm2 a post, the housing's flange over %.0f mm2, the"
      " bevel box's floor over %.0f mm2" % (land_posts, land_housing, land_box))
fixed = {"head plate": hp, "housing": RB["housing"], "guide plates": head["guide_plates"], "blocks": head["blocks"],
         "bevel box": drive["box"], "grip": grip_part, "rails": G.fuse_all(rails_local), "bearings": head_brgs.fuse(drive["bearings"])}
moving = {"rotor": RB["rotor"], "gear": RB["gear"], "stop disc": RB["stop_disc"], "pinion": RB["pinion"], "slip": RB["slip"],
          "layshaft": layshaft, "bevel L": drive["bevel_lay"], "bevel C": drive["bevel_crank"], "crank": drive["crank"],
          "lever": lev, "lever pulled": lev_on, "trigger": trig, "trigger pulled": trig_on, "rod": rod_off,
          "rod pulled": rod_on}
ok_with = {"layshaft": ("head plate", "bearings", "slip", "bevel box", "bevel L", "pinion"), "slip": ("bearings", "layshaft", "head plate"),
           "bevel L": ("bevel C", "bearings", "layshaft"), "bevel C": ("bevel L", "bearings"), "crank": ("bearings",),
           "lever": ("rod",), "lever pulled": ("rod pulled",), "trigger": ("rod",), "trigger pulled": ("rod pulled",),
           "rod": ("lever", "trigger"), "rod pulled": ("lever pulled", "trigger pulled"), "pinion": ("gear", "layshaft"),
           "gear": ("pinion",)}
clash = []
mech = [k for k in moving if k.split()[0] in ("lever", "trigger", "rod")]
for nm, s in moving.items():
    for on, o in list(fixed.items()) + list(moving.items()):
        if on == nm or on in ok_with.get(nm, ()) or nm in ok_with.get(on, ()) or on.split()[0] == nm.split()[0]:
            continue
        if on in mech and nm in mech and (("pulled" in on) != ("pulled" in nm)):
            continue                                    # rest against pulled: never there together
        if s.BoundBox.intersect(o.BoundBox) and over(s, o) > 0.5:
            clash.append(nm + "/" + on)
check(not clash, "nothing that turns or moves (the stack, the drive, lever, rod and trigger at rest and pulled) runs"
      " into the plate, posts, housing, box, grip, rails or each other%s" % (" (" + ", ".join(sorted(set(clash))) + ")" if clash else ""))
posts = G.fuse_all([cyl(RB["POST_D"], 0, POST_H, *p) for p in post_xy])
d_rod = min(wall(r, o) for r in (rod_off, rod_on) for o in (posts, RB["housing"], RB["gear"], RB["stop_disc"]))
d_rod_grip = min(wall(r, grip_part) for r in (rod_off, rod_on))
d_lev = min(wall(l, o) for l in (lev, lev_on) for o in (posts, RB["housing"], RB["stop_disc"]))
check(min(d_rod, d_rod_grip, d_lev) >= CLEAR, "rod %.1f mm clear of the posts, housing, gear and stop disc, %.1f of the"
      " grip's slot; lever %.1f clear of the posts, housing and disc" % (d_rod, d_rod_grip, d_lev))
d_rail = min(wall(r, o) for r in rails_local for o in (head["blocks"], head["guide_plates"], head["fittings"], RB["slip"], drive["box"]))
check(d_rail >= RAIL_CLEAR, "rails %.1f mm clear of the blocks, guide plates, fittings, slip clutch and bevel box" % d_rail)
# crank: the arm and knob swept round the crank shaft
cb = drive["crank"].BoundBox
r_sweep = max(math.hypot(y, z - z_crank) for y in (cb.YMin, cb.YMax) for z in (cb.ZMin, cb.ZMax))
sweep = Part.makeCylinder(r_sweep, cb.XLength, V(cb.XMin, 0, z_crank), X)
d_crank = min(wall(sweep, o) for o in (hp, grip_part, G.fuse_all(rails_local), head["blocks"], head["fittings"]))
check(d_crank >= 5.0, "crank R%.0f swept round its shaft at z %.0f: %.0f mm clear of the plate, grip, rails and head"
      % (RB["CRANK_R"], z_crank + Z0, d_crank))
# the stop through the rod
pin_clear = PIN[2] - PIN[0] / 2 - RB["STOP"][0]
check(pin_clear >= 0.3, "lever %.0f : %.0f (pin : rod), turns %.1f deg: the rod pulls %.1f mm, the pin comes %.1f mm"
      " clear of the disc's rim" % (arm_pin, arm_end, phi, end_travel, pin_clear))
f_hold = RB["f_trig"] * RB["LEVER"][1] / arm_end                  # the bench's holding force at its lever's end
f_finger = f_hold * TRIG_L1 / r_f
check(theta <= 35.0 and finger_travel <= 14.0, "trigger %.0f : %.0f, pulled %.0f deg (%.0f mm over the pin's need):"
      " %.0f mm at the finger, ~%.0f N to hold it (%.0f N at the rod, the bench's estimate) + its spring"
      % (TRIG_L1, r_f, theta, OVERTRAVEL, finger_travel, f_finger, f_hold))
# the hand
y_f = TRIG_FINGER[0]
reach = TRIG_FINGER[1] + 4.5 - (grip_axis_z(y_f) - GRIP_SEC[1] / 2)
room_z = HOUSING[3] - (TRIG_FINGER[1] + 4.5)
room_y = HOUSING[1] - GUARD_Y[1]
check(60 <= reach <= 80 and room_z >= 25 and room_y >= 25, "hand: %.0f mm from the grip's back to the trigger's face,"
      " %.0f x %.0f in the guard for a gloved finger; grip %.0f x %.0f, %.0f long, raked %.0f deg"
      % (reach, room_z, room_y, GRIP_SEC[0], GRIP_SEC[1], GRIP_LEN, GRIP_RAKE))
d_hand = wall(trig_on, grip_part.common(box(-50, 50, -250, HOUSING[1], -150, HOUSING[3] - 0.01)))
sp_pulled = SPRING[2] + d_hand
check(sp_pulled >= 7 * SPRING[1] + 1.0, "pulled, the trigger stays %.0f mm off the grip, its spring at %.0f mm (solid %.1f)"
      % (d_hand, sp_pulled, 7 * SPRING[1]))
# loads: the grip's pull and the head at G_LOAD go into the rails as a frame, through the head plate and the rear
# plate (plates and rails a box, rails pulled and pushed by the bending)
printed = [hp, grip_part, trig, lev, drive["box"], RB["housing"], RB["stop_disc"], RB["gear"], RB["rotor"], RB["pinion"],
           head["blocks"], head["guide_plates"], head["followers"], drive["bevel_lay"], drive["bevel_crank"], drive["crank"]]
steel = [RB["shaft"], layshaft, head["pins"], head["cores"], head["fittings"], head_brgs, drive["bearings"],
         drive["crank_shaft"], RB["stop_pin"]]
m_head = (sum(s.Volume for s in printed) * DENSITY["printed"] + sum(s.Volume for s in steel) * 7.85) / 1e6
cg = sum(s.Volume * s.BoundBox.Center.z for s in printed) / sum(s.Volume for s in printed) + Z0
z_mid = z_rp + PLATE_T / 2
z_grip = grip_axis_z(FORK[0] - GRIP_LEN / 2 * math.cos(math.radians(GRIP_RAKE))) + Z0
moment = F_GRIP * (z_mid - z_grip) + m_head * 9.81 * G_LOAD * (z_mid - cg)
n_rail = moment / (4 * RAIL_R * math.cos(math.radians(45)))
dimple = DIMPLE * RAIL[1] * 1.5 * RAIL_YIELD
check(n_rail <= dimple / 2, "frame: %.0f N on the grip and the head (%.1f kg) at %.0f g, %.0f N m at the rear plate:"
      " %.0f N along each rail through a grub screw in a Ø%.1f dimple (bears %.0f N)"
      % (F_GRIP, m_head, G_LOAD, moment / 1000, n_rail, DIMPLE, dimple))
y_mid = FORK[0] - GRIP_LEN / 2 * math.cos(math.radians(GRIP_RAKE))
tab_m = F_GRIP * (FORK[1] - y_mid)                  # pulled back at the grip's middle, about the fork's top edge
tab_w = TAB[0] * HP_T ** 2 / 6
check(tab_m / tab_w <= TAB_STRESS_MAX, "tab: %.0f N pulled back at the grip's middle bends it %.0f MPa (<= %.0f)"
      % (F_GRIP, tab_m / tab_w, TAB_STRESS_MAX))
rail_len = z_fs - RAIL_Z0
lay_len = z_lay_front - z_lay_back

report = [
    "Mitrailleuse concept A: rear frame (head plate, bevel box, rear grip, trigger), bench C's head, common to 16 and 19",
    "  head plate z %.0f..%.0f (front face = the bench base's top), Ø%.0f + 4 rail lugs, %.0f cm3 (%.0f-%.0f g);"
    " head's block top at z %.0f, fittings to z %.0f" % (Z0 - HP_T, Z0, 2 * HP_R, hp.Volume / 1000,
                                                       hp.Volume / 1000 * DENSITY["printed"], hp.Volume / 1000 * DENSITY["solid"],
                                                       Z0 + RB["z_top"], Z0 + head["fittings"].BoundBox.ZMax),
    "  rails now z %.0f..%.1f: 4 x %.0f mm" % (RAIL_Z0, z_fs, rail_len),
    "  bevel box behind the plate to z %.0f, crank shaft at z %.0f on the right; layshaft M8 x %.0f (z %.0f..%.0f)"
    % (drive["box"].BoundBox.ZMin + Z0, z_crank + Z0, lay_len, z_lay_back + Z0, z_lay_front + Z0),
    "  grip %.0f cm3, trigger %.0f cm3, lever %.0f cm3; head and rear frame ~%.1f kg, its CG at z %.0f"
    % (grip_part.Volume / 1000, trig.Volume / 1000, lev.Volume / 1000, m_head, cg),
    "  bought: 12 x M4 x 50 (blocks), 3 x M4 x 16 + nuts (housing), 2 x M4 x 25 + nuts (box), 2 x M4 x 30 + nuts (grip),"
    " M4 x 40 (lever), M3 x 20 + nut (trigger), 4 x M3 x 8 grub + nuts, M8 stud %.0f, wire Ø%.1f ~%.0f mm, spring"
    " %.1f x %.0f x 30" % (lay_len, ROD_D, rod_off.BoundBox.YLength + 20, SPRING[1], SPRING[0]),
] + ["  [%s] %s" % ("OK " if ok else "FAIL", t) for t, ok in checks]
print("\n".join(report))

# ---------------------------------------------------------------- document and exports
os.makedirs(OUT_DIR, exist_ok=True)
sc = FV.Scene(NAME)
FV.STYLES.setdefault("alu", ((0.80, 0.82, 0.86), 0))
FV.STYLES.setdefault("barrel", ((0.45, 0.46, 0.50), 0))
T = V(0, 0, Z0)
# the document in the gun's frame turned so that FreeCAD's Front looks at the crank's side: z (to the muzzle) to the
# right, y up
SHOW = FV.VIEW_ROT.inverse().multiply(App.Placement(App.Matrix(0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1)))


def add(group, name, shape, style, offset=None):
    s = shape.copy()
    if offset is not None:
        s.translate(offset)
    s.Placement = SHOW.multiply(s.Placement)
    sc.add(group, name, s, style)


for n, s, st in (("Head_plate", hp, "frame"), ("Grip", grip_part, "printed"), ("Trigger", trig, "rotor"),
                 ("Stop_lever", lev, "rotor"), ("Bevel_box", drive["box"], "frame")):
    add("Rear_frame", n, s, st, offset=T)
for n, st in (("housing", "stator"), ("blocks", "stator"), ("guide_plates", "plate"), ("followers", "printed"),
              ("rotor", "rotor"), ("gear", "drive"), ("pinion", "drive"), ("stop_disc", "printed")):
    add("Head", "Head_" + n, head[n], st, offset=T)
add("Head", "Bevel_gears", drive["bevel_lay"].fuse(drive["bevel_crank"]), "drive", offset=T)
add("Head", "Crank", drive["crank"], "printed", offset=T)
for n, s, st in (("Trigger_rod", rod_off, "steel"), ("Trigger_spring", spring_off, "steel"), ("Stop_pin", RB["stop_pin"], "steel"),
                 ("Shaft", RB["shaft"], "steel"), ("Layshaft", layshaft, "steel"), ("Crank_shaft", drive["crank_shaft"], "steel"),
                 ("Bearings", head_brgs.fuse(drive["bearings"]), "steel"), ("Slip_clutch", RB["slip"], "oring"),
                 ("Valve_cores", head["cores"], "steel"), ("Pins", head["pins"], "steel"), ("Fittings", head["fittings"], "steel")):
    add("Bought", n, s, st, offset=T)
add("Pulled", "Trigger_pulled", trig_on, "ghost", offset=T)
add("Pulled", "Lever_pulled", lev_on, "ghost", offset=T)
add("Pulled", "Rod_pulled", rod_on, "ghost", offset=T)
key, tag = "j_rings_4_12", "A16"
mods = module_parts(key)
add("Pack", "A16_rails", Part.makeCompound(rail_parts), "alu")
for side in ("rear", "front"):
    add("Pack", "A16_%s_plate" % side, plate(key, side)[0], "frame")
for style, names in (("stator", ("rp", "fp", "rear_yoke", "front_yoke", "muzzle_ring")), ("ghost", ("chamber",)),
                     ("barrel", ("barrel",)), ("steel", ("hardware", "fitting"))):
    add("Pack", "A16_" + "_".join(names), Part.makeCompound([m[n] for m in mods for n in names]), style)
sc.finish(hidden_groups=("Pulled",))
sc.doc.saveAs(os.path.join(OUT_DIR, NAME + ".FCStd"))

import MeshPart


def write(shape, name, rot=None):
    s = shape.copy()
    if rot is not None:
        s.rotate(O, *rot)
    s.translate(V(-s.BoundBox.Center.x, -s.BoundBox.Center.y, -s.BoundBox.ZMin))
    s.exportStep(os.path.join(OUT_DIR, name + ".step"))
    MeshPart.meshFromShape(Shape=s, LinearDeflection=0.02, AngularDeflection=0.1).write(
        os.path.join(OUT_DIR, name + ".stl"))


write(hp, "head_plate")                                     # back face on the bed, posts up
write(grip_part, "rear_grip", (Y, 90))                      # on its side
write(trig, "trigger", (Y, 90))
write(lev, "stop_lever")
write(drive_box_b, "bevel_box", (X, 90))                    # on its side, as the bench's
with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
    f.write("\n".join(report) + "\n")
print("written to", OUT_DIR)
