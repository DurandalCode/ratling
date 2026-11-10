# -*- coding: utf-8 -*-
"""
Bench D: one bought 3/2 valve and a hand slider, to see if the valve head can fire a module.

The 19-barrel head (valve_head.py) stays a scheme. This bench does not draw its hoses, its plate
tunnels or its header. Air stays in bought fittings: a barb in P from the regulator, a barb in A
to one v4.4 module, R left open. The printed parts only hold the body and slide a pad across the
button the way the face cam will.

The pad is the cam. At rest it clears the cap by 0.5 mm. Over a 12 mm ramp it comes down 2.5 mm,
so the dwell presses 2.0 of the drawing's 2.4 stroke and then stays there however far you push.
Pull it back and the button is free. No separate pusher.

Body 31.8 x 16 x 33.3 and the 12.5 mm button stack are the order drawing, same numbers as
valve_head.py. Nothing here is measured. The pocket is 0.4 mm loose and the strap lands on the
body, so a slightly different body still clamps. If the cap sits high, file the dwell; if low,
a layer of tape on the pad.

    freecadcmd -c "REPO='$PWD'; exec(open('mitrailleuse/valve_bench.py').read())"
"""

import math
import os
import sys

import FreeCAD as App
import Part

try:
    REPO
except NameError:
    REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VR = {"__name__": "valve_rotor"}
exec(open(os.path.join(REPO, "mitrailleuse", "valve_rotor.py")).read(), VR)

BODY_X = VR["RADIAL"]                 # 31.8, port faces on the ends
BODY_Y = VR["TANGENTIAL"]             # 16
OVERALL = VR["OVERALL_H"]             # 45.8 to the cap
PRESS = VR["PRESS"]                   # 2.0
STOP = VR["STROKE"]                   # 2.4, the valve's own stop; the pad must not reach it
BUTTON_D = VR["BUTTON_D"]
BUTTON_STACK = 12.5                   # valve_head.py: body top to cap, off the drawing
BODY_Z = OVERALL - BUTTON_STACK
NUT_AF, NUT_H = 14.0, 6.4
NUT_HOLE = 18.0                       # corners of a 14 mm hex are 16.2

REST_GAP = 0.5                        # wider than the rotor's 0.3; the bench is proving the stroke
RAMP_L, DWELL_L = 12.0, 24.0
PAD_DROP = REST_GAP + PRESS           # 2.5: rest clearance plus the press
SLIDE_CLEAR = 0.2                     # bar above its ledges
LID_GAP = 0.35

FLOOR = 6.0
Z_BODY = FLOOR
Z_TOP = Z_BODY + BODY_Z
Z_TIP = Z_BODY + OVERALL
Z_LEDGE = Z_TIP + REST_GAP - SLIDE_CLEAR
BAR_Z = Z_LEDGE + SLIDE_CLEAR         # underside, also the rest pad
BAR_TOP = BAR_Z + 12.0
LID_Z = BAR_TOP + LID_GAP
LID_T = 4.0

# rails on the wide-face sides, clear of both port ends. The ledge is the low step,
# the wall is the tall guide; both grow from the floor, so neither is a bridge.
LEDGE_IN, LEDGE_OUT = 16.0, 19.3
WALL_IN, WALL_OUT = 19.3, 27.0
# two posts, not a wall: the valve sits in the gap where the barbs and the button show
POSTS = ((-54.0, -22.0), (22.0, 48.0))
SLIDER_HY = 18.9                      # 0.4 mm to the guide wall
SLIDER_X0, SLIDER_X1 = -72.0, 62.0
PAD_HY = 7.0
# parked: the cap is on the flat, and the ramp hangs out past the rail where it can be seen
SHOWN = 16.0

STRAP_T = 4.0
SCREW_CLR, SCREW_TAP, SCREW_DEEP = 3.4, 2.7, 8.0
FITS = []


def check(ok, text):
    FITS.append(bool(ok))
    print("[%s] %s" % ("OK " if ok else "FAIL", text), flush=True)
    return ok


