"""Round 2: voice is NEVER cut (full take 0-44.1s), B-roll pasted over matching lines.

  TF_full_white  : full voice, white text style (as before), stickers, SFX
  S1_talk        : full voice, style-1 script title behind the person, matched B-roll
  S1_overlay     : style-1 fast pose cuts, no voice, title behind the person

usage: python3 videos2.py RAWDIR WORKDIR OUTDIR FONTDIR [names...]
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import render, TEXT_Y as TY
import style1

BOT, INSIDE_Y, LOW, WIDE = 1640, 1480, 1500, 260
CLASP = ("hb", 15.9, (0.5, 0.62, 0.9))
INSIDE = ("hb", 19.0, (0.42, 0.72, 0.8))
FRONT = ("r2", 1.2, (0.62, 0.45, 0.8))
CHAIN = ("r1", 6.0, (0.6, 0.5, 0.85))


def stk(st, en, still, cx, cy, w=280, rot=0):
    raw, t, crop = still
    return (st, en, raw, t, cx, cy, w, rot, crop)


FULL = [(0.0, 44.10)]  # whole take, untouched
# B-roll over the voice, timed to what she is saying (output time == raw time)
CUTS = [(3.80, 6.20, "r1", 2.5),    # "Ya memang cantik ... memang cantik"
        (14.34, 15.34, "r2", 1.0),  # "macam handbag yang mahal"
        (23.80, 25.75, "r1", 5.5),  # "lepas tu cantik berkilat"
        (25.75, 28.40, "r2", 5.5),  # "warna ... brown sangat-sangat cantik"
        (42.00, 44.10, "r2", 6.0)]  # "grab ... sangat-sangat murah"

TF = dict(voice=FULL, cut=CUTS,
    stickers=[stk(33.8, 37.6, CLASP, 190, 760, 280, -7),
              stk(34.3, 37.6, FRONT, 920, 900, 270, 6),
              stk(34.8, 37.6, INSIDE, 190, 1180, 260, 4)],
    texts=[(0.0, 3.3, "Ramai sangat tanya pasal beg ni", "\U0001F440", TY, None),
           (3.8, 6.2, "Memang cantik!", None, TY, "sparkle"),
           (6.3, 11.1, "Hampir setahun pakai, masih sayang", "\U0001F90E", TY, None),
           (11.2, 15.3, "Comel + kualiti macam beg mahal", "✨", TY, None),
           (15.4, 17.6, "Kisslock lain dari yang lain", None, BOT, "sparkle"),
           (17.6, 21.2, "Kecil tapi muat macam-macam", None, INSIDE_Y, None),
           (21.4, 23.7, "Berat & solid, bukan ringan", None, TY, None),
           (23.8, 25.75, "Cantik berkilat", "✨", LOW, "sparkle"),
           (25.75, 28.4, "Warna brown yang timeless", "\U0001F90E", LOW, None),
           (28.4, 31.0, "Masih ada stok", "\U0001F6CD️", LOW, "ding"),
           (31.0, 33.6, "Boleh pakai Raya tahun depan", None, LOW, None),
           (33.7, 36.3, "Boleh sling atau hand carry", None, WIDE, None),
           (38.2, 39.9, "Handle comel", None, TY, None),
           (40.0, 41.4, "Harga dah turun!", "\U0001F525", LOW, "ding"),
           (41.4, 44.1, "Grab sementara murah", "\U0001F6CD️", LOW, None)])

S1T = dict(voice=FULL, cut=CUTS, texts=[])

S1O = dict(clips=[("hb", 33.0, 1.0), ("hb", 34.2, 0.9), ("r1", 3.5, 1.0), ("hb", 35.3, 0.9),
                  ("hb", 31.0, 1.0), ("r2", 1.0, 1.0), ("hb", 36.4, 1.0), ("r1", 6.0, 0.9),
                  ("hb", 32.2, 0.8), ("r2", 6.5, 1.2), ("hb", 37.0, 0.8)], texts=[])

PLAIN = {"TF_full_white": TF}
STYLE1 = {"S1_talk": S1T, "S1_overlay": S1O}

if __name__ == "__main__":
    rawdir, work, outdir, fontdir = sys.argv[1:5]
    names = sys.argv[5:] or [*PLAIN, *STYLE1]
    raws = {k: f"{rawdir}/{k}.mov" for k in ("hb", "r1", "r2")}
    os.makedirs(outdir, exist_ok=True)
    sfx = f"{work}/sfx"
    for nm in names:
        if nm in PLAIN:
            t = render(PLAIN[nm], raws, sfx, f"{work}/{nm}", f"{outdir}/{nm}.mp4")
        else:
            base = f"{work}/{nm}_base.mp4"
            t = render(STYLE1[nm], raws, sfx, f"{work}/{nm}", base, crf="12")
            n = style1.masks(base, f"{work}/{nm}_mask")
            title = f"{work}/{nm}_title.png"
            style1.title_png(title, (f"{fontdir}/GreatVibes-Regular.ttf",
                                     "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"))
            style1.composite(base, f"{work}/{nm}_mask", title, f"{outdir}/{nm}.mp4")
        print(nm, round(t, 2), "s", flush=True)
