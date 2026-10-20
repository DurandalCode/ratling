# -*- coding: utf-8 -*-
"""
docs/img/weights_a16_a19.png: the two views from tools/weights_picture.py and a table of the weight by material
(plain Python with Pillow).

    python3 tools/weights_sheet.py exports/weights/a19.png exports/weights/a16.png docs/img/weights_a16_a19.png

The grams are docs/weights.md's, regrouped: a module is 74.1 g printed, 271.7 g metal (barrel 106.5 steel, chamber
tube 122.3 aluminium, rods and nuts 34.9 steel, pilot fitting 8 brass) and 4.2 g rubber. The head's 20 / 23
fittings are brass (160 / 184 g), the rest of its bought parts steel. The rear grip (an estimate) is 197 g
printed and 16 g of bolts and spring; the hoses and the bleed valve with its hose go under other.
"""
import sys

from PIL import Image, ImageDraw, ImageFont

N = {"A16": 16, "A19": 19}
G = {}
for t, n in N.items():
    head_brass = 8 * (20 if n == 16 else 23)
    head_steel = (521 if n == 16 else 562) - head_brass
    G[t] = {
        "p_mod": 74.1 * n,
        "p_frame": (274 if n == 16 else 255) + (324 if n == 16 else 295) + 148 + 171,
        "p_head": (1017 if n == 16 else 1019) + 472,
        "p_grip": 197,
        "steel": n * (106.5 + 34.9) + 7 + 32 + head_steel + 21 + 16,
        "alu": n * 122.3 + 179,
        "brass": n * 8 + head_brass,
        "other": n * 4.2 + (16 if n == 16 else 19) + 70,
        "casing": 263,
        "sleeves": 610 if n == 16 else 710,
    }
    g = G[t]
    g["print"] = g["p_mod"] + g["p_frame"] + g["p_head"] + g["p_grip"]
    g["metal"] = g["steel"] + g["alu"] + g["brass"]
    # weights.md's totals: its rows are rounded per item, so the sums above run 2-3 g over
    g["total"] = 9062 if n == 16 else 10111
    g["all"] = 9935 if n == 16 else 11084

PRINT, STEEL, ALU, BRASS, RUBBER = (237, 140, 38), (77, 82, 92), (199, 204, 214), (158, 148, 107), (20, 20, 20)
ROWS = [  # (text, key, swatch, style): style h = group head, s = sub row, t = total, a = add-on
    ("Печать PETG", "print", PRINT, "h"),
    ("пробки, ярма и кольца модулей", "p_mod", None, "s"),
    ("плиты пакета и ЦТ, ручка, площадка", "p_frame", None, "s"),
    ("головка, плита головки, коробка", "p_head", None, "s"),
    ("рукоять с гашеткой (оценка, не нарисована)", "p_grip", None, "s"),
    ("Металл", "metal", None, "h"),
    ("сталь: стволы, шпильки, валы, подшипники", "steel", STEEL, "s"),
    ("алюминий: трубы камер, 4 направляющие", "alu", ALU, "s"),
    ("латунь: фитинги (оценка)", "brass", BRASS, "s"),
    ("Прочее: резина, шланги, кран сброса", "other", RUBBER, "h"),
    ("ИТОГО без кожуха и насадок", "total", None, "t"),
    ("+ кожух головки, печать (оценка)", "casing", None, "a"),
    ("+ дульные насадки с бандажом, печать", "sleeves", None, "a"),
    ("ВСЁ ВМЕСТЕ", "all", None, "t"),
]

top, bot, out = sys.argv[1:4]
F = "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf"
f, fb, fs = (ImageFont.truetype(F % "", 22), ImageFont.truetype(F % "-Bold", 24),
             ImageFont.truetype(F % "", 17))
views = [Image.open(p).convert("RGB") for p in (top, bot)]
vw = max(v.width for v in views)
W, H = vw + 860, max(sum(v.height for v in views) + 120, 1000)
im = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(im)
y = 0
for v, t in zip(views, ("A19 (соты 19)", "A16 (кольца 4 + 12)")):
    d.text((30, y + 20), t, font=ImageFont.truetype(F % "-Bold", 30), fill="black")
    im.paste(v, (0, y + 60))
    y += v.height + 60

x0, c16, c19 = vw + 30, W - 190, W - 90
y = 40
d.text((x0, y), "Вес, кг", font=fb, fill="black")
d.text((c16, y), "A16", font=fb, fill="black")
d.text((c19, y), "A19", font=fb, fill="black")
y += 60
for text, k, sw, st in ROWS:
    font = fb if st in "ht" else f
    if st == "t":
        d.line((x0, y - 12, W - 20, y - 12), fill="black", width=2)
    if st == "h" and k != "print":
        y += 14
    if sw:
        d.rectangle((x0, y, x0 + 28, y + 28), fill=sw, outline=(60, 60, 60))
    d.text((x0 + 42, y), text, font=font, fill="black")
    for c, t in ((c16, "A16"), (c19, "A19")):
        d.text((c, y), "%.2f" % (G[t][k] / 1000), font=font, fill="black")
    y += 44 if st != "t" else 52
y += 10
for line in ("Цвет на видах — материал: оранжевое — печать, серое — сталь,",
             "светло-серое — алюминий, серо-жёлтое — латунь, чёрное — резина.",
             "Без рюкзака, ресивера, ремня и скина. Головка у A19 нарисована",
             "та, что у 16 (ротор на 19 ещё не нарисован), её вес пересчитан.",
             "Вместо насадок на видах дульные кольца: насадки закрыли бы стволы."):
    d.text((x0, y), line, font=fs, fill=(60, 60, 60))
    y += 26
im.save(out, optimize=True)
for t in N:
    print(t, {k: round(v) for k, v in G[t].items()})
