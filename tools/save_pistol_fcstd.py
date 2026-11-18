# Regenerate pistol/hammer_assembly.py in freecadcmd and save exports/pistol_hammer_assembly.FCStd with every
# object visible and its look colours: freecadcmd writes no GuiDocument.xml, so append one (else the GUI opens
# the groups hidden and all grey). Run:
#   freecadcmd -c "REPO='$PWD'; exec(open('tools/save_pistol_fcstd.py').read())"

import os, zipfile
_src = open(os.path.join(REPO, 'pistol', 'hammer_assembly.py')).read()
_old = "    if App.GuiUp:\n        o.ViewObject.ShapeColor = col\n        o.ViewObject.Transparency = transp\n    return o"
assert _old in _src
_COLS = {}
exec(_src.replace(_old, "    _COLS[o.Name] = (col, transp)\n" + _old))
for o in doc.Objects:
    o.Visibility = True
doc.recompute()
out = os.path.join(REPO, "exports", "pistol_hammer_assembly.FCStd")
doc.saveAs(out)
def packed(c):
    r, g, b = [max(0, min(255, int(round(v * 255)))) for v in c[:3]]
    return (r << 24) | (g << 16) | (b << 8)
vps = []
for o in doc.Objects:
    props = ['<Property name="Visibility" type="App::PropertyBool" status="1"><Bool value="true"/></Property>']
    if o.Name in _COLS:
        col, tr = _COLS[o.Name]
        props.append('<Property name="ShapeColor" type="App::PropertyColor"><PropertyColor value="%d"/></Property>' % packed(col))
        props.append('<Property name="Transparency" type="App::PropertyPercent"><Integer value="%d"/></Property>' % int(tr))
    exp = ' expanded="1"' if o.TypeId == "App::DocumentObjectGroup" else ' expanded="0"'
    vps.append('<ViewProvider name="%s"%s>\n<Properties Count="%d" TransientCount="0">\n%s\n</Properties>\n</ViewProvider>' % (o.Name, exp, len(props), "\n".join(props)))
xml = ("<?xml version='1.0' encoding='utf-8'?>\n<Document SchemaVersion=\"1\" HasExpansion=\"1\">\n<ViewProviderData Count=\"%d\">\n%s\n</ViewProviderData>\n<Camera settings=\"\"/>\n</Document>\n"
       % (len(vps), "\n".join(vps)))
with zipfile.ZipFile(out, "a", zipfile.ZIP_DEFLATED) as z:
    if "GuiDocument.xml" not in z.namelist():
        z.writestr("GuiDocument.xml", xml)
print("SAVED", out, len(doc.Objects), "coloured", len(_COLS))
