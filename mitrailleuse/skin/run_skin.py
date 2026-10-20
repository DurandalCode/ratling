# -*- coding: utf-8 -*-
"""
Run ratling_skin.py headless in the FreeCAD GUI (it needs a display; on a VM use xvfb-run) and quit.

    xvfb-run -a -s "-screen 0 2560x1600x24" env LANG=C.UTF-8 LC_ALL=C.UTF-8 \
        BARRELS=16 TOP=arch GRIP=butt SHEETS=0 freecad mitrailleuse/skin/run_skin.py

The report goes to exports/ratling_skin/A<n>_<top>_<grip>.log, errors too.
"""

import os
import sys
import traceback

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
name = "A%s_%s_%s" % (os.environ.get("BARRELS", "16"), os.environ.get("TOP", "arch"), os.environ.get("GRIP", "butt"))
os.makedirs(os.path.join(REPO, "exports", "ratling_skin"), exist_ok=True)
log = open(os.path.join(REPO, "exports", "ratling_skin", name + ".log"), "w", encoding="utf-8")
sys.stdout = log
try:
    exec(open(os.path.join(REPO, "mitrailleuse", "skin", "ratling_skin.py"), encoding="utf-8").read(),
         {"REPO": REPO, "__name__": "__main__"})
except Exception:
    log.write(traceback.format_exc())
log.close()
os._exit(0)
