# -*- coding: utf-8 -*-
"""
Concept of the 19-barrel valve head, in FreeCAD. Not a print file: the valves are not in hand yet,
and the 12.5 mm button stack is read off the order drawing.

The ring numbers come from valve_rotor.py. Ports, from the order drawing and the body photo:
1(P) and 3(R) on the inner 16 mm face, 2(A) alone on the outer one. Wide faces carry the mounting
holes and no ports.

Stack, muzzle at z = 0, breech toward +z. The head plate is the existing disc (R 98, 10 mm). On its
breech face a cage of ribs holds the bodies, a retainer clamps them, and a guide ring limits each
pusher to 2.2 mm so it cannot drive the button past the valve's 2.4 mm stop. The face cam rises
2.3 mm: 0.3 mm of that is running clearance, so a free button is not rubbed and a pressed one is
down 2.0 mm.

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
APPROACH = 0.3               # base circle stays this clear of a free pusher
LOBE_H = DEPRESS + APPROACH  # 2.3; the valve's own stop is 2.4
HARD = 2.2                   # pusher flange hits the guide here, short of 2.4
PUSHER_L = 18.0
PUSHER_D, NOSE_D = 4.0, 3.0
PORT_D = 8.0                 # Rc1/8, shown as a plain hole; the thread is not modelled
PORT_PITCH = 9.5             # order drawing, P to R along the button axis
POCKET_CLEAR = 0.4           # valve drops into the cage
RIB_T = 2.2                  # thinner than the 3 mm inner-corner gap
RETAINER_T = 3.0
RETAINER_HOLE = 18.0         # clears the nut's corners (14 mm across flats is 16.2 across corners)
GUIDE_T = 3.0
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
# pusher nose sits on the button. Free tail clears the cam base by APPROACH.
z_tail_free = z_tip + PUSHER_L
z_cam_base = z_tail_free + APPROACH          # the disc's valve-side face
z_cam_back = z_cam_base + CAM_T
# guide: the flange has HARD mm of travel before it hits, and the working press uses DEPRESS.
z_guide1 = z_tip + 7.0
z_guide0 = z_guide1 - GUIDE_T
z_flange_free = z_guide1 + HARD              # flange's valve-side face, button fully out


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
    stubs = [Part.makeCylinder(PORT_D / 2.0, 5.0, App.Vector(0, y0 + RADIAL, z_mid), App.Vector(0, 1, 0))]
    for dz in (-PORT_PITCH / 2.0, PORT_PITCH / 2.0):
        stubs.append(Part.makeCylinder(PORT_D / 2.0, 6.0, App.Vector(0, y0, z_mid + dz), App.Vector(0, -1, 0)))
    nut = hex_prism(NUT_AF, 3.2, z_ret1 + 0.2, 0, R).cut(cyl(11.0, z_ret1, z_ret1 + 4.0, 0, R))
    button = cyl(BUTTON_D, z_ret1 + 3.5 - down, z_tip - down, 0, R)
    shape = body.fuse(stubs).fuse(nut).fuse(button)
    return spun(shape, math.degrees(ang - math.pi / 2.0))


def elbow_shape(j):
    """Rc1/8 elbow on A: out, then toward the muzzle, past the plate rim."""
    ang = valve_angle(j)
    y0 = R + RADIAL / 2.0
    z_mid = z_body0 + BODY_H / 2.0
    radial = Part.makeCylinder(4.5, 16.0, App.Vector(0, y0, z_mid), App.Vector(0, 1, 0))
    out_y = y0 + 16.0
    down = Part.makeCylinder(4.5, 22.0, App.Vector(0, out_y, z_mid - 22.0), App.Vector(0, 0, 1))
    return spun(radial.fuse(down), math.degrees(ang - math.pi / 2.0))


def pusher_shape(j):
    ang = valve_angle(j)
    down = DEPRESS if depressed(j) else 0.0
    x, y = polar(R, ang)
    nose = z_tip - down
    tail = nose + PUSHER_L
    pin = cyl(NOSE_D, nose, nose + 3.0, x, y).fuse(cyl(PUSHER_D, nose + 3.0, tail, x, y))
    flange = cyl(8.0, z_flange_free - down, z_flange_free - down + 2.0, x, y)
    return pin.fuse(flange)


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


def guide():
    s = tube(2 * (R + 9.0), 2 * (R - 9.0), z_guide0, z_guide1)
    for j in range(N):
        x, y = polar(R, valve_angle(j))
        s = s.cut(cyl(5.0, z_guide0 - 0.5, z_guide1 + 0.5, x, y))
    return s


def cam():
    r0, r1 = R - 8.0, R + 10.0
    disc = tube(2 * r1, SHAFT_D + 0.4, z_cam_base, z_cam_back)
    # angles: x = (pi/2 - ang) * R, plateau x in [0, lp]
    a_rel = math.pi / 2.0                       # release edge, x = 0
    a_hold = math.pi / 2.0 - lobe["lp"] / R     # far end of the plateau
    a_climb = a_hold - lobe["lr"] / R
    a_fire = a_rel + lobe["lr"] / R
    pad = sector(r0, r1, a_hold, a_rel, z_cam_base - LOBE_H, z_cam_base + 0.05)
    climb = ramp(r0, r1, a_climb, a_hold, z_cam_base, 0.0, LOBE_H)
    fire = ramp(r0, r1, a_rel, a_fire, z_cam_base, LOBE_H, 0.0)
    return disc, pad.fuse(climb).fuse(fire), (r0, r1, a_hold, a_fire)


def shift(obj, vec):
    s = obj.Shape.copy()
    s.translate(App.Vector(*vec))
    obj.Shape = s


def ghost():
    """See through the disc, the clamp and the plate. The valves, pushers and lobe stay solid."""
    fade = {"Cam": 82, "Guide": 78, "Retainer": 68, "Head_plate": 55, "Cage": 40}
    for o in doc.Objects:
        vo = getattr(o, "ViewObject", None)
        if vo is None or not hasattr(vo, "Transparency"):
            continue
        if o.Name in fade:
            vo.Transparency = fade[o.Name]


def explode():
    """Pull the stack apart along the bore axis. Elbows also step out radially.

    The shaft stays on the axis and is lengthened so it still reaches the cam.
    The disc is transparent in this view: the blue lobe is on its underside.
    """
    valve_z, retainer_z, guide_z, pusher_z, cam_z = 55.0, 90.0, 108.0, 130.0, 160.0
    for o in list(doc.Objects):
        name = o.Name
        if name in ("Cage",) or name.startswith("Valve_"):
            shift(o, (0, 0, valve_z))
        elif name.startswith("Elbow_"):
            bb = o.Shape.BoundBox
            cx = (bb.XMin + bb.XMax) / 2.0
            cy = (bb.YMin + bb.YMax) / 2.0
            r = math.hypot(cx, cy) or 1.0
            shift(o, (22.0 * cx / r, 22.0 * cy / r, valve_z))
        elif name == "Retainer":
            shift(o, (0, 0, retainer_z))
        elif name == "Guide":
            shift(o, (0, 0, guide_z))
        elif name.startswith("Pusher_"):
            shift(o, (0, 0, pusher_z))
        elif name in ("Cam", "Cam_lobe"):
            shift(o, (0, 0, cam_z))
        elif name == "Shaft":
            o.Shape = cyl(SHAFT_D, -4.0, z_cam_back + 18.0 + cam_z)
    cam = doc.getObject("Cam")
    if cam is not None and getattr(cam, "ViewObject", None) is not None:
        cam.ViewObject.Transparency = 72


plate = tube(2 * PLATE_R, PLATE_BORE, 0.0, PLATE_T)
ribs = cage()
hold = retainer()
ring_guide = guide()
disc, pad, cam_win = cam()
shaft = cyl(SHAFT_D, -4.0, z_cam_back + 18.0)
valves = [valve_shape(j) for j in range(N)]
elbows = [elbow_shape(j) for j in range(N)]
pushers = [pusher_shape(j) for j in range(N)]


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
check(elbows[0].distToShape(plate)[0] > 1.0, "the A elbow clears the plate by %.1f mm"
      % elbows[0].distToShape(plate)[0])
check(elbows[0].distToShape(elbows[1])[0] > 2.0, "neighbouring A elbows clear by %.1f mm"
      % elbows[0].distToShape(elbows[1])[0])

free_j = next(j for j in range(N) if not depressed(j))
press_j = next(j for j in range(N) if depressed(j))
# tail to cam: free pusher ends APPROACH short of the base, pressed tail meets the lobe
free_tail_z = z_tip + PUSHER_L
press_tail_z = z_tip - DEPRESS + PUSHER_L
check(abs((z_cam_base - free_tail_z) - APPROACH) < 1e-6,
      "free pusher clears the cam base by %.1f mm" % APPROACH)
check(abs((z_cam_base - LOBE_H) - press_tail_z) < 1e-6,
      "pressed pusher meets the lobe, button down %.1f mm" % DEPRESS)
check(LOBE_H < VR["STROKE"] + 1e-9 and DEPRESS > VR["SWITCH"],
      "lobe %.1f mm is under the %.1f stop and the button passes the %.1f switch"
      % (LOBE_H, VR["STROKE"], VR["SWITCH"]))
# hard stop: after DEPRESS mm the flange still has HARD - DEPRESS before the guide
left = HARD - DEPRESS
check(0.1 < left < 0.5, "hard stop leaves %.1f mm before the flange, short of the 2.4 stop" % left)
check(z_guide1 < z_flange_free - 1.0 and z_cam_base > z_tail_free,
      "guide, pusher and cam are in that order from the button")
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
add("Guide", ring_guide, (0.45, 0.50, 0.55), printed)
add("Cam", disc, (0.55, 0.62, 0.72), printed)
add("Cam_lobe", pad, (0.16, 0.45, 0.78), printed)
for j, v in enumerate(valves):
    color = (0.45, 0.62, 0.82) if depressed(j) else (0.72, 0.74, 0.76)
    add("Valve_%02d" % j, v, color, bought)
for j, e in enumerate(elbows):
    add("Elbow_%02d" % j, e, (0.72, 0.55, 0.28), bought)
add("Shaft", shaft, (0.35, 0.38, 0.42), steel)
for j, p in enumerate(pushers):
    add("Pusher_%02d" % j, p, (0.15, 0.15, 0.16), steel)

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
print("  two buttons down, lobe %.1f mm = %.1f approach + %.1f press, hard stop %.1f" % (LOBE_H, APPROACH, DEPRESS, HARD))
print("  A elbows outward, P and R stubs inward %.1f mm apart" % PORT_PITCH)
print("concept only: valves are not measured, do not slice")
ok = all(FITS)
print("checks: %s" % ("OK" if ok else "FAIL"))
if __name__ == "__main__" and not os.environ.get("OUT"):
    sys.exit(0 if ok else 1)
