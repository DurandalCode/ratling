# -*- coding: utf-8 -*-
"""
Concept of the 19-barrel valve head, in FreeCAD. Not a print file: the valves are not in hand yet,
and the 12.5 mm button stack is read off the order drawing.

The ring numbers come from valve_rotor.py. Ports, from the order drawing and the body photo:
1(P) and 3(R) on the inner 16 mm face, 2(A) alone on the outer one. Wide faces carry the mounting
holes and no ports.

Stack, muzzle at z = 0, breech toward +z. The head plate is the existing disc (R 98, 10 mm). On its
breech face a cage of ribs holds the bodies and a retainer clamps them. The face cam bears on the
buttons themselves: its face sits 0.3 mm off a free button and the lobe presses 2.0 mm, short of
the valve's own 2.4 mm stop. No separate pushers.

Tubes are straight. A leaves the outer face radially, past the plate rim. P and R run inward to
two rings (supply is the upper ring, exhaust the lower one). Each ring has its own straight pipe
down through the plate, so the supply and the exhaust both come out under the head. The cam is a
solid disc, so those pipes cannot rise through it.

  freecadcmd -c "REPO='$PWD'; exec(open('mitrailleuse/valve_head.py').read())"
"""

import math
import os
import sys

import FreeCAD as App
import Part

try:
    REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
except NameError:
    REPO = os.environ.get("REPO") or REPO
VR = {"__name__": "valve_rotor"}
exec(open(os.path.join(REPO, "mitrailleuse", "valve_rotor.py")).read(), VR)

N = VR["GUN_N"]
R = None  # set from the ring
RADIAL, TANGENTIAL = VR["RADIAL"], VR["TANGENTIAL"]
BODY_W, BODY_T = RADIAL, TANGENTIAL
OVERALL = VR["OVERALL_H"]
BUTTON_D = VR["BUTTON_D"]
NUT_AF = 14.0
BUTTON_STACK = 12.5          # order drawing: body top to button tip, including the nut
BODY_H = OVERALL - BUTTON_STACK
PLATE_R, PLATE_T = VR["HEAD_PLATE_R"], 10.0
PLATE_BORE = 12.0
SHAFT_D = 8.0
DEPRESS = VR["PRESS"]        # button travel under the lobe
APPROACH = 0.3               # disc face stays this clear of a free button
LOBE_H = DEPRESS + APPROACH  # 2.3; the valve's own stop is 2.4
PORT_D = 8.0                 # Rc1/8, shown as a plain hole; the thread is not modelled
PORT_PITCH = 9.5             # order drawing, P to R along the button axis
SPOKE_OD = 6.0               # straight tubes, P and R; thinner than the port so they clear
A_OD = 8.0                   # straight tube on A
A_STICKOUT = 22.0            # past the outer face; the plate rim is inside this
MAN_R_P, MAN_R_R = 36.0, 48.0
MAN_TUBE_R = 3.0             # ring tube radius; the two rings stay 9.5 mm apart in z
FEED_OD = 4.0
FEED_DOWN = 22.0             # both pipes stick out of the muzzle face of the plate
POCKET_CLEAR = 0.4           # valve drops into the cage
RIB_T = 2.2                  # thinner than the 3 mm inner-corner gap
RETAINER_T = 3.0
RETAINER_HOLE = 18.0         # clears the nut's corners (14 mm across flats is 16.2 across corners)
CAM_T = 8.0
FITS = []


def check(ok, text):
    FITS.append(ok)
    print("[%s] %s" % ("OK " if ok else "FAIL", text))
    return ok


def cyl(d, z0, z1, x=0.0, y=0.0):
    return Part.makeCylinder(d / 2.0, z1 - z0, App.Vector(x, y, z0), App.Vector(0, 0, 1))


def tube(d_out, d_in, z0, z1):
    return cyl(d_out, z0, z1).cut(cyl(d_in, z0 - 0.2, z1 + 0.2))


def spun(shape, deg):
    s = shape.copy()
    s.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), deg)
    return s


