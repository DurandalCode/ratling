# GPT-mask shell overlays

`.brep` files here replace the matching housing solid after
`pistol/hammer_assembly.py` builds it. Written by:

```sh
python3 experiments/gpt-mask/mask_sync.py in /tmp/mask-D
```

Expected names: `frame_lower.brep`, `frame_upper.brep`, `side_wall.brep`,
`side_band.brep`, `side_plate_r.brep`, `grip_left.brep`, `grip_right.brep`,
`guard.brep`, `detent_box.brep`.

Delete a file to fall back to the parametric generator for that part.
The `*.brep` files are gitignored.
