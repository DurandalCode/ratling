# Reimport maps (keep out of GPT workspaces)

## A / B / C — housing only

| A | B / C | Live object / variable |
|---|---|---|
| `Shell_tray` | `Frame_lower` | `Frame_lower` / `frame_lower` |
| `Shell_cover` | `Frame_upper` | `Frame_upper` / `frame_upper` |
| `Cover_left_wall` | `Frame_side` | `Frame_side` / `side_wall` |
| `Cover_left_band` | `Frame_side_band` | `Frame_side_band` / `side_band` |
| `Cover_right` | `Frame_right` | `Frame_right` / `side_plate_r` |
| `Grip_left` | `Grip_left` | `Grip_left` / `grip_left` |
| `Grip_right` | `Grip_right` | `Grip_right` / `grip_right` |
| `Bail` | `Trigger_guard` | `Trigger_guard` / `guard` |
| `Latch_box` | `Detent_housing` | `Detent_housing` / `detent_box` |
| — | `Cylinder` (C) | `Block` / `block` |

## D — full mechanism, renamed

| D name | Live object / variable |
|---|---|
| `Shell_tray` | `Frame_lower` / `frame_lower` |
| `Shell_cover` | `Frame_upper` / `frame_upper` |
| `Cover_left_wall` | `Frame_side` / `side_wall` |
| `Cover_left_band` | `Frame_side_band` / `side_band` |
| `Cover_right` | `Frame_right` / `side_plate_r` |
| `Grip_*` / `Bail` / `Index_box` | same dress names / `detent_box` |
| `Stack_body` / `Stack_cap` | `Valve_body_*` / `valve_body`, `valve_cap` |
| `Coupler` | `Lock_housing` / `lock_housing_h` |
| `Spindle` | `Chamber_axle` / `axle` |
| `Rotor` | `Block` / `block` |
| `Sector` / `Yoke` / `Thumb_lever` / `Pedal` | pose keys Sector/Slider/Hammer/Trigger |
| `Click_tooth` | `Pawl` |
| `Limit_switch` | `Vent_valve` / `mini_valves` |
| `Cable` / `Signal_wire` / `Sense_wire` / `Wire_tee` | hose / pilot_line / gauge_line / tee |
| `Stack_ties` / `Coupler_screws` | `valve_rods` / `lock_bolts` |
| `Return_springs` / `Lever_axle` / `Yoke_rod` | mainsprings / shaft / guide_rod |
| `Rotor_strap` / `Spindle_nose` / `Spindle_plug` | top_strap / nose / axle_plug |

Regenerate fixture solids:

```sh
export LANG=C.UTF-8 LC_ALL=C.UTF-8
freecadcmd -c "REPO='$PWD'; exec(open('experiments/gpt-mask/pull_real_shell.py').read())"
```