def polar(r, ang):
    return r * math.cos(ang), r * math.sin(ang)


def hex_prism(af, h, z, x, y):
    r = af / math.sqrt(3.0)
    pts = [App.Vector(x + r * math.cos(i * math.pi / 3.0), y + r * math.sin(i * math.pi / 3.0), z)
           for i in range(6)]
    pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts)).extrude(App.Vector(0, 0, h))


def sector(r0, r1, a0, a1, z0, z1, n=None):
    n = n or max(2, int(abs(a1 - a0) / math.radians(4.0)) + 1)
    pts = []
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / float(n)
        pts.append(App.Vector(r1 * math.cos(a), r1 * math.sin(a), z0))
    for i in range(n + 1):
        a = a1 - (a1 - a0) * i / float(n)
        pts.append(App.Vector(r0 * math.cos(a), r0 * math.sin(a), z0))
    pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts)).extrude(App.Vector(0, 0, z1 - z0))


def ramp(r0, r1, a0, a1, z_back, h0, h1, n=8):
    """Stepped solid whose valve-side face goes from h0 to h1, proud of z_back toward -z."""
    parts = []
    for i in range(n):
        a = a0 + (a1 - a0) * i / float(n)
        b = a0 + (a1 - a0) * (i + 1) / float(n)
        h = h0 + (h1 - h0) * (i + 0.5) / float(n)
        if h < 0.05:
            continue
        parts.append(sector(r0, r1, a, b, z_back - h, z_back + 0.02, n=1))
    return parts[0].fuse(parts[1:])


# ---------------------------------------------------------------- ring and cam angles
rg = VR["ring"](N, TANGENTIAL, RADIAL, VR["WALL"])
R = rg["R"]
lobe = VR["lobe_hold"](rg["pitch"])
lobe = dict(lobe, h=LOBE_H)
step = 2.0 * math.pi / N

z_body0 = PLATE_T
z_body1 = z_body0 + BODY_H
z_tip = z_body0 + OVERALL          # free button tip
z_ret0 = z_body1
z_ret1 = z_body1 + RETAINER_T
z_mid = z_body0 + BODY_H / 2.0
z_port_r = z_mid - PORT_PITCH / 2.0          # R, toward the muzzle, as on the sketch
z_port_p = z_mid + PORT_PITCH / 2.0          # P, toward the button
# disc face clears a free button by APPROACH; the lobe reaches the pressed tip
z_cam_base = z_tip + APPROACH
z_cam_back = z_cam_base + CAM_T


def valve_angle(j):
    return math.pi / 2.0 - j * step


def cam_rise(ang):
    """Lobe height proud of the base, at this angle. x = 0 is the release edge, on +Y."""
    x = (math.pi / 2.0 - ang) * R
    # fold into one turn so the ramps on either side of the plateau both count
    circ = N * rg["pitch"]
    x = (x + circ / 2.0) % circ - circ / 2.0
    return VR["height"](x, lobe)


def depressed(j):
    return cam_rise(valve_angle(j)) >= LOBE_H - 1e-6


# ---------------------------------------------------------------- parts
def valve_shape(j):
    ang = valve_angle(j)
    down = DEPRESS if depressed(j) else 0.0
    y0 = R - RADIAL / 2.0
    body = Part.makeBox(BODY_T, RADIAL, BODY_H, App.Vector(-BODY_T / 2.0, y0, z_body0))
    z_mid = z_body0 + BODY_H / 2.0
    holes = []
    # A, outer face, one hole. The cylinder starts outside and drills in.
    holes.append(Part.makeCylinder(PORT_D / 2.0, 14.0, App.Vector(0, y0 + RADIAL + 1.0, z_mid),
                                   App.Vector(0, -1, 0)))
    for dz in (-PORT_PITCH / 2.0, PORT_PITCH / 2.0):
        holes.append(Part.makeCylinder(PORT_D / 2.0, 14.0, App.Vector(0, y0 - 1.0, z_mid + dz),
                                       App.Vector(0, 1, 0)))
    body = body.cut(holes)
    # Tall nut, short cap. A 6 mm pin above a thin nut read as a pusher; the cap is the
    # valve's own button, Ø10.6, and it sinks into the nut's bore when the cam presses.
    nut_h = 6.4
    nut_z = z_ret1 + 0.2
    nut = hex_prism(NUT_AF, nut_h, nut_z, 0, R).cut(cyl(11.0, nut_z - 0.2, nut_z + nut_h + 0.4, 0, R))
    button = cyl(BUTTON_D, nut_z + nut_h + 0.15 - down, z_tip - down, 0, R)
    shape = body.fuse(nut).fuse(button)
    return spun(shape, math.degrees(ang - math.pi / 2.0))


