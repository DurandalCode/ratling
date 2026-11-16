# -*- coding: utf-8 -*-
"""
Gatling export: the imported coax module is replaced by its outer solids.

The station still execs this file. The copy it gets is the same solids (nose,
flange, ears, tube, yoke, rods), written as geometry, without the stack source.
Context only: `in` does not take the file back. Rebuilt from the live module on
each `out`, so a basket drawn against this form fits the live station.
"""

from __future__ import print_function

import json
import os
import re
import shutil
import subprocess
import tempfile
import zlib

_SHAPES = (
    "rp", "sr", "diaphragm", "front_cover", "front_yoke",
    "barrel_stub", "chamber", "hardware", "fitting",
)

_DUMP = r"""
import json, os, re, sys
REPO = os.environ["PACK_REPO"]
OUT = os.environ["PACK_OUT"]
sys.path.insert(0, REPO)
ns = {"REPO": REPO, "GATLING_FAT_COAX_LIBRARY": True, "__name__": "pack"}
exec(open(os.path.join(REPO, "gatling", "fat_coax_qev.py"), encoding="utf-8").read(), ns)
import Part
breech = open(os.path.join(REPO, "gatling", "linear_breech.py"), encoding="utf-8").read()
used = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", breech))
nums = []
for name in sorted(ns):
    if not name[:1].isalpha() or name not in used:
        continue
    v = ns[name]
    if isinstance(v, bool):
        continue
    if isinstance(v, (int, float)):
        nums.append({"name": name, "repr": repr(v)})
    elif isinstance(v, tuple) and v and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in v):
        nums.append({"name": name, "repr": repr(v)})
vols = {}
for name in %s:
    shape = ns[name]
    path = os.path.join(OUT, name + ".brep")
    shape.exportBrep(path)
    raw = open(path, encoding="ascii").read()
    back = Part.Shape()
    back.importBrepFromString(raw)
    if abs(back.Volume - shape.Volume) > 1e-3 or not back.isValid():
        raise SystemExit("roundtrip failed for " + name)
    vols[name] = shape.Volume
json.dump({"nums": nums, "vols": vols}, open(os.path.join(OUT, "meta.json"), "w"), indent=1)
print("PACK_OK")
""" % (repr(_SHAPES),)


def _wrap(comp):
    """Comma-separated bytes, broken on commas so a later rename cannot join digits."""
    parts = [str(b) for b in comp]
    lines, line, width = [], [], 0
    for p in parts:
        line.append(p)
        width += len(p) + 1
        if width >= 100:
            lines.append(",".join(line))
            line, width = [], 0
    if line:
        lines.append(",".join(line))
    # A comma between lines too: the loader strips newlines before splitting.
    return ",\n".join(lines)


def _build_pack():
    freecad = shutil.which("freecadcmd")
    if not freecad:
        raise ValueError("freecadcmd is not on PATH; the housing form is taken from the live module")
    repo = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
    tmp = tempfile.mkdtemp(prefix="gatling-pack-")
    try:
        script = os.path.join(tmp, "dump.py")
        with open(script, "w", encoding="utf-8") as f:
            f.write(_DUMP)
        env = dict(os.environ)
        env["LANG"] = "C.UTF-8"
        env["LC_ALL"] = "C.UTF-8"
        env["PACK_REPO"] = repo
        env["PACK_OUT"] = tmp
        proc = subprocess.run(
            [freecad, script], cwd=repo, env=env,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        meta_path = os.path.join(tmp, "meta.json")
        if proc.returncode != 0 or not os.path.exists(meta_path) or "PACK_OK" not in proc.stdout:
            tail = (proc.stdout or "")[-2000:]
            raise ValueError("could not read the housing form\n" + tail)
        meta = json.load(open(meta_path, encoding="utf-8"))
        blobs = {}
        for name in _SHAPES:
            raw = open(os.path.join(tmp, name + ".brep"), encoding="ascii").read()
            blobs[name] = _wrap(zlib.compress(raw.encode("ascii"), 9))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    lines = [
        "# -*- coding: utf-8 -*-",
        '"""One station housing. The solids are the outer form."""',
        "import math",
        "import zlib",
        "",
        "import FreeCAD as App",
        "import Part",
        "",
        "V = App.Vector",
        "",
    ]
    for item in meta["nums"]:
        if not re.match(r"[A-Za-z_][A-Za-z0-9_]*$", item["name"]):
            raise ValueError("unexpected name %r" % item["name"])
        if not re.match(r"-?[0-9.eE+,() ]+$", item["repr"]):
            raise ValueError("unexpected value for %s" % item["name"])
        lines.append("%s = %s" % (item["name"], item["repr"]))
    lines += [
        "",
        "def at(r, a_deg, z=0.0):",
        "    a = math.radians(a_deg)",
        "    return V(r * math.cos(a), r * math.sin(a), z)",
        "",
        "def _s(blob):",
        '    raw = zlib.decompress(bytes(int(x) for x in blob.replace("\\n", "").split(",") if x))',
        '    sh = Part.Shape()',
        '    sh.importBrepFromString(raw.decode("ascii"))',
        "    return sh",
        "",
    ]
    for name in _SHAPES:
        lines.append("%s = _s(\"\"\"%s\"\"\")" % (name, blobs[name]))
    lines.append("")
    return "\n".join(lines)


def apply(rel, text):
    """Return the outer solids for the coax module; leave every other file unchanged."""
    if rel != "gatling/fat_coax_qev.py":
        return text
    cached = getattr(apply, "pack", None)
    if cached is None:
        cached = _build_pack()
        apply.pack = cached
    return cached
