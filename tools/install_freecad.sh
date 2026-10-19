#!/bin/sh
# Install FreeCAD 1.0.2 (the version the generators are written for) on a Linux x86-64 VM, e.g. a cloud
# agent session. Downloads the official AppImage (~800 MB) and unpacks it, so no FUSE is needed.
# Idempotent: does nothing when it is already there. Takes about a minute.
#   sh tools/install_freecad.sh            # installs to /opt/freecad, links /usr/local/bin/freecadcmd
#   freecadcmd -c "REPO='$PWD'; exec(open('module/stage3v4_coaxial_chamber.py').read())"
# On macOS install FreeCAD 1.0.x from freecad.org instead.
set -e
DEST=${FREECAD_DIR:-/opt/freecad}
VER=1.0.2
URL=https://github.com/FreeCAD/FreeCAD/releases/download/$VER/FreeCAD_$VER-conda-Linux-x86_64-py311.AppImage
if [ ! -x "$DEST/usr/bin/freecadcmd" ]; then
  TMP=$(mktemp -d)
  curl -fsSL -o "$TMP/fc.AppImage" "$URL"
  chmod +x "$TMP/fc.AppImage"
  (cd "$TMP" && ./fc.AppImage --appimage-extract >/dev/null)
  mkdir -p "$(dirname "$DEST")"
  rm -rf "$DEST"
  mv "$TMP/squashfs-root" "$DEST"
  rm -rf "$TMP"
fi
for b in freecadcmd freecad; do
  ln -sf "$DEST/usr/bin/$b" "/usr/local/bin/$b" 2>/dev/null || true
done
# The generators print Ø, °, Cyrillic: without a UTF-8 locale FreeCAD's Python fails on the first one.
LANG=C.UTF-8 LC_ALL=C.UTF-8 "$DEST/usr/bin/freecadcmd" --version | tail -1