def radial_tube(r0, r1, z, od):
    """Straight tube along +Y from r0 to r1. r1 may be inside r0."""
    lo, hi = (r0, r1) if r1 > r0 else (r1, r0)
    return Part.makeCylinder(od / 2.0, hi - lo, App.Vector(0, lo, z), App.Vector(0, 1, 0))


def spun_at(shape, j):
    return spun(shape, math.degrees(valve_angle(j) - math.pi / 2.0))


def outlet_shape(j):
    """Straight tube on A, radially out, past the plate rim. No turn toward the muzzle."""
    face = R + RADIAL / 2.0
    tube = radial_tube(face, face + A_STICKOUT, z_mid, A_OD)
    return spun_at(tube, j)


def spoke_shape(j, z, ring_r):
    """Straight tube from inside the ring tube to 3 mm into the Ø8 hole."""
    face = R - RADIAL / 2.0
    tube = radial_tube(ring_r + 1.0, face + 3.0, z, SPOKE_OD)
    return spun_at(tube, j)


def ring_shape(major, z):
    ring = Part.makeTorus(major, MAN_TUBE_R)
    ring.translate(App.Vector(0, 0, z))
    return ring


def feed_angle(k):
    """Between two valves, so the riser misses the spokes. Opposite sides for P and R."""
    return valve_angle(0) - step / 2.0 + k * math.pi


def feed_shape(k, major, z0, z1):
    x, y = polar(major, feed_angle(k))
    return cyl(FEED_OD, z0, z1, x, y)


def cage():
    ribs = []
    for j in range(N):
        mid = valve_angle(j) + step / 2.0
        rib = Part.makeBox(RIB_T, RADIAL + 6.0, BODY_H,
                           App.Vector(-RIB_T / 2.0, R - RADIAL / 2.0 - 3.0, z_body0))
        ribs.append(spun(rib, math.degrees(mid - math.pi / 2.0)))
    return ribs[0].fuse(ribs[1:]) if len(ribs) > 1 else ribs[0]


def retainer():
    # lands on the body's inner and outer ends; the hole clears the nut
    s = tube(2 * (rg["r_out"] - 1.0), 2 * (rg["r_in"] + 1.0), z_ret0, z_ret1)
    for j in range(N):
        x, y = polar(R, valve_angle(j))
        s = s.cut(cyl(RETAINER_HOLE, z_ret0 - 0.5, z_ret1 + 0.5, x, y))
    return s


def cam():
    # disc is the rotor; the lobe is only as wide as the button it presses
    r0, r1 = R - 8.0, R + 10.0
    b0, b1 = R - 6.0, R + 6.0
    disc = tube(2 * r1, SHAFT_D + 0.4, z_cam_base, z_cam_back)
    # angles: x = (pi/2 - ang) * R, plateau x in [0, lp]
    a_rel = math.pi / 2.0                       # release edge, x = 0
    a_hold = math.pi / 2.0 - lobe["lp"] / R     # far end of the plateau
    a_climb = a_hold - lobe["lr"] / R
    a_fire = a_rel + lobe["lr"] / R
    pad = sector(b0, b1, a_hold, a_rel, z_cam_base - LOBE_H, z_cam_base + 0.05)
    climb = ramp(b0, b1, a_climb, a_hold, z_cam_base, 0.0, LOBE_H, n=16)
    fire = ramp(b0, b1, a_rel, a_fire, z_cam_base, LOBE_H, 0.0, n=16)
    return disc, pad.fuse(climb).fuse(fire), (b0, b1, a_hold, a_fire)


