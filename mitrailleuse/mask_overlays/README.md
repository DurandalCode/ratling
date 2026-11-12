# Mechanismus shell overlays (mitrailleuse / gatling)

`.brep` files here replace matching solids in `pack_frame.py`, `rear_frame.py`,
and `carry_mount.py` after they are built. Written by:

```sh
python3 experiments/gpt-mask/mask_sync.py in --product mitrailleuse
```

Expected names match `experiments/gpt-mask/products/mitrailleuse.json` (`a16_rear_plate.brep`, …).
The `*.brep` files are gitignored.
