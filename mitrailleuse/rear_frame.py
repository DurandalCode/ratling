# -*- coding: utf-8 -*-
"""
Mitrailleuse concept A: the rear frame, the firing head on a head plate, the bevel box behind it, the stop's
pull rod (FreeCAD 1.0).

The head is bench C's (rotor_bench.py) as it is, four quarter blocks instead of one: what passes on the bench
goes into the gun unchanged. The bench's base becomes the head plate, its stop lever is turned so that a rod
reaches it from underneath, and its bevel box goes behind the plate, where the gun has room for it (on the bench it
stands where the head has no block). Frame as in pack_frame.py: z along the barrels (+z to the muzzle), y up,
x to the gunner's left; the bench's stator angles from +x are the gun's (the stop pin at 270 deg is underneath,
the layshaft at 180 deg on the crank's side, the gunner's right).

    head plate .. printed, one for 16 and one for 19 (the posts differ): a disc on the four rails (lugs, M3 grub screws as the pack's
                  plates), its front face at Z0 is the bench base's top. On it, as on the base: the shaft
                  housing's three M4 with nuts behind, the layshaft's boss with its lower 608, the stop lever's
                  pivot post, and twelve posts on R78 (three a block) that carry the four guide plates and
                  blocks, an M4 through block and guide plate into each. A tab underneath (two M4 holes) is where
                  the rear grip goes, an ear at the right takes the bevel box.
    rails ....... pack_frame.py's, now from the head plate's back face (RAIL_Z0) to the front plate. Each grub
                  screw of the head plate and of the rear plate sits in a dimple drilled into the rail: a
                  grip's load goes through the frame as an axial pull in the rails, too much for a bare screw.
    bevel box ... the bench's, without its two columns: its floor (the layshaft's upper 608) on the head plate's
                  back face, two M4 through the plate. The layshaft (an M8 stud) runs from the slip clutch's nut
                  through the boss and the plate into the box; the crank comes out at the right.
    stop lever .. the head's (bench C's stop lever with its disconnector): the stop pin, the coupling pin's
                  hole and the tab; its spring on a post outside the pin, as on the bench's base.
    trigger arm . the gun's: under the stop lever on the same pivot, turned round from the bench's so that
                  pivot, pin and the rod's end lie on one line (the notch's push still goes through the pivot);
                  the rod pulls its end down past the pin, LEVER_END, between the posts underneath. It carries
                  the coupling pin and its spring, as the bench's, and rests on the stop lever's tab.
    pull rod .... a stub: steel wire from the arm's end down to PULL under the head plate's tab, where a
                  trigger will take it. Pulled down by end_travel, the pin comes out of the stop disc; let go, a
                  spring pushes it back, the pin drops into the next notch, the rotor stops on a step. Held
                  down, the trip cam lets the stop lever go once a turn and the rotor stops at home after one
                  volley; letting go of the trigger couples the levers again (rotor_bench.py, docs/rotor.md).

Not drawn on purpose: the rear grip and its trigger. Their kind is not chosen yet (Maxim's spade grips with a
thumb trigger, a flintlock pistol's grip, ...); whatever it is, it bolts to the tab and pulls the rod's end down
by end_travel with about f_hold (the report gives both). The rod's ends get their final sizes once bench C
settles the stop (pin travel, the force to hold it). Only the head plate, lever and bevel box are this file's
parts; the head's own parts are printed from exports/rotor_bench/ (four quarter blocks and guide plates).

HEAD_N = 19 before exec builds the 19's: bench C's head with ROTOR_N = 19 (blocks of 5 + 5 + 5 + 4 ports, its own
rotor and stop disc), the posts under its blocks, the 19 pack; writes exports/rear_frame19/.

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
try:
    HEAD_N                  # barrels: 16 or 19
except NameError:
    HEAD_N = 16
# the frame's parameters and functions, without its build, checks and export
PACK_FRAME_LIBRARY = True
exec(open(os.path.join(REPO, "mitrailleuse", "pack_frame.py"), encoding="utf-8").read()
     .split("\n# ---------------------------------------------------------------- build")[0])
# bench C's parts and levels (its frame: z up along the rotor's axis, z = 0 the base's top)
RB = {"REPO": REPO, "ROTOR_BENCH_LIBRARY": True, "ROTOR_N": HEAD_N}
exec(open(os.path.join(REPO, "mitrailleuse", "rotor_bench.py"), encoding="utf-8").read(), RB)

NAME = "rear_frame" if HEAD_N == 16 else "rear_frame%d" % HEAD_N
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
GRIP_BOLTS = ((14.0, -114.0), (-14.0, -114.0))     # M4 along z through the tab, for the grip
M4, M4_NUT = 4.5, (7.2, 3.5)
LEVER_END = (-22.0, -27.0)  # the rod's top: past the pin, on the pivot-pin line, its hook outside the stop disc
ROD_D = 2.5                 # steel wire, its top bent up through the trigger arm
PULL = (0.0, -128.0)        # the rod's lower end (x, y), under the tab, in the lever's plane
F_GRIP = 150.0              # N on a grip (leaning on it, pulling it round), with the head at G_LOAD
GRIP_AT = (-170.0, -60.0)   # where that load acts (y, z local): any grip on the tab, roughly
DIMPLE = 2.5                # drilled under each grub screw (rail wall 1 mm)
TAB_STRESS_MAX = 15.0       # MPa, printed PETG in bending, half its strength
CLEAR = 0.5

LAY, BRG, PIN = RB["LAY"], RB["BRG"], RB["PIN"]
z_lev0, z_lev1 = RB["z_lev0"], RB["z_lev1"]
z_arm0, z_arm1 = RB["z_arm0"], RB["z_arm1"]
pivot, pin_xy = RB["pivot"], RB["pin_xy"]
POST_H = RB["z_plate0"]
post_xy = RB["GUN"]["post_xy"]                  # three a block, between its ports
DZ = RB["z_floor"][0] - HP_T                     # bench drive -> behind the plate: turned over x, shifted


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def drive_tf(s):
    """Bench drive parts (bevel box, bevels, crank) to behind the head plate: z -> -z, y -> -y."""
    s = s.copy()
    s.rotate(O, X, 180)
    s.translate(V(0, 0, DZ))
    return s


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
    add = [cyl(32.0, 0, RB["Z_BOSS"], *LAY), cyl(12.0, 0, z_arm0 - 0.5, *pivot), RB["lever_spring_post"]()]
    add += [cyl(RB["POST_D"], 0, POST_H, *p) for p in post_xy]
    s = s.fuse(G.fuse_all(add))
    cuts = [cyl(BRG[0] + 0.2, RB["Z_BOSS"] - BRG[2], RB["Z_BOSS"] + 1, *LAY), cyl(12.0, -1, RB["Z_BOSS"] - BRG[2] + 0.01, *LAY),
            cyl(3.4, z_arm0 - 16, z_arm0, *pivot)]                     # pivot: M4 from the front
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


# ---------------------------------------------------------------- trigger arm (the bench's, turned round)
def trigger_arm():
    s = RB["trigger_arm_shape"](LEVER_END[0] - 5, pivot[0] + RB["TAB_AT"] + 4).fuse(cyl(8.0, z_arm0, z_arm1, *LEVER_END))
    return s.cut(cyl(ROD_D + 0.3, z_arm0 - 1, z_arm1 + 1, *LEVER_END)).removeSplitter()


# ---------------------------------------------------------------- pull rod (a stub)
def pull_rod(lever_end, low):
    """Straight wire from under the lever to its lower end, the top bent up through the lever."""
    lx, ly = lever_end
    zl = z_arm0 - ROD_D / 2 - 0.3
    return G.fuse_all([rod(ROD_D, (lx, ly, zl), (low[0], low[1], zl)), rod(ROD_D, (lx, ly, zl), (lx, ly, z_arm1 - 0.5))])


# ---------------------------------------------------------------- build (local, then shifted by Z0)
checks = []
check = lambda ok, text: checks.append((text, bool(ok)))
hp = head_plate()
arm = trigger_arm()
stop_lever = RB["stop_lever"]
lev = Part.makeCompound([stop_lever, arm])          # the stop's two levers, for the weights

# the stop: the pin from R PIN[1] (in a notch) to PIN[2] (clear of the rim); the lever turns about its pivot
arm_pin = pivot[0] - pin_xy[0]
arm_end = pivot[0] - LEVER_END[0]
phi = math.degrees(math.asin((PIN[2] - PIN[1]) / arm_pin))
end_travel = (PIN[2] - PIN[1]) * arm_end / arm_pin
arm_on = arm.rotated(V(pivot[0], pivot[1], 0), Z, phi)
stop_lever_on = stop_lever.rotated(V(pivot[0], pivot[1], 0), Z, phi)
end_on = (pivot[0] - arm_end * math.cos(math.radians(phi)), pivot[1] - arm_end * math.sin(math.radians(phi)))
pull_on = (end_on[0] + (PULL[0] - LEVER_END[0]), end_on[1] + (PULL[1] - LEVER_END[1]))
rod_off = pull_rod(LEVER_END, PULL)
rod_on = pull_rod(end_on, pull_on)
pull_travel = math.hypot(pull_on[0] - PULL[0], pull_on[1] - PULL[1])

# the head: bench C's parts, its blocks round the stator (four quarters at 16; 5 + 5 + 5 + 4 ports at 19)
head = {
    "housing": RB["housing"], "stop_disc": RB["stop_disc"], "gear": RB["gear"], "rotor": RB["rotor"],
    "pinion": RB["pinion"], "slip": RB["slip"], "shaft": RB["shaft"], "stop_pin": RB["stop_pin"],
}
head.update({k: RB["GUN"][k] for k in ("blocks", "guide_plates", "followers", "pins", "springs", "cores", "fittings")})
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
for nm, s in (("trigger arm", arm), ("bevel box", drive["box"])):
    check(G.single_solid(s), "%s one solid" % nm)
# the head and the drive land on the plate, nothing in it
land_posts = hp.common(head["guide_plates"].translated(V(0, 0, -0.05))).Volume / 0.05 / len(post_xy)
land_housing = hp.common(RB["housing"].translated(V(0, 0, -0.05))).Volume / 0.05
land_box = hp.common(drive["box"].translated(V(0, 0, 0.05))).Volume / 0.05
check(land_posts >= 80 and land_housing >= 1000 and land_box >= 400,
      "on the plate: each guide plate on its posts over %.0f mm2 a post, the housing's flange over %.0f mm2, the"
      " bevel box's floor over %.0f mm2" % (land_posts, land_housing, land_box))
fixed = {"head plate": hp, "housing": RB["housing"], "guide plates": head["guide_plates"], "blocks": head["blocks"],
         "bevel box": drive["box"], "rails": G.fuse_all(rails_local), "bearings": head_brgs.fuse(drive["bearings"])}
moving = {"rotor": RB["rotor"], "gear": RB["gear"], "stop disc": RB["stop_disc"], "pinion": RB["pinion"], "slip": RB["slip"],
          "layshaft": layshaft, "bevel L": drive["bevel_lay"], "bevel C": drive["bevel_crank"], "crank": drive["crank"],
          "lever": stop_lever, "lever pulled": stop_lever_on, "arm": arm, "arm pulled": arm_on, "rod": rod_off,
          "rod pulled": rod_on, "trip cam": RB["trip_cam"]}
ok_with = {"layshaft": ("head plate", "bearings", "slip", "bevel box", "bevel L", "pinion"), "slip": ("bearings", "layshaft", "head plate"),
           "bevel L": ("bevel C", "bearings", "layshaft"), "bevel C": ("bevel L", "bearings"), "crank": ("bearings",),
           "lever": ("rod", "arm"), "lever pulled": ("rod pulled", "arm pulled"), "arm": ("rod", "lever"),
           "arm pulled": ("rod pulled", "lever pulled"), "rod": ("arm",), "rod pulled": ("arm pulled",),
           "pinion": ("gear", "layshaft"), "gear": ("pinion", "trip cam")}
clash = []
mech = [k for k in moving if k.split()[0] in ("lever", "arm", "rod")]
for nm, s in moving.items():
    for on, o in list(fixed.items()) + list(moving.items()):
        if on == nm or on in ok_with.get(nm, ()) or nm in ok_with.get(on, ()) or on.split()[0] == nm.split()[0]:
            continue
        if on in mech and nm in mech and (("pulled" in on) != ("pulled" in nm)):
            continue                                    # rest against pulled: never there together
        if s.BoundBox.intersect(o.BoundBox) and over(s, o) > 0.5:
            clash.append(nm + "/" + on)
check(not clash, "nothing that turns or moves (the stack, the drive, lever and rod at rest and pulled) runs"
      " into the plate, posts, housing, box, rails or each other%s" % (" (" + ", ".join(sorted(set(clash))) + ")" if clash else ""))
posts = G.fuse_all([cyl(RB["POST_D"], 0, POST_H, *p) for p in post_xy])
d_rod = min(wall(r, o) for r in (rod_off, rod_on) for o in (posts, RB["housing"], RB["gear"], RB["stop_disc"]))
d_rod_hp = min(wall(r, hp) for r in (rod_off, rod_on))
d_lev = min(wall(l, o) for l in (stop_lever, stop_lever_on, arm, arm_on) for o in (posts, RB["housing"], RB["stop_disc"]))
check(min(d_rod, d_rod_hp, d_lev) >= CLEAR, "rod %.1f mm clear of the posts, housing, gear and stop disc, %.1f of the"
      " plate; levers %.1f clear of the posts, housing and disc" % (d_rod, d_rod_hp, d_lev))
cam_sweep = RB["sweep"]
d_cam = min(wall(cam_sweep, o) for o in (posts, arm, arm_on, rod_off, rod_on, hp))
check(d_cam >= CLEAR, "trip cam's sweep %.1f mm clear of the posts, trigger arm, rod and plate" % d_cam)
d_rail = min(wall(r, o) for r in rails_local for o in (head["blocks"], head["guide_plates"], head["fittings"], RB["slip"], drive["box"]))
check(d_rail >= RAIL_CLEAR, "rails %.1f mm clear of the blocks, guide plates, fittings, slip clutch and bevel box" % d_rail)
# crank: the arm and knob swept round the crank shaft
cb = drive["crank"].BoundBox
r_sweep = max(math.hypot(y, z - z_crank) for y in (cb.YMin, cb.YMax) for z in (cb.ZMin, cb.ZMax))
sweep = Part.makeCylinder(r_sweep, cb.XLength, V(cb.XMin, 0, z_crank), X)
d_crank = min(wall(sweep, o) for o in (hp, G.fuse_all(rails_local), head["blocks"], head["fittings"]))
check(d_crank >= 5.0, "crank R%.0f swept round its shaft at z %.0f: %.0f mm clear of the plate, rails and head"
      % (RB["CRANK_R"], z_crank + Z0, d_crank))
# the stop through the rod
pin_clear = PIN[2] - PIN[0] / 2 - RB["STOP"][0]
check(pin_clear >= 0.3, "lever %.0f : %.0f (pin : rod), turns %.1f deg: the rod pulls %.1f mm, the pin comes %.1f mm"
      " clear of the disc's rim" % (arm_pin, arm_end, phi, end_travel, pin_clear))
f_hold = RB["f_trig"] * RB["LEVER"][1] / arm_end                  # the bench's holding force at its lever's end
check(PULL[1] < TAB[1] + 0.1, "for the trigger (not drawn): pull the rod's end at (%.0f, %.0f, %.0f) %.1f mm down, hold it"
      " with ~%.0f N (the bench's estimate) plus the return spring" % (PULL[0], PULL[1], Z0 + z_arm0 - ROD_D / 2 - 0.3,
                                                                       pull_travel, f_hold))
# loads: a grip's pull and the head at G_LOAD go into the rails as a frame, through the head plate and the rear
# plate (plates and rails a box, rails pulled and pushed by the bending)
printed = [hp, stop_lever, arm, RB["trip_cam"], drive["box"], RB["housing"], RB["stop_disc"], RB["gear"], RB["rotor"], RB["pinion"],
           head["blocks"], head["guide_plates"], head["followers"], drive["bevel_lay"], drive["bevel_crank"], drive["crank"]]
steel = [RB["shaft"], layshaft, head["pins"], head["cores"], head["fittings"], head_brgs, drive["bearings"],
         drive["crank_shaft"], RB["stop_pin"]]
m_head = (sum(s.Volume for s in printed) * DENSITY["printed"] + sum(s.Volume for s in steel) * 7.85) / 1e6
cg = sum(s.Volume * s.BoundBox.Center.z for s in printed) / sum(s.Volume for s in printed) + Z0
z_mid = z_rp + PLATE_T / 2
z_grip = GRIP_AT[1] + Z0
moment = F_GRIP * (z_mid - z_grip) + m_head * 9.81 * G_LOAD * (z_mid - cg)
n_rail = moment / (4 * RAIL_R * math.cos(math.radians(45)))
dimple = DIMPLE * RAIL[1] * 1.5 * RAIL_YIELD
check(n_rail <= dimple / 2, "frame: %.0f N on the grip and the head (%.1f kg) at %.0f g, %.0f N m at the rear plate:"
      " %.0f N along each rail through a grub screw in a Ø%.1f dimple (bears %.0f N)"
      % (F_GRIP, m_head, G_LOAD, moment / 1000, n_rail, DIMPLE, dimple))
tab_m = F_GRIP * (-HP_R - GRIP_AT[0])                 # pulled back, about the tab's root
tab_w = TAB[0] * HP_T ** 2 / 6
check(tab_m / tab_w <= TAB_STRESS_MAX, "tab: %.0f N pulled back %.0f mm under its root bends it %.0f MPa (<= %.0f)"
      % (F_GRIP, -HP_R - GRIP_AT[0], tab_m / tab_w, TAB_STRESS_MAX))
rail_len = z_fs - RAIL_Z0
lay_len = z_lay_front - z_lay_back

report = [
    "Mitrailleuse concept A: rear frame (head plate, bevel box, stop's pull rod), bench C's head, %d barrels (blocks of %s)"
    % (HEAD_N, " + ".join(str(n) for n in RB["BLOCK_PORTS"])),
    "  head plate z %.0f..%.0f (front face = the bench base's top), Ø%.0f + 4 rail lugs, %.0f cm3 (%.0f-%.0f g);"
    " head's block top at z %.0f, fittings to z %.0f" % (Z0 - HP_T, Z0, 2 * HP_R, hp.Volume / 1000,
                                                       hp.Volume / 1000 * DENSITY["printed"], hp.Volume / 1000 * DENSITY["solid"],
                                                       Z0 + RB["z_top"], Z0 + head["fittings"].BoundBox.ZMax),
    "  rails now z %.0f..%.1f: 4 x %.0f mm" % (RAIL_Z0, z_fs, rail_len),
    "  bevel box behind the plate to z %.0f, crank shaft at z %.0f on the right; layshaft M8 x %.0f (z %.0f..%.0f)"
    % (drive["box"].BoundBox.ZMin + Z0, z_crank + Z0, lay_len, z_lay_back + Z0, z_lay_front + Z0),
    "  levers %.0f cm3; head and rear frame without a grip ~%.1f kg, its CG at z %.0f" % (lev.Volume / 1000, m_head, cg),
    "  bought: %d x M4 x 50 (blocks), 3 x M4 x 16 + nuts (housing), 2 x M4 x 25 + nuts (box),"
    " M4 x 45 (levers), 4 x M3 x 8 grub + nuts, M8 stud %.0f, wire Ø%.1f ~%.0f mm" % (len(post_xy), lay_len, ROD_D, rod_off.BoundBox.YLength + 20),
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


for n, s, st in (("Head_plate", hp, "frame"), ("Trigger_arm", arm, "printed"), ("Bevel_box", drive["box"], "frame")):
    add("Rear_frame", n, s, st, offset=T)
for n, st in (("housing", "stator"), ("blocks", "stator"), ("guide_plates", "plate"), ("followers", "printed"),
              ("rotor", "rotor"), ("gear", "drive"), ("pinion", "drive"), ("stop_disc", "printed")):
    add("Head", "Head_" + n, head[n], st, offset=T)
add("Head", "Bevel_gears", drive["bevel_lay"].fuse(drive["bevel_crank"]), "drive", offset=T)
add("Head", "Crank", drive["crank"], "printed", offset=T)
for n, s, st in (("Pull_rod", rod_off, "steel"), ("Stop_pin", RB["stop_pin"], "steel"),
                 ("Shaft", RB["shaft"], "steel"), ("Layshaft", layshaft, "steel"), ("Crank_shaft", drive["crank_shaft"], "steel"),
                 ("Bearings", head_brgs.fuse(drive["bearings"]), "steel"), ("Slip_clutch", RB["slip"], "oring"),
                 ("Valve_cores", head["cores"], "steel"), ("Pins", head["pins"], "steel"), ("Fittings", head["fittings"], "steel")):
    add("Bought", n, s, st, offset=T)
add("Head", "Stop_lever", stop_lever, "rotor", offset=T)
add("Head", "Trip_cam", RB["trip_cam"], "drive", offset=T)
add("Bought", "Coupling_pins", RB["plunger"].fuse(RB["push_pin"]), "steel", offset=T)
add("Bought", "Stop_springs", RB["pl_springs"].fuse(RB["lever_spring"]), "steel", offset=T)
add("Pulled", "Lever_pulled", stop_lever_on.fuse(arm_on), "ghost", offset=T)
add("Pulled", "Rod_pulled", rod_on, "ghost", offset=T)
key, tag = {16: ("j_rings_4_12", "A16"), 19: ("g_hex_19", "A19")}[HEAD_N]
mods = module_parts(key)
add("Pack", tag + "_rails", Part.makeCompound(rail_parts), "alu")
for side in ("rear", "front"):
    add("Pack", tag + "_%s_plate" % side, plate(key, side)[0], "frame")
for style, names in (("stator", ("rp", "fp", "rear_yoke", "front_yoke", "muzzle")), ("ghost", ("chamber",)),
                     ("barrel", ("barrel",)), ("steel", ("hardware", "fitting"))):
    add("Pack", tag + "_" + "_".join(names), Part.makeCompound([m[n] for m in mods for n in names]), style)
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
write(arm, "trigger_arm")                                   # the stop lever and trip cam are the head's
write(drive_box_b, "bevel_box", (X, 90))                    # on its side, as the bench's
with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
    f.write("\n".join(report) + "\n")
print("written to", OUT_DIR)