def shift(obj, vec):
    s = obj.Shape.copy()
    s.translate(App.Vector(*vec))
    obj.Shape = s


def ghost():
    """See through the disc, the clamp and the plate. Valves, tubes, rings and the lobe stay solid."""
    fade = {"Cam": 82, "Retainer": 68, "Head_plate": 72, "Cage": 40}
    for o in doc.Objects:
        vo = getattr(o, "ViewObject", None)
        if vo is None or not hasattr(vo, "Transparency"):
            continue
        if o.Name in fade:
            vo.Transparency = fade[o.Name]


def explode():
    """Pull the stack apart along the bore axis.

    Outlets step out, inlet spokes step in, the two rings and their pipes lift off the plate.
    The shaft stays on the axis and is lengthened so it still reaches the cam. The disc is
    transparent here: the blue lobe is on its underside.
    """
    # rings sit clear of the plate; spokes stay on the valves and are not pulled inward
    valve_z, ring_z, retainer_z, cam_z = 108.0, 56.0, 150.0, 188.0
    for o in list(doc.Objects):
        name = o.Name
        if name in ("Cage",) or name.startswith("Valve_"):
            shift(o, (0, 0, valve_z))
        elif name.startswith("Outlet_"):
            bb = o.Shape.BoundBox
            cx = (bb.XMin + bb.XMax) / 2.0
            cy = (bb.YMin + bb.YMax) / 2.0
            r = math.hypot(cx, cy) or 1.0
            shift(o, (18.0 * cx / r, 18.0 * cy / r, valve_z))
        elif name.startswith("Spoke_"):
            shift(o, (0, 0, valve_z))
        elif name.startswith("Ring_") or name.startswith("Feed_"):
            shift(o, (0, 0, ring_z))
        elif name == "Retainer":
            shift(o, (0, 0, retainer_z))
        elif name in ("Cam", "Cam_lobe"):
            shift(o, (0, 0, cam_z))
        elif name == "Shaft":
            o.Shape = cyl(SHAFT_D, -4.0, z_cam_back + 18.0 + cam_z)
    cam_obj = doc.getObject("Cam")
    if cam_obj is not None and getattr(cam_obj, "ViewObject", None) is not None:
        cam_obj.ViewObject.Transparency = 72


def head_plate(feeds):
    s = tube(2 * PLATE_R, PLATE_BORE, 0.0, PLATE_T)
    for feed in feeds:
        bb = feed.BoundBox
        cx = (bb.XMin + bb.XMax) / 2.0
        cy = (bb.YMin + bb.YMax) / 2.0
        s = s.cut(cyl(FEED_OD + 3.0, -1.0, PLATE_T + 1.0, cx, cy))
    return s


ribs = cage()
hold = retainer()
disc, pad, cam_win = cam()
shaft = cyl(SHAFT_D, -4.0, z_cam_back + 18.0)
valves = [valve_shape(j) for j in range(N)]
outlets = [outlet_shape(j) for j in range(N)]
spokes_p = [spoke_shape(j, z_port_p, MAN_R_P) for j in range(N)]
spokes_r = [spoke_shape(j, z_port_r, MAN_R_R) for j in range(N)]
ring_p = ring_shape(MAN_R_P, z_port_p)
ring_r = ring_shape(MAN_R_R, z_port_r)
feed_p = feed_shape(0, MAN_R_P, -FEED_DOWN, z_port_p)
feed_r = feed_shape(1, MAN_R_R, -FEED_DOWN, z_port_r)
plate = head_plate((feed_p, feed_r))


# ---------------------------------------------------------------- checks
check(abs(BODY_H + BUTTON_STACK - OVERALL) < 1e-9, "body %.1f + button stack %.1f = overall %.1f"
      % (BODY_H, BUTTON_STACK, OVERALL))
