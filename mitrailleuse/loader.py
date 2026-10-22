# -*- coding: utf-8 -*-
"""
Mitrailleuse concept A: a loader that rams a whole wafer of balls down every barrel at once, and comes off (FreeCAD 1.0).

The v4.4 module is closed behind the ball by its valve, so it loads from the muzzle, through the muzzle sleeve
(215 mm, bore Ø30, kept on the gun for the look): each ball goes 215 mm down the sleeve and 272 mm down the
barrel, onto the seat ring's spigot, where the module's own model puts it. That is 487 mm of rigid ram in every
barrel, so the loader is a comb of rams on four legs; the rams telescope, which only shortens it for carrying.

    feet ........ printed, four, common: a spigot into the bore of a frame rail's front end (rail 12 x 1, its
                  bore Ø10, flush with the front plate's face, pack_frame.py), a collar on the rail's end, a
                  socket for the leg. Nothing is added to the gun.
    legs ........ aluminium tube 12 x 1, four, common, on the rails' axes (R 104 at 45 deg), from the feet
                  past the muzzle sleeves to a printed cap on each front end that keeps the comb on. Each in
                  LEG_PARTS sections on printed ferrules: glued in the lower section, a finger's nub clicks
                  into a hole in the upper one, flush, so the lugs slide over; press it in to part.
    wafer ....... printed, per pack: a plate with a pocket per barrel; a counterbore on its back sits on the
                  sleeve's tip, so the pocket is on the bore's axis. Three ribs in each pocket hold the ball
                  (it is soft and goes in tight), the ram pushes it through. Four lugs slide on the legs.
                  Fill wafers ahead and carry them like clips.
    comb ........ printed plate, per pack, with a boss per barrel for a ram, long lugs that slide on the legs,
                  and two side tabs for the handle posts. Its back face lands on the wafer's face at the end of
                  the stroke: that stop sets how deep the balls go (STOP_GAP short of the spigot).
    rams ........ telescopes, one per barrel: an outer aluminium tube RAM_OUT glued into the comb's boss, a
                  printed nose glued in its lower end; an inner tube RAM_IN slides through the nose, a printed
                  stop collar on its top (it cannot pass the nose: the inner does not fall out) and a printed
                  latch just under the nose when drawn out: two fingers whose nubs spring out below the nose
                  and bear on its face, so the push cannot shut the ram. Shake the comb cups down and every
                  ram runs out and clicks; pinch the nubs in to shut one. A printed cup on the inner's end
                  (Ø CUP_D: CUP_CLEAR inside the bore; a concave face that keeps the ball centred in the
                  loose sleeve, a chamfered nose that finds the sleeve's flare into the barrel).
    posts ....... printed, two, common: handles standing forward from the comb's side tabs, an M5 each.

Loading: release the trigger and open the dump valve with its key (the two chambers charged ahead empty
through their bleeds, docs/rotor.md), so the barrels hold no air under pressure and the air the balls push
ahead of them (up to ~1 bar, docs: the loader concept) can bleed out. Gun muzzle up. Wafer onto the legs from
their back ends, feet into the rails, push the comb down by its posts to the stop in 5-10 s, hold a moment,
pull it back, lift the loader off with the empty wafer, close the dump valve.

The push per ball is not known: the ball's friction in the bore was not measured. RAM_LOAD is the design figure
(the trapped air's 47 N plus as much again for friction): the rams are checked against it, and the total says
whether hands are enough or the comb needs a ratchet drive (a caulking gun's) later.

Run inside FreeCAD (or freecadcmd):
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/mitrailleuse/loader.py').read())
Prints a report with [OK ] / [FAIL] checks and writes exports/loader/ (STEP, STL in print orientation, FCStd).
AT_STOP = True before exec (or LOADER_AT_STOP=1 in the environment, for tools/render_view.py) shows the comb at the
end of the stroke, the balls on the spigots, everything cut in half through the axis (y > 0 taken away).
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
    AT_STOP
except NameError:
    AT_STOP = os.environ.get("LOADER_AT_STOP") == "1"
# the frame's parameters and functions, without its build, checks and export (it builds the v4.4 module as M)
PACK_FRAME_LIBRARY = True
exec(open(os.path.join(REPO, "mitrailleuse", "pack_frame.py"), encoding="utf-8").read()
     .split("\n# ---------------------------------------------------------------- build")[0])

NAME = "loader"
OUT_DIR = os.path.join(REPO, "exports", NAME)
Y = V(0, 1, 0)

# ---------------------------------------------------------------- parameters
BALL_D = M["BARREL_ID"]     # Ø23.8, fitted to the bore
SLEEVE_OD, SLEEVE_BORE = M["SLEEVE_OD"], M["SLEEVE_BORE"]
Z_TIP = M["z_sl1"]          # muzzle sleeve's tip
Z_MUZZLE = M["z_end"]       # barrel's end
Z_BALL = M["ball"].BoundBox.ZMax                   # ball's front on the seat ring's spigot (the module's model)
SLEEVE_LIP = 2 * (M["BARREL_ID"] / 2 + 0.2)        # the sleeve's lip at the barrel's end, its flare above it

LEG = (12.0, 1.0)           # aluminium tube, as the rails
LEG_PARTS = 3               # folds: sections joined by printed snap ferrules
# telescopic ram: nose in the outer tube, stop collar and latch on the inner (z from the nose's lower face)
TELE = dict(bore=10.8, flange=(18.0, 6.0), spigot=(11.9, 15.0), stop=(11.8, 12.0), latch_od=10.6,
            latch_body=(8.0, 20.0), finger_in=9.2, nub=(11.8, 3.0), nub_play=0.3, slot=3.0)
# leg joint: a printed ferrule glued in the lower section; in the upper one a finger's nub clicks into a hole
# drilled in its wall, flush (the comb's and wafer's lugs slide over); press the nub in to part
LEG_FERRULE = dict(d=LEG[0] - 2 * 1.0 - 0.3, len=60.0, nub=3.6, hole=4.0, nub_at=20.0, finger=(5.0, 20.0, 1.2))
LEG_HOLE = 12.4             # in the wafer's and the comb's lugs
LUG_R = 12.5
RAIL_BORE = RAIL[0] - 2 * RAIL[1]
FOOT_SPIGOT = (RAIL_BORE - 0.4, 25.0)               # into the rail's bore: Ø, length
FOOT_D, FOOT_COLLAR, FOOT_SOCKET = 20.0, 4.0, 20.0
CAP = (18.0, 15.0)          # leg's front cap: Ø, length

W_T = 30.0                  # wafer thickness
W_CB = 6.0                  # counterbore over the sleeve's tip
CB_CLEAR = 0.3              # per side round the sleeve
POCKET = 24.2               # ball pocket
RIBS = (3, 2.5, 23.0, 12.0)                        # per pocket: count, width, Ø over their crests, length
ENTRY = 1.5                 # 45 deg chamfer at the pocket's mouth
RIM = 3.0

RAM_OUT, RAM_IN = (14.0, 1.0), (8.0, 1.0)          # aluminium tubes: outer in the comb, inner with the cup
OUT_HOLE, RAM_HOLE = 14.15, 8.15
CUP_D, CUP_L, CUP_SOCKET, CUP_DEPTH, CUP_NOSE = 22.5, 22.0, 12.0, 1.5, 1.5   # wide: a soft ball slips round a thin rod
CUP_CLEAR = (BALL_D - CUP_D) / 2
C_T, BOSS = 12.0, 18.0      # comb plate, ram bosses ahead of it
BOSS_D = 20.0
C_LUG_LEN = 34.0            # comb's lugs along the legs, against racking
POST_X, POST_D, POST_LEN = 105.0, 26.0, 100.0
TAB_W = 40.0
M5 = (5.5, 8.0, 4.0)        # hole, nut AF, nut thickness
STOP_GAP = 1.0              # the cup stops this short of the ball's place on the spigot
START_GAP = 5.0             # cups ahead of the wafer's face at the start

RAM_LOAD = 100.0            # N per ball, design: trapped air 47 N + friction (assumed as much)
HAND_PUSH = 500.0           # N, two hands and some body weight, muzzle up
E_ALU = 69000.0
LEG_CLEAR = 1.0             # legs to any module part
DENSITY.update({"ram": 2.70})

# ---------------------------------------------------------------- geometry
wz0 = Z_TIP - W_CB                       # wafer's back face
wz1 = wz0 + W_T                          # its face, where the comb stops
z_cup = Z_BALL + STOP_GAP                # cup's tip at the end of the stroke
STROKE = (wz1 + START_GAP) - z_cup
cz0_end, cz0_start = wz1, wz1 + STROKE   # comb's back face
z_leg0 = z_fs + FOOT_COLLAR
CAP_SOCKET = 10.0
z_leg1 = cz0_start + C_LUG_LEN + 0.5 + CAP_SOCKET          # the cap's back 0.5 mm ahead of the comb's lugs at the start
legs_xy = [polar(RAIL_R, a) for a in RAIL_ANGLES]


def face(solid, z):
    return bottom(solid, z)


def outline(key, r_core, z0, z1, extra=()):
    """A disc over the pack with four lugs round the legs, as a face at z0 (and the disc's radius)."""
    pts = LAYOUT[key]
    r = max(math.hypot(x, y) for x, y in pts) + r_core + RIM
    s = G.fuse_all([cyl(2 * r, z0, z1)] + [M["hull_prism"]([(*p, LUG_R), (*polar(r - 12, a), LUG_R + 4)], z0, z1)
                                           for p, a in zip(legs_xy, RAIL_ANGLES)] + list(extra)).removeSplitter()
    return face(s, z0), r


def wafer(key):
    pts = LAYOUT[key]
    f, r = outline(key, SLEEVE_OD / 2 + CB_CLEAR, wz0, wz1)
    holes = [disc(LEG_HOLE / 2, *p, z=wz0) for p in legs_xy] + [disc(POCKET / 2, x, y, wz0) for x, y in pts]
    s = f.cut(holes).extrude(V(0, 0, W_T))
    cut, rib = [], []
    rz0 = (Z_TIP + wz1) / 2 - RIBS[3] / 2
    for x, y in pts:
        cut.append(cyl(SLEEVE_OD + 2 * CB_CLEAR, wz0 - 1, Z_TIP, x, y))
        cut.append(G.cone(POCKET, wz1 - ENTRY, POCKET + 2 * ENTRY + 0.02, wz1 + 0.01, x, y))
        for k in range(RIBS[0]):
            b = Part.makeBox(POCKET / 2 - RIBS[2] / 2 + 0.5, RIBS[1], RIBS[3], V(RIBS[2] / 2, -RIBS[1] / 2, rz0))
            b.rotate(V(0, 0, 0), Z, 90.0 + 360.0 / RIBS[0] * k)
            b.translate(V(x, y, 0))
            rib.append(b)
    return s.cut(G.fuse_all(cut)).fuse(G.fuse_all(rib)).removeSplitter(), r


def comb(key, z0):
    pts = LAYOUT[key]
    tabs = [Part.makeBox(POST_X + POST_D / 2 + 3 - 60, TAB_W, C_T, V(sx * 60 if sx > 0 else -(POST_X + POST_D / 2 + 3),
                                                                      -TAB_W / 2, z0)) for sx in (1, -1)]
    f, r = outline(key, BOSS_D / 2, z0, z0 + C_T, tabs)
    holes = [disc(LEG_HOLE / 2, *p, z=z0) for p in legs_xy] + [disc(OUT_HOLE / 2, x, y, z0) for x, y in pts]
    holes += [disc(M5[0] / 2, sx * POST_X, 0, z0) for sx in (1, -1)]
    s = f.cut(holes).extrude(V(0, 0, C_T))
    add = [cyl(BOSS_D, z0 + C_T - 0.01, z0 + C_T + BOSS, x, y) for x, y in pts]
    add += [cyl(2 * LUG_R, z0 + C_T - 0.01, z0 + C_LUG_LEN, *p) for p in legs_xy]
    s = s.fuse(G.fuse_all(add))
    s = s.cut(G.fuse_all([cyl(OUT_HOLE, z0 - 1, z0 + C_T + BOSS + 1, x, y) for x, y in pts]
                         + [cyl(LEG_HOLE, z0 - 1, z0 + C_LUG_LEN + 1, *p) for p in legs_xy]))
    return s, r


def tube(od, wall, z0, z1, x=0.0, y=0.0):
    return cyl(od, z0, z1, x, y).cut(cyl(od - 2 * wall, z0 - 1, z1 + 1, x, y))


def nose_z(z0):
    """The nose's lower face with the comb's back face at z0: placed so that, shut, the cup on the nose and
    the stop collar at the comb's lug tops, the ram is no longer than the comb's lugs above the cup."""
    zt = z0 - cz0_end + z_cup
    t = TELE
    s_top = t["flange"][1] + t["spigot"][1] + t["stop"][1]          # stop collar's top above the nose's face
    return (z0 + C_LUG_LEN - s_top + CUP_L + zt) / 2


def nose():
    """Lower face at z = 0: a flange under the outer tube, a spigot glued into it, the inner's bore through."""
    t = TELE
    f, sp = t["flange"], t["spigot"]
    return M["revolve"]([(t["bore"] / 2, 0), (f[0] / 2, 0), (f[0] / 2, f[1]), (sp[0] / 2, f[1]),
                         (sp[0] / 2, f[1] + sp[1]), (t["bore"] / 2, f[1] + sp[1])])


def stop_collar():
    """On the inner's top end, on the nose's upper face (z = 0 the nose's lower face, drawn out)."""
    t = TELE
    z0 = t["flange"][1] + t["spigot"][1]
    return M["revolve"]([(RAM_HOLE / 2, z0), (t["stop"][0] / 2, z0), (t["stop"][0] / 2, z0 + t["stop"][1]),
                         (RAM_HOLE / 2, z0 + t["stop"][1])])


def latch():
    """Glued on the inner just under the nose when drawn out (z = 0 the nose's lower face): a body inside the
    nose, two fingers split by a slot, a nub on each that springs out below the nose: square on top (it bears
    on the nose's face when the ram is pushed), 45 deg underneath (it rides in through the nose's bore)."""
    t = TELE
    r_b, r_f, r_n = t["latch_od"] / 2, t["finger_in"] / 2, t["nub"][0] / 2
    zb0, zb1 = t["latch_body"]
    zn1 = -t["nub_play"]
    zn0 = zn1 - t["nub"][1]
    body = M["revolve"]([(RAM_HOLE / 2, zb0), (r_b, zb0), (r_b, zb1), (RAM_HOLE / 2, zb1)])
    fingers = M["revolve"]([(r_f, zn0), (r_b, zn0), (r_n, zn0 + (r_n - r_b)), (r_n, zn1), (r_b, zn1), (r_b, zb0 + 0.01),
                            (r_f, zb0 + 0.01)])
    s = body.fuse(fingers).cut(Part.makeBox(t["slot"], 2 * r_n + 2, zb0 - 1.0 - zn0 + 0.5,
                                            V(-t["slot"] / 2, -r_n - 1, zn0 - 0.5)))
    return s.removeSplitter()


def rams(key, z0):
    """Telescopic rams drawn out: [tubes, noses, stop collars, latches], [cups]."""
    zt = z0 - cz0_end + z_cup                         # cup's tip
    zn = nose_z(z0)
    t = TELE
    s_top = zn + t["flange"][1] + t["spigot"][1] + t["stop"][1]
    parts = []
    for x, y in LAYOUT[key]:
        at = V(x, y, zn)
        parts += [tube(RAM_OUT[0], RAM_OUT[1], zn + t["flange"][1], z0 + C_T + BOSS, x, y),
                  tube(RAM_IN[0], RAM_IN[1], zt + CUP_L - CUP_SOCKET, s_top - 2.0, x, y),
                  nose().translated(at), stop_collar().translated(at), latch().translated(at)]
    return parts, [cup().translated(V(x, y, zt)) for x, y in LAYOUT[key]]


def cup():
    """Cup at the origin, tip at z = 0."""
    body = G.fuse_all([G.cone(CUP_D - 2 * CUP_NOSE, 0, CUP_D, CUP_NOSE), cyl(CUP_D, CUP_NOSE - 0.01, CUP_L)])
    r_s = BALL_D / 2 + 0.3
    dish = Part.makeSphere(r_s, V(0, 0, r_s - CUP_DEPTH))
    return body.cut(G.fuse_all([dish, cyl(RAM_HOLE, CUP_L - CUP_SOCKET, CUP_L + 1)])).removeSplitter()


def foot():
    """At the rail's end (z_fs), on the rail's axis at the origin."""
    s = G.fuse_all([cyl(FOOT_SPIGOT[0], z_fs - FOOT_SPIGOT[1], z_fs + 0.01),
                    cyl(FOOT_D, z_fs, z_fs + FOOT_COLLAR + FOOT_SOCKET)])
    return s.cut(cyl(LEG[0] + 0.3, z_leg0, z_fs + FOOT_COLLAR + FOOT_SOCKET + 1)).removeSplitter()


def leg_cap():
    """On the leg's front end, on the leg's axis at the origin."""
    z0 = z_leg1 - CAP_SOCKET
    return cyl(CAP[0], z0, z0 + CAP[1]).cut(cyl(LEG[0] + 0.3, z0 - 1, z_leg1)).removeSplitter()


def post(z0):
    """Handle post on the comb's tab at x = POST_X, from the tab's face forward; an M5 nut trap at its foot."""
    zb = z0 + C_T
    p = cyl(POST_D, zb, zb + POST_LEN, POST_X, 0)
    p = p.makeFillet(4.0, [e for e in p.Edges if e.BoundBox.ZMin > zb + POST_LEN - 1e-6])
    return p.cut(G.fuse_all([cyl(M5[0], zb - 1, zb + 30, POST_X, 0),
                             G.hex_prism(M5[1] + 0.3, zb + 12, zb + 12 + M5[2] + 0.4, POST_X, 0),
                             Part.makeBox(POST_D, M5[1] + 0.3, M5[2] + 0.4, V(POST_X, -(M5[1] + 0.3) / 2, zb + 12))]))


leg_joints = [z_leg0 + (z_leg1 - z_leg0) * k / LEG_PARTS for k in range(1, LEG_PARTS)]


def leg_ferrule():
    """Joint's plane at z = 0, nub along +x: the lower half glued in, the upper half's finger snaps its nub
    into the hole in the upper section's wall."""
    k = LEG_FERRULE
    r = k["d"] / 2
    fw, fl, ft = k["finger"]
    s = cyl(k["d"], -k["len"] / 2, k["len"] / 2)
    za, zb = k["nub_at"] - fl + 4.0, k["nub_at"] + 4.0           # finger from za (its root) to zb
    gap = Part.makeBox(ft, fw + 1.6, zb - za + 1, V(r - 1.6 - ft, -(fw + 1.6) / 2, za))       # under the finger
    sides = [Part.makeBox(r, 0.8, zb - za + 1, V(r - 1.6 - ft, sy * (fw / 2 + 0.4) - 0.4, za)) for sy in (1, -1)]
    s = s.cut(G.fuse_all([gap] + sides + [cyl(k["d"] + 2, zb, zb + 1.0).cut(cyl(2 * (r - 1.6 - ft), zb - 1, zb + 2))
                                          .common(Part.makeBox(r + 2, fw + 1.6, 2, V(0, -(fw + 1.6) / 2, zb - 0.5)))]))
    nub = Part.makeCylinder(k["nub"] / 2, LEG[0] / 2 - 0.1 - (r - 1.0), V(r - 1.0, 0, k["nub_at"]), V(1, 0, 0))
    return s.fuse(nub).removeSplitter()


def placed_ferrule(p, a, z):
    f = leg_ferrule()
    f.rotate(V(0, 0, 0), Z, a)
    return f.translated(V(p[0], p[1], z))


def legs():
    """Each leg in LEG_PARTS sections butted on snap ferrules, a hole for the nub in the upper section."""
    zs = [z_leg0] + leg_joints + [z_leg1]
    k = LEG_FERRULE
    out = []
    for p, a in zip(legs_xy, RAIL_ANGLES):
        for lo, hi in zip(zs, zs[1:]):
            t = tube(LEG[0], LEG[1], lo + (0.2 if lo > z_leg0 else 0), hi - (0.2 if hi < z_leg1 else 0), *p)
            if lo > z_leg0:
                h = Part.makeCylinder(k["hole"] / 2, LEG[0], V(0, 0, lo + k["nub_at"]), V(1, 0, 0))
                h.rotate(V(0, 0, 0), Z, a)
                t = t.cut(h.translated(V(p[0], p[1], 0)))
            out.append(t)
        out += [placed_ferrule(p, a, z) for z in leg_joints]
    return out


def module_front(key):
    """Each module's parts near the loader, placed, with the muzzle sleeve in place of the clamp."""
    pts = LAYOUT[key]
    names = ("barrel", "fp", "front_yoke", "chamber", "muzzle_sleeve", "hardware_ring", "ball", "sr", "rp")
    return [{n: place(M[n], x, y, a) for n in names} for (x, y), a in zip(pts, rod_angles(key, pts))]


_zn = nose_z(cz0_end)
out_len = cz0_end + C_T + BOSS - (_zn + TELE["flange"][1])
in_len = (_zn + TELE["flange"][1] + TELE["spigot"][1] + TELE["stop"][1] - 2.0) - (z_cup + CUP_L - CUP_SOCKET)

# ---------------------------------------------------------------- build
checks = []
check = lambda ok, text: checks.append((text, bool(ok)))
leg_parts = legs()
foot_part = foot()
cap_part = leg_cap()
cup_part = cup()
built = {}
for tag, key in KEYS:
    w, r_w = wafer(key)
    c_end, r_c = comb(key, cz0_end)
    c_start = c_end.translated(V(0, 0, STROKE))
    built[tag] = dict(key=key, mods=module_front(key), wafer=w, r_w=r_w, comb=c_start, comb_end=c_end, r_c=r_c,
                      rams=rams(key, cz0_start), rams_end=rams(key, cz0_end))
posts = [post(cz0_start)]
posts.append(posts[0].mirror(V(0, 0, 0), V(1, 0, 0)))

# ---------------------------------------------------------------- checks
lines = []
for tag, b in built.items():
    key, mods, n = b["key"], b["mods"], len(LAYOUT[b["key"]])
    sleeves = G.fuse_all([m["muzzle_sleeve"] for m in mods])
    for name, s in (("wafer", b["wafer"]), ("comb", b["comb"])):
        bb = s.BoundBox
        check(G.single_solid(s) and max(bb.XLength, bb.YLength) <= BED - 4,
              "%s %s one solid, %.0f x %.0f x %.0f, fits the %.0f bed" % (tag, name, bb.XLength, bb.YLength,
                                                                          bb.ZLength, BED))
    w = b["wafer"]
    check(w.common(sleeves).Volume < 1e-3 and w.common(sleeves.translated(V(0, 0, 0.05))).Volume / 0.05 > n * 30,
          "%s wafer sits on the %d sleeve tips (counterbore Ø%.1f x %.0f), clear of them otherwise"
          % (tag, n, SLEEVE_OD + 2 * CB_CLEAR, W_CB))
    ball_in = G.fuse_all([Part.makeSphere(BALL_D / 2, V(x, y, (Z_TIP + wz1) / 2)) for x, y in LAYOUT[key]])
    grip = w.common(ball_in).Volume
    check(grip > 0 and RIBS[2] < BALL_D < POCKET,
          "%s wafer: ball Ø%.1f held by %d ribs to Ø%.1f (%.1f mm squeeze), pocket Ø%.1f; %.0f mm3 of rib in each ball"
          % (tag, BALL_D, RIBS[0], RIBS[2], BALL_D - RIBS[2], POCKET, grip / n))
    # legs: past every module part, and in line with the rails
    d_leg = min(l.distToShape(m[p])[0] for l in leg_parts for m in mods
                for p in ("muzzle_sleeve", "hardware_ring", "fp", "front_yoke", "chamber")
                if math.hypot(l.BoundBox.Center.x - m["barrel"].BoundBox.Center.x,
                              l.BoundBox.Center.y - m["barrel"].BoundBox.Center.y) < 70)
    check(d_leg >= LEG_CLEAR, "%s: legs %.1f mm clear of the sleeves, rods, yokes and plugs" % (tag, d_leg))
    # end of the stroke: rams and cups down the bores, clear of barrels and sleeves
    tubes, cups = b["rams_end"]
    hit = max(G.fuse_all(cups + tubes).common(G.fuse_all([m[p] for m in mods for p in ("barrel", "muzzle_sleeve")])).Volume,
              0.0)
    check(hit < 1e-3, "%s: at the stop rams and cups clear of the barrels and sleeves (overlap %.3f mm3)" % (tag, hit))
    check(CUP_CLEAR >= 0.6 and CUP_D < SLEEVE_LIP, "%s: cup Ø%.1f in the bore Ø%.1f (%.2f a side), through the sleeve's lip Ø%.1f"
          % (tag, CUP_D, BALL_D, CUP_CLEAR, SLEEVE_LIP))
    lines.append("  %s: wafer Ø%.0f + 4 lugs, %.0f mm, %.0f cm3 (%.0f-%.0f g); comb Ø%.0f + tabs, %.0f cm3 (%.0f-%.0f g)"
                 % (tag, 2 * b["r_w"], W_T, w.Volume / 1000, w.Volume / 1000 * DENSITY["printed"],
                    w.Volume / 1000 * DENSITY["solid"], 2 * b["r_c"], b["comb"].Volume / 1000,
                    b["comb"].Volume / 1000 * DENSITY["printed"], b["comb"].Volume / 1000 * DENSITY["solid"]))
    ram_g = n * sum(math.pi / 4 * (d ** 2 - (d - 2 * w) ** 2) * l for (d, w), l in ((RAM_OUT, out_len), (RAM_IN, in_len))
                    ) / 1000 * DENSITY["ram"]
    cups_g = n * cup_part.Volume / 1000 * DENSITY["solid"]
    leg_g = 4 * math.pi / 4 * (LEG[0] ** 2 - (LEG[0] - 2 * LEG[1]) ** 2) * (z_leg1 - z_leg0) / 1000 * DENSITY["alu"]
    small = (4 * foot_part.Volume + 4 * cap_part.Volume + 2 * posts[0].Volume) / 1000 * DENSITY["solid"]
    total = ram_g + cups_g + leg_g + small + (w.Volume + b["comb"].Volume) / 1000 * DENSITY["printed"]
    lines.append("  %s: rams %.0f g, cups %.0f g, legs %.0f g, feet + caps + posts %.0f g; loader %.1f kg with the"
                 " wafer and comb at %.1f g/cm3" % (tag, ram_g, cups_g, leg_g, small, total / 1000, DENSITY["printed"]))
    push = n * RAM_LOAD
    lines.append("  %s: push %.0f N at %.0f N a ball (%s two hands, ~%.0f N)"
                 % (tag, push, RAM_LOAD, "within" if push <= HAND_PUSH else "MORE than", HAND_PUSH))
# folded: rams parted, the lower halves alongside the upper ones; legs in sections; posts off
zn = nose_z(cz0_end)
t = TELE
s_top = zn + t["flange"][1] + t["spigot"][1] + t["stop"][1]
tip_shut = zn - CUP_L                                       # cup up against the nose
s_top_shut = s_top + (tip_shut - z_cup)
fold_comb = max(cz0_end + C_LUG_LEN, s_top_shut) - tip_shut
fold_leg = (z_leg1 - z_leg0) / LEG_PARTS + FOOT_COLLAR + FOOT_SPIGOT[1]   # the first section with its foot
fold_len = max(fold_comb, fold_leg)
fold_w = max(b["comb"].BoundBox.XLength for b in built.values())
fold_h = max(b["comb"].BoundBox.YLength for b in built.values())
check(s_top_shut <= cz0_end + C_LUG_LEN + 0.5 and s_top_shut - (cz0_end + C_T + BOSS) < 20.0,
      "folds: rams shut %.0f mm (cup on the nose, the stop collar %.0f above the boss's end), legs in %d x %.0f"
      % (fold_comb, s_top_shut - (cz0_end + C_T + BOSS), LEG_PARTS, (z_leg1 - z_leg0) / LEG_PARTS))
nb, sc_, la = nose(), stop_collar(), latch()
ok_fit = (TELE["latch_od"] < TELE["bore"] < TELE["nub"][0] < RAM_OUT[0] - 2 * RAM_OUT[1]
          and TELE["bore"] < TELE["stop"][0] < RAM_OUT[0] - 2 * RAM_OUT[1] and TELE["flange"][0] <= BALL_D - 4)
check(all(G.single_solid(q) for q in (nb, sc_)) and len(la.Solids) == 1 and nb.common(la).Volume < 1e-3
      and nb.common(sc_).Volume < 1e-3 and ok_fit,
      "ram telescope: outer %g x %g, inner %g x %g; nose bore Ø%g (flange Ø%g, %.1f a side in the bore), stop"
      " collar Ø%g can't pass it, latch body Ø%g passes, nubs Ø%g bear %.1f mm on the nose's face, fingers"
      " flex %.1f (gap %.1f)"
      % (RAM_OUT + RAM_IN + (TELE["bore"], TELE["flange"][0], (BALL_D - TELE["flange"][0]) / 2, TELE["stop"][0],
         TELE["latch_od"], TELE["nub"][0], (TELE["nub"][0] - TELE["bore"]) / 2, (TELE["nub"][0] - TELE["bore"]) / 2,
         (TELE["finger_in"] - RAM_IN[0]) / 2)))
lf = leg_ferrule()
check(G.single_solid(lf) and lf.BoundBox.XMax <= LEG[0] / 2 - 0.05 and LEG_FERRULE["d"] < LEG[0] - 2 * LEG[1]
      and LEG_FERRULE["nub"] < LEG_FERRULE["hole"],
      "leg ferrule Ø%.1f x %.0f in the bore Ø%g, its nub Ø%g in a Ø%g hole %.0f mm into the upper section,"
      " %.2f under the leg's surface (the lugs slide over)"
      % (LEG_FERRULE["d"], LEG_FERRULE["len"], LEG[0] - 2 * LEG[1], LEG_FERRULE["nub"], LEG_FERRULE["hole"],
         LEG_FERRULE["nub_at"], LEG[0] / 2 - lf.BoundBox.XMax))
# rams: pinned at the comb, guided at the cup (wafer pocket, sleeve, bore)
i_in = math.pi / 64 * (RAM_IN[0] ** 4 - (RAM_IN[0] - 2 * RAM_IN[1]) ** 4)
free = zn - z_cup
p_euler = math.pi ** 2 * E_ALU * i_in / free ** 2
nub_a = 2 * (TELE["nub"][0] - TELE["bore"]) / 2 * (math.pi * TELE["nub"][0] / 2 - TELE["slot"])
check(p_euler >= 3 * RAM_LOAD and RAM_LOAD / nub_a <= 20.0,
      "inner ram %g x %g, %.0f mm out of the nose: buckles at %.0f N (>= 3 x %.0f); nubs bear %.0f mm2, %.0f MPa"
      % (RAM_IN + (free, p_euler, RAM_LOAD, nub_a, RAM_LOAD / nub_a)))
check(abs(z_cup - STOP_GAP - Z_BALL) < 1e-6 and STROKE > 0,
      "stroke %.0f mm: ball from the wafer to the spigot, %.0f mm down the sleeve and %.1f down the barrel"
      % (STROKE, Z_TIP - Z_MUZZLE, Z_MUZZLE - Z_BALL))
check(G.single_solid(foot_part) and FOOT_SPIGOT[0] < RAIL_BORE,
      "foot: spigot Ø%.1f x %.0f into the rail's bore Ø%.0f, collar on its end at z %.1f"
      % (FOOT_SPIGOT[0], FOOT_SPIGOT[1], RAIL_BORE, z_fs))
c_start = built["A19"]["comb"]
check(all(c_start.common(cap_part.translated(V(*p, 0))).Volume < 1e-3 for p in legs_xy)
      and min(cap_part.translated(V(*p, 0)).distToShape(c_start)[0] for p in legs_xy) < 1.0,
      "comb at the start rests under the legs' caps")
check(all(p.common(G.fuse_all(leg_parts)).Volume < 1e-3 and p.common(c_start).Volume < 1e-3 for p in posts),
      "posts clear of the legs, on the comb's tabs")

report = [
    "Mitrailleuse concept A: loader (wafer of balls, comb of rams on four legs into the frame's rails)",
    "  sleeve tip z %.1f, barrel's end z %.1f, ball on the spigot to z %.1f; wafer z %.1f..%.1f"
    % (Z_TIP, Z_MUZZLE, Z_BALL, wz0, wz1),
    "  comb: back face z %.1f at the start, %.1f at the stop (on the wafer's face); stroke %.0f mm"
    % (cz0_start, cz0_end, STROKE),
    "  legs: 4 x alu tube %g x %g, z %.1f..%.1f (%.0f mm each); loader from the rails' ends to the posts' tops %.0f mm,"
    " %.0f ahead of the sleeve tips" % (LEG + (z_leg0, z_leg1, z_leg1 - z_leg0, cz0_start + C_T + POST_LEN
                                                - (z_fs - FOOT_SPIGOT[1]), cz0_start + C_T + POST_LEN - Z_TIP)),
    "  rams: 16 / 19 telescopes, outer alu %g x %g x %.0f, inner %g x %g x %.0f mm, cups Ø%.1f"
    % (RAM_OUT + (out_len,) + RAM_IN + (in_len, CUP_D)),
    "  bought: legs 4 x %d x %.0f mm (a Ø%g hole %.0f mm from the lower end of the upper two), 2 x M5 x 25 + nuts;"
    " printed: 16 or 19 noses, stop collars, latches, cups; %d leg ferrules"
    % (LEG_PARTS, (z_leg1 - z_leg0) / LEG_PARTS - 0.4, LEG_FERRULE["hole"], LEG_FERRULE["nub_at"], 4 * (LEG_PARTS - 1)),
    "  folded (rams shut, legs in sections, posts off): %.0f x %.0f x %.0f mm" % (fold_len, fold_w, fold_h),
] + lines + ["  [%s] %s" % ("OK " if ok else "FAIL", t) for t, ok in checks]
print("\n".join(report))

# ---------------------------------------------------------------- document and exports
os.makedirs(OUT_DIR, exist_ok=True)
sc = FV.Scene(NAME)
FV.STYLES.setdefault("alu", ((0.80, 0.82, 0.86), 0))
FV.STYLES.setdefault("barrel", ((0.45, 0.46, 0.50), 0))
FV.STYLES.setdefault("ball", ((0.95, 0.8, 0.2), 0))
dx = {"A16": -150.0, "A19": 150.0}
half = Part.makeBox(800, 400, 1600, V(-400, -400, -300))                 # y <= 0: the section's kept half


def cut(shape):
    return shape.common(half) if AT_STOP else shape


for tag, b in built.items():
    off = V(2 * dx[tag], 0, 0)
    key, mods = b["key"], b["mods"]
    comb_s, rams_s = (b["comb_end"], b["rams_end"]) if AT_STOP else (b["comb"], b["rams"])
    sc.add(tag + "_loader", tag + "_wafer", cut(b["wafer"]), "rotor", offset=off)
    sc.add(tag + "_loader", tag + "_comb", cut(comb_s), "printed", offset=off)
    sc.add(tag + "_loader", tag + "_rams", cut(Part.makeCompound(rams_s[0])), "alu", offset=off)
    sc.add(tag + "_loader", tag + "_cups", cut(Part.makeCompound(rams_s[1])), "shoe", offset=off)
    sc.add(tag + "_loader", tag + "_legs", cut(Part.makeCompound(leg_parts)), "alu", offset=off)
    sc.add(tag + "_loader", tag + "_feet_caps_posts", cut(Part.makeCompound(
        [foot_part.translated(V(*p, 0)) for p in legs_xy] + [cap_part.translated(V(*p, 0)) for p in legs_xy]
        + [p.translated(V(0, 0, cz0_end - cz0_start)) if AT_STOP else p for p in posts])), "printed", offset=off)
    balls = ([m["ball"] for m in mods] if AT_STOP else
             [Part.makeSphere(BALL_D / 2, V(x, y, (Z_TIP + wz1) / 2)) for x, y in LAYOUT[key]])
    sc.add(tag + "_balls", tag + "_balls", cut(Part.makeCompound(balls)), "ball", offset=off)
    sc.add(tag + "_gun", tag + "_front_plate", cut(plate(key, "front")[0]), "frame", offset=off)
    sc.add(tag + "_gun", tag + "_rails", cut(Part.makeCompound([r.common(cyl(400, -40, 400)) for r in rails()])),
           "alu", offset=off)
    for style, names in (("stator", ("fp", "front_yoke", "muzzle_sleeve", "sr", "rp")), ("ghost", ("chamber",)),
                         ("barrel", ("barrel",)), ("steel", ("hardware_ring",))):
        sc.add(tag + "_gun", "%s_%s" % (tag, "_".join(names)),
               cut(Part.makeCompound([m[n].common(cyl(400, -40, 600)) for m in mods for n in names])), style,
               offset=off)
sc.finish()
sc.doc.saveAs(os.path.join(OUT_DIR, NAME + ".FCStd"))

import MeshPart


def write(shape, name, flip=False):
    s = shape.copy()
    if flip:
        s.rotate(V(0, 0, 0), X, 180)
    s.translate(V(-s.BoundBox.Center.x, -s.BoundBox.Center.y, -s.BoundBox.ZMin))
    s.exportStep(os.path.join(OUT_DIR, name + ".step"))
    MeshPart.meshFromShape(Shape=s, LinearDeflection=0.02, AngularDeflection=0.1).write(
        os.path.join(OUT_DIR, name + ".stl"))


for tag, b in built.items():
    write(b["wafer"], "%s_wafer" % tag.lower(), True)        # face on the bed, the counterbores open upward
    write(b["comb"], "%s_comb" % tag.lower())                 # back face on the bed, bosses and lugs up
write(cup_part, "cup", True)                                  # socket end on the bed, the dish up; print 16 or 19
write(foot_part, "foot")                                      # spigot on the bed; print 4
write(cap_part, "leg_cap", True)                              # closed end on the bed; print 4
write(nose(), "ram_nose")                                     # flange on the bed; print 16 or 19
write(stop_collar(), "ram_stop_collar")                       # print 16 or 19
write(latch(), "ram_latch")                                   # nubs' 45 deg side on the bed; print 16 or 19
write(leg_ferrule(), "leg_ferrule")                           # print 8
write(posts[0], "post")                                       # flat foot on the bed; print 2
with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
    f.write("\n".join(report) + "\n")
print("written to", OUT_DIR)
