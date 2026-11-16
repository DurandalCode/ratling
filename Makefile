# Shortcuts for exchanging editable GPT workspaces with the live sources.
# Run from the repository root. Override *_WORK on the command line if needed.

MASK := experiments/gpt-mask/mask
FREECADCMD ?= freecadcmd
GATLING_WORK ?= $(abspath $(CURDIR)/../marble_machine)
PISTOL_WORK ?= $(abspath $(CURDIR)/../mechanismus)
GATLING_REPORTS := \
	exports/gatling_fat_coax_qev/gatling_fat_coax_qev_report.txt \
	exports/gatling_linear_breech/gatling_linear_breech_report.txt \
	exports/gatling_linear_breech_bench/gatling_linear_breech_bench_report.txt
STAGE3_V13_REPORT := exports/stage3_qev_v13/stage3_qev_v13_report.txt

# The obfuscators may build the live housing to preserve its outline. On the
# owner's Mac FreeCAD lives inside the application bundle and is not on PATH.
FREECAD_MAC_BIN := /Applications/FreeCAD.app/Contents/Resources/bin
ifneq ($(wildcard $(FREECAD_MAC_BIN)/freecadcmd),)
export PATH := $(FREECAD_MAC_BIN):$(PATH)
endif
export LANG := C.UTF-8
export LC_ALL := C.UTF-8

.DEFAULT_GOAL := help

.PHONY: help gpt-out gpt-in gpt-status \
	gatling-out gatling-in gatling-status \
	pistol-out pistol-in pistol-status \
	plates gatling-plates gatling-stl pistol-plates pistol-stl

help:
	@printf '%s\n' \
	  'GPT workspace sync (run from the live repository):' \
	  '  make gpt-out          live sources -> both GPT workspaces' \
	  '  make gpt-in           both GPT workspaces -> live sources' \
	  '  make gpt-status       show pending edits on both sides' \
	  '' \
	  '  make gatling-out      live -> $(GATLING_WORK)' \
	  '  make gatling-in       $(GATLING_WORK) -> live' \
	  '  make gatling-status   show gatling sync state' \
	  '' \
	  '  make pistol-out       live -> $(PISTOL_WORK)' \
	  '  make pistol-in        $(PISTOL_WORK) -> live' \
	  '  make pistol-status    show pistol sync state' \
	  '' \
	  'Print plates (fresh STL exports, then Bambu Studio .3mf):' \
	  '  make plates           slice both complete default print sets' \
	  '  make gatling-plates   regenerate + slice the gatling hand bench' \
	  '  make gatling-stl      regenerate and check gatling STLs only' \
	  '  make pistol-plates    regenerate + slice all pistol print groups' \
	  '  make pistol-stl       regenerate and check pistol STLs only' \
	  '' \
	  'No sync target uses --force. Editable GPT edits are merged or kept;' \
	  'context files always refresh from live on out.'

gpt-out: gatling-out pistol-out

gpt-in: gatling-in pistol-in

gpt-status: gatling-status pistol-status

gatling-out:
	$(MASK) out -p gatling "$(GATLING_WORK)"

gatling-in:
	$(MASK) in -p gatling "$(GATLING_WORK)"

gatling-status:
	MECHANISMUS="$(GATLING_WORK)" $(MASK) status -p gatling

pistol-out:
	$(MASK) out -p pistol "$(PISTOL_WORK)"

pistol-in:
	$(MASK) in -p pistol "$(PISTOL_WORK)"

pistol-status:
	MECHANISMUS="$(PISTOL_WORK)" $(MASK) status -p pistol

# Bambu Studio projects. Always rebuild STLs first: exports/ is gitignored and
# may hold an older model. A [FAIL] report or invalid pistol part stops slicing.
plates: gatling-plates pistol-plates

gatling-plates: gatling-stl
	sh gatling/linear_breech_bench_plates.sh

gatling-stl:
	$(FREECADCMD) -c "REPO='$(CURDIR)'; exec(open('gatling/fat_coax_qev.py').read())"
	$(FREECADCMD) -c "REPO='$(CURDIR)'; exec(open('gatling/linear_breech.py').read())"
	$(FREECADCMD) -c "REPO='$(CURDIR)'; exec(open('gatling/linear_breech_bench.py').read())"
	@if grep -n '\[FAIL\]' $(GATLING_REPORTS); then \
	  printf '%s\n' 'Refusing to slice: a gatling generator reported [FAIL].' >&2; \
	  exit 1; \
	fi

pistol-plates: pistol-stl
	sh pistol/build/make_plates.sh

pistol-stl:
	$(FREECADCMD) -c "REPO='$(CURDIR)'; exec(open('module/stage3_v13.py').read())"
	@if grep -n '\[FAIL\]' $(STAGE3_V13_REPORT); then \
	  printf '%s\n' 'Refusing to slice: the v1.3 valve generator reported [FAIL].' >&2; \
	  exit 1; \
	fi
	$(FREECADCMD) -c "REPO='$(CURDIR)'; CHECKS=False; VALVE='v13'; exec(open('pistol/build/export_parts.py').read())"
	@python3 -c "import json,sys; parts=json.load(open('exports/pistol_build/parts.json'))['parts']; bad=[p['name'] for p in parts if not p['valid'] or p.get('orientation') == 'FAIL']; print('Pistol export check:', 'OK' if not bad else 'FAIL: ' + ', '.join(bad)); sys.exit(bool(bad))"