check(rg["r_out"] < PLATE_R - 5.0, "bodies stay inside the plate: outer R %.1f, plate R %.0f"
      % (rg["r_out"], PLATE_R))
check(rg["gap"] >= VR["WALL"] - 0.05, "inner-corner gap %.2f mm" % rg["gap"])
check(sum(1 for j in range(N) if depressed(j)) == 2, "the parked hold cam keeps two buttons down")

gap01 = valves[0].distToShape(valves[1])[0]
check(gap01 > 0.3, "neighbouring valves clear by %.2f mm" % gap01)
rib_gap = min(valves[j].distToShape(ribs)[0] for j in (0, 1, 5))
check(rib_gap > 0.1, "cage rib clears the bodies by %.2f mm" % rib_gap)
check(valves[0].common(plate).Volume < 1.0, "valves sit on the plate, common volume %.1f mm3"
      % valves[0].common(plate).Volume)
check(outlets[0].distToShape(plate)[0] > 2.0, "the straight A tube clears the plate by %.1f mm"
      % outlets[0].distToShape(plate)[0])
check(outlets[0].distToShape(outlets[1])[0] > 2.0, "neighbouring A tubes clear by %.1f mm"
      % outlets[0].distToShape(outlets[1])[0])
check(outlets[0].BoundBox.YMax > PLATE_R + 8.0, "A tube ends at R %.0f, past the plate"
      % outlets[0].BoundBox.YMax)
check(spokes_p[0].distToShape(spokes_p[1])[0] > 1.0, "neighbouring P tubes clear by %.1f mm"
      % spokes_p[0].distToShape(spokes_p[1])[0])
check(spokes_p[0].distToShape(spokes_r[0])[0] > 1.0, "P and R tubes on one valve clear by %.1f mm"
      % spokes_p[0].distToShape(spokes_r[0])[0])
check(ring_p.distToShape(ring_r)[0] > 1.0, "supply and exhaust rings clear by %.1f mm"
      % ring_p.distToShape(ring_r)[0])
check(ring_r.distToShape(ribs)[0] > 0.5, "exhaust ring clears the cage by %.1f mm"
      % ring_r.distToShape(ribs)[0])
check(spokes_p[0].common(ring_p).Volume > 1.0, "P tube joins the supply ring")
check(spokes_r[0].common(ring_r).Volume > 1.0, "R tube joins the exhaust ring")
check(feed_p.common(ring_p).Volume > 1.0 and feed_r.common(ring_r).Volume > 1.0,
      "each ring has its own pipe")
check(feed_p.distToShape(ring_r)[0] > 1.0, "the supply pipe clears the exhaust ring by %.1f mm"
      % feed_p.distToShape(ring_r)[0])
spoke_feed = min(feed_p.distToShape(spokes_p[j])[0] for j in (0, 1))
check(spoke_feed > 0.4, "supply pipe clears the nearest P tubes by %.1f mm" % spoke_feed)
check(min(feed_p.distToShape(plate)[0], feed_r.distToShape(plate)[0]) > 0.4,
      "both pipes clear the holes in the plate")

free_j = next(j for j in range(N) if not depressed(j))
press_j = next(j for j in range(N) if depressed(j))
free_disc = valves[free_j].distToShape(disc)[0]
check(abs(free_disc - APPROACH) < 0.05, "free button clears the disc face by %.2f mm" % free_disc)
press_d = valves[press_j].distToShape(pad)[0]
press_hit = valves[press_j].common(pad).Volume
check(press_d < 0.05 and press_hit < 20.0,
      "pressed button meets the lobe, common volume %.1f mm3" % press_hit)
free_lobe = min(valves[j].distToShape(pad)[0] for j in range(N) if not depressed(j))
check(free_lobe > 0.05, "free buttons stay off the lobe, closest %.2f mm" % free_lobe)
nut_top = z_ret1 + 0.2 + 6.4
check(z_cam_base - LOBE_H > nut_top + 0.4, "lobe stays %.1f mm above the nut"
      % (z_cam_base - LOBE_H - nut_top))