def box(x0, y0, z0, x1, y1, z1):
    x0, x1 = (x0, x1) if x1 > x0 else (x1, x0)
    y0, y1 = (y0, y1) if y1 > y0 else (y1, y0)
    z0, z1 = (z0, z1) if z1 > z0 else (z1, z0)
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, App.Vector(x0, y0, z0))


def prism_xz(pts, y0, y1):
    loop = [App.Vector(x, y0, z) for x, z in pts]
    loop.append(loop[0])
    return Part.Face(Part.makePolygon(loop)).extrude(App.Vector(0, y1 - y0, 0))


def hex_at(af, h, z, x, y):
    r = af / math.sqrt(3.0)
    pts = [App.Vector(x + r * math.cos(i * math.pi / 3.0), y + r * math.sin(i * math.pi / 3.0), z)
           for i in range(6)]
    pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts)).extrude(App.Vector(0, 0, h))


def cyl_z(d, z0, z1, x, y):
    return Part.makeCylinder(d / 2.0, z1 - z0, App.Vector(x, y, z0), App.Vector(0, 0, 1))


def cyl_x(d, x0, x1, y, z):
    x_lo, x_hi = (x0, x1) if x1 > x0 else (x1, x0)
    return Part.makeCylinder(d / 2.0, x_hi - x_lo, App.Vector(x_lo, y, z), App.Vector(1, 0, 0))


# ---------------------------------------------------------------- valve, bought, for the picture and the checks
hx, hy = BODY_X / 2.0, BODY_Y / 2.0
body = box(-hx, -hy, Z_BODY, hx, hy, Z_TOP)
nut = hex_at(NUT_AF, NUT_H, Z_TOP, 0, 0)
button = cyl_z(BUTTON_D, Z_TOP + NUT_H, Z_TIP, 0, 0)

# a barb's worth of air outside each port. Nothing printed may enter it.
z_mid = Z_BODY + BODY_Z / 2.0
port_zones = [
    cyl_x(10.0, hx, hx + 22.0, 0, z_mid),                                  # A
    cyl_x(10.0, -hx, -hx - 22.0, 0, z_mid + 4.75),                         # P
    cyl_x(10.0, -hx, -hx - 22.0, 0, z_mid - 4.75),                         # R
]


# ---------------------------------------------------------------- printed parts
def base_shape():
    parts = [box(-68, -40, 0, 68, 40, FLOOR)]
    for s in (1.0, -1.0):
        # strap shelf and body locator, below the ledge so nothing bridges over it
        parts.append(box(-12, s * (hy + 0.4), FLOOR - 0.2, 12, s * 15.2, Z_TOP - 0.4))
        parts.append(box(s * (hx + 0.6), -7, FLOOR - 0.2, s * (hx + 3.4), 7, Z_BODY + 5.0))
        for x0, x1 in POSTS:
            parts.append(box(x0, s * LEDGE_IN, FLOOR - 0.2, x1, s * LEDGE_OUT, Z_LEDGE))
            parts.append(box(x0, s * WALL_IN, FLOOR - 0.2, x1, s * WALL_OUT, LID_Z))
    s = parts[0].fuse(parts[1:])
    for x in (-8.0, 8.0):
        for y in (-12.0, 12.0):
            s = s.cut(cyl_z(SCREW_TAP, Z_TOP - 0.4 - SCREW_DEEP, Z_TOP - 0.2, x, y))
    for x in (-32.0, 32.0):
        for y in (-23.0, 23.0):
            s = s.cut(cyl_z(SCREW_TAP, LID_Z - SCREW_DEEP, LID_Z + 0.2, x, y))
    return s


def strap_shape():
    s = box(-16, -15.0, Z_TOP, 16, 15.0, Z_TOP + STRAP_T)
    s = s.cut(cyl_z(NUT_HOLE, Z_TOP - 0.2, Z_TOP + STRAP_T + 0.2, 0, 0))
    for x in (-8.0, 8.0):
        for y in (-12.0, 12.0):
            s = s.cut(cyl_z(SCREW_CLR, Z_TOP - 0.2, Z_TOP + STRAP_T + 0.2, x, y))
    return s


def slider_shape(shift):
    """Bar plus the pad. shift is the world x of the ramp start."""
    bar = box(SLIDER_X0 + shift, -SLIDER_HY, BAR_Z, SLIDER_X1 + shift, SLIDER_HY, BAR_TOP)
    x0 = shift
    x1 = shift + RAMP_L
    x2 = x1 + DWELL_L
    z_lo = BAR_Z - PAD_DROP
    pad = prism_xz([(x0, BAR_Z), (x1, z_lo), (x2, z_lo), (x2, BAR_Z + 0.3), (x0, BAR_Z + 0.3)],
                   -PAD_HY, PAD_HY)
    return bar.fuse(pad)


def lid_shape(x_screw):
    """One keeper. Two of them hold the slider, with the button showing between."""
    s = box(x_screw - 12.0, -29.0, LID_Z, x_screw + 12.0, 29.0, LID_Z + LID_T)
    for y in (-23.0, 23.0):
        s = s.cut(cyl_z(SCREW_CLR, LID_Z - 0.2, LID_Z + LID_T + 0.2, x_screw, y))
    return s


base = base_shape()
strap = strap_shape()
slider = slider_shape(SHOWN)
pressed = slider_shape(-(RAMP_L + DWELL_L / 2.0))
lid_a = lid_shape(-32.0)
lid_b = lid_shape(32.0)


# ---------------------------------------------------------------- checks
check(len(base.Solids) == 1 and base.Volume > 20000, "base is one solid, %.0f mm3" % base.Volume)
check(len(strap.Solids) == 1 and strap.Volume > 2000, "strap is one solid, %.0f mm3" % strap.Volume)
check(len(slider.Solids) == 1 and slider.Volume > 5000, "slider is one solid, %.0f mm3" % slider.Volume)
check(len(lid_a.Solids) == 1 and lid_a.Volume > 2000, "keeper is one solid, %.0f mm3" % lid_a.Volume)

check(base.common(body).Volume < 1.0, "body drops into the pocket, common %.1f mm3" % base.common(body).Volume)
check(abs(strap.distToShape(body)[0]) < 0.05, "strap lands on the body")
check(strap.distToShape(nut)[0] > 0.6, "strap hole clears the nut by %.1f mm" % strap.distToShape(nut)[0])
check(base.distToShape(strap)[0] > 0.2, "strap clears the cheeks by %.1f mm" % base.distToShape(strap)[0])

check(abs(slider.distToShape(button)[0] - REST_GAP) < 0.05,
      "at rest the pad clears the cap by %.2f mm" % slider.distToShape(button)[0])
press_overlap = pressed.common(button).Volume
cap_slice = math.pi * (BUTTON_D / 2.0) ** 2 * PRESS
check(abs(press_overlap - cap_slice) < 40.0,
      "dwell presses %.1f mm into the cap, overlap %.0f mm3" % (PRESS, press_overlap))
check(pressed.BoundBox.ZMin > Z_TIP - STOP - 0.01,
      "pad stops %.2f mm short of the valve stop" % (pressed.BoundBox.ZMin - (Z_TIP - STOP)))
check(pressed.distToShape(nut)[0] > 2.0, "pressed pad clears the nut by %.1f mm" % pressed.distToShape(nut)[0])

check(slider.distToShape(base)[0] > 0.1, "slider clears the guides by %.2f mm" % slider.distToShape(base)[0])
check(abs(lid_a.distToShape(slider)[0] - LID_GAP) < 0.05
      and abs(lid_b.distToShape(slider)[0] - LID_GAP) < 0.05,
      "keepers clear the slider by %.2f mm" % lid_a.distToShape(slider)[0])