check(VR["STROKE"] - DEPRESS > 0.3, "press %.1f mm leaves %.1f mm to the valve stop"
      % (DEPRESS, VR["STROKE"] - DEPRESS))
check(shaft.distToShape(disc)[0] > 0.1, "shaft clears the cam bore")
check(hold.distToShape(valves[free_j])[0] < 0.2, "retainer lands on the body")
check(hold.common(valves[free_j]).Volume < 1.0, "retainer does not cut the valve")
check(all(v.Volume > 10000 for v in valves), "each valve is one solid, %.0f mm3" % valves[0].Volume)


# ---------------------------------------------------------------- document
doc = App.newDocument("valve_head")


def add(name, shape, color, group):
    o = doc.addObject("Part::Feature", name)
    o.Shape = shape
    if App.GuiUp:
        o.ViewObject.ShapeColor = color
    group.addObject(o)
    return o


printed = doc.addObject("App::DocumentObjectGroup", "Printed")
bought = doc.addObject("App::DocumentObjectGroup", "Bought")
steel = doc.addObject("App::DocumentObjectGroup", "Steel")
add("Head_plate", plate, (0.62, 0.60, 0.55), printed)
add("Cage", ribs, (0.78, 0.74, 0.66), printed)
add("Retainer", hold, (0.55, 0.62, 0.70), printed)
add("Cam", disc, (0.55, 0.62, 0.72), printed)
add("Cam_lobe", pad, (0.16, 0.45, 0.78), printed)
add("Ring_P", ring_p, (0.78, 0.62, 0.28), bought)
add("Ring_R", ring_r, (0.45, 0.38, 0.30), bought)
add("Feed_P", feed_p, (0.78, 0.62, 0.28), bought)
add("Feed_R", feed_r, (0.45, 0.38, 0.30), bought)
for j, v in enumerate(valves):
    color = (0.45, 0.62, 0.82) if depressed(j) else (0.72, 0.74, 0.76)
    add("Valve_%02d" % j, v, color, bought)
for j, tube_a in enumerate(outlets):
    add("Outlet_%02d" % j, tube_a, (0.72, 0.55, 0.28), bought)
for j, sp in enumerate(spokes_p):
    add("SpokeP_%02d" % j, sp, (0.78, 0.62, 0.28), bought)
for j, sp in enumerate(spokes_r):
    add("SpokeR_%02d" % j, sp, (0.45, 0.38, 0.30), bought)
add("Shaft", shaft, (0.35, 0.38, 0.42), steel)

sys.stdout.flush()
try:
    doc.recompute()
    out_dir = os.path.join(REPO, "exports", "valve_head")
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    doc.saveAs(os.path.join(out_dir, "valve_head.FCStd"))
    if App.GuiUp:
        show = os.environ.get("SHOW", "")
        if show == "ghost":
            ghost()
        elif show == "explode":
            explode()
        if show:
            doc.recompute()
except Exception:
    import traceback
    traceback.print_exc()
    sys.stdout.flush()
    raise

print("valve head, %d barrels, buttons on R %.1f" % (N, R))
print("  plate R %.0f x %.0f, cage ribs %.1f mm, retainer clamps the body top" % (PLATE_R, PLATE_T, RIB_T))
print("  disc on the buttons, lobe %.1f mm = %.1f clearance + %.1f press, %.1f left to the stop"
      % (LOBE_H, APPROACH, DEPRESS, VR["STROKE"] - DEPRESS))
print("  straight A tubes out, P and R tubes in to rings at R %.0f and %.0f" % (MAN_R_P, MAN_R_R))
print("concept only: valves are not measured, do not slice")
ok = all(FITS)
print("checks: %s" % ("OK" if ok else "FAIL"))
if __name__ == "__main__" and not os.environ.get("OUT"):
    sys.exit(0 if ok else 1)