check(lid_a.distToShape(base)[0] < 0.05 and lid_b.distToShape(base)[0] < 0.05,
      "keepers sit on the rails")

port_hit = max(z.common(s).Volume for z in port_zones for s in (base, strap, slider, lid_a, lid_b))
check(port_hit < 1.0, "barbs on P, R and A stay clear of the print, worst %.1f mm3" % port_hit)

rise = PAD_DROP / RAMP_L
check(rise < math.tan(math.radians(18.0)),
      "ramp is %.0f deg, the rotor's is 18" % math.degrees(math.atan(rise)))


# ---------------------------------------------------------------- document
doc = App.newDocument("valve_bench")


def add(name, shape, color, group):
    o = doc.addObject("Part::Feature", name)
    o.Shape = shape
    if App.GuiUp:
        o.ViewObject.ShapeColor = color
    group.addObject(o)
    return o


printed = doc.addObject("App::DocumentObjectGroup", "Printed")
bought = doc.addObject("App::DocumentObjectGroup", "Bought")
show = os.environ.get("SHOW", "")
lid_a_show, lid_b_show, slider_show = lid_a.copy(), lid_b.copy(), slider.copy()
if show == "open":
    # off the button, so the cap and the pad both read
    slider_show.translate(App.Vector(96, 0, 0))
    lid_a_show.translate(App.Vector(0, 0, 22))
    lid_b_show.translate(App.Vector(0, 0, 22))
add("Base", base, (0.62, 0.60, 0.55), printed)
add("Strap", strap, (0.45, 0.50, 0.58), printed)
add("Slider", slider_show, (0.72, 0.55, 0.28), printed)
add("Keeper_a", lid_a_show, (0.55, 0.58, 0.62), printed)
add("Keeper_b", lid_b_show, (0.55, 0.58, 0.62), printed)
add("Valve_body", body, (0.62, 0.66, 0.72), bought)
add("Valve_nut", nut, (0.75, 0.72, 0.62), bought)
add("Valve_button", button, (0.86, 0.72, 0.36), bought)

out_dir = os.path.join(REPO, "exports", "valve_bench")
if not os.path.isdir(out_dir):
    os.makedirs(out_dir)


def export_stl(shape, name, flip=False):
    s = shape.copy()
    if flip:
        s.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), 180)
    s.translate(App.Vector(0, 0, -s.BoundBox.ZMin))
    s.exportStep(os.path.join(out_dir, name + ".step"))
    import MeshPart
    MeshPart.meshFromShape(Shape=s, LinearDeflection=0.05, AngularDeflection=0.15).write(
        os.path.join(out_dir, name + ".stl"))


export_stl(base, "base")
export_stl(strap, "strap")
export_stl(slider, "slider", flip=True)   # pad up, so the ramp is not an overhang
export_stl(lid_a, "keeper")               # print two

try:
    doc.recompute()
    doc.saveAs(os.path.join(out_dir, "valve_bench.FCStd"))
except Exception:
    import traceback
    traceback.print_exc()

print("valve bench D, one 3/2 valve")
print("  body %.1f x %.1f x %.1f on a %.0f mm floor, strap on the body, hole %.0f for the nut"
      % (BODY_X, BODY_Y, BODY_Z, FLOOR, NUT_HOLE))
print("  slider ramp %.0f mm, rise %.1f mm (%.0f deg), dwell presses %.1f of the %.1f stop"
      % (RAMP_L, PAD_DROP, math.degrees(math.atan(rise)), PRESS, STOP))
print("  no printed air: barb in P, barb in A to the module, R open")
print("concept of the test, not of the head: valves are not measured")
ok = all(FITS)
print("checks: %s" % ("OK" if ok else "FAIL"), flush=True)
with open("/tmp/bench_report.txt", "a", encoding="utf-8") as fh:
    fh.write("checks: %s\n" % ("OK" if ok else "FAIL"))
if __name__ == "__main__" and not os.environ.get("OUT"):
    sys.exit(0 if ok else 1)
