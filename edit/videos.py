"""Six Larissa Kisslock Bag videos: 3 talking (T1-T3) + 3 overlay-only (O1-O3).

RAW:
  hb = "2/11 Handbag larissa" (talking, 44s)
  r1, r2 = silent B-roll of the bag (10s, 9s)

usage: python3 videos.py RAWDIR WORKDIR OUTDIR [names...]
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import render, TEXT_Y as TY

BOT = 1640    # under the bag on clasp close-ups (face fills the top)
INSIDE_Y = 1480  # under the open bag on "inside" shots
LOW = 1500    # a little lower when the bag sits low
WIDE = 260    # on the wall above the head in full-body shots (bag is at the waist)

# sticker stills: (raw, time, crop)
CLASP = ("hb", 15.9, (0.5, 0.62, 0.9))
INSIDE = ("hb", 19.0, (0.42, 0.72, 0.8))
FRONT = ("r2", 1.2, (0.62, 0.45, 0.8))
CHAIN = ("r1", 6.0, (0.6, 0.5, 0.85))


def stk(st, en, still, cx, cy, w=300, rot=0):
    raw, t, crop = still
    return (st, en, raw, t, cx, cy, w, rot, crop)


def starts(voice):
    out, t = [], 0.0
    for a, b in voice:
        out.append(round(t, 3)); t += b - a
    out.append(round(t, 3))
    return out


# ---------------- TALKING ----------------
T1v = [(0.20, 3.30), (4.80, 6.22), (11.20, 15.34), (15.34, 17.62), (17.62, 21.16), (28.38, 30.95), (31.00, 32.88)]
s = starts(T1v)
T1 = dict(voice=T1v,
    cut=[(s[1], s[2], "r1", 2.5),                       # "memang cantik" -> bag + chain
         (s[2] + 3.14, s[3], "r2", 1.0),                 # "macam handbag yang mahal" -> front logo
         (s[6], s[7], "hb", 33.2)],                      # "pakai raya" -> full outfit
    stickers=[stk(s[6] + 0.1, s[7], CLASP, 190, 760, 290, -7),
              stk(s[6] + 0.5, s[7], FRONT, 920, 1000, 270, 6)],
    texts=[(s[0], s[1], "Ramai sangat tanya pasal beg ni", "\U0001F440", TY, None),
           (s[1], s[2], "Memang cantik!", None, TY, "sparkle"),
           (s[2], s[3], "Comel + kualiti macam beg mahal", "✨", TY, None),
           (s[3], s[4], "Kisslock lain dari yang lain", None, BOT, "sparkle"),
           (s[4], s[5], "Kecil tapi muat macam-macam", None, INSIDE_Y, None),
           (s[5], s[6], "Masih ada stok", "\U0001F6CD️", LOW, "ding"),
           (s[6], s[7], "Ready untuk Raya!", None, WIDE, None)])

T2v = [(6.22, 9.68), (9.70, 11.08), (12.26, 15.34), (21.40, 23.70), (23.78, 25.72), (25.72, 28.40), (37.48, 39.94), (39.96, 41.38)]
s = starts(T2v)
T2 = dict(voice=T2v,
    cut=[(s[2] + 2.08, s[3], "r2", 1.0),                 # "macam handbag yang mahal"
         (s[4], s[5], "r1", 5.5),                        # "cantik berkilat"
         (s[5], s[6], "r2", 5.5),                        # "warna brown"
         (s[6], s[6] + 1.0, "hb", 33.5)],                # "sayang sangat dengan handbag" -> outfit
    stickers=[stk(s[6] + 0.05, s[6] + 1.0, CHAIN, 190, 800, 280, -6),
              stk(s[6] + 0.3, s[6] + 1.0, INSIDE, 920, 1000, 270, 5)],
    texts=[(s[0], s[1], "Hampir setahun pakai beg ni", "\U0001F90E", TY, None),
           (s[1], s[2], "...masih sayang!", None, TY, None),
           (s[2], s[3], "Kualiti macam beg mahal", "✨", TY, None),
           (s[3], s[4], "Berat & solid, bukan ringan", None, TY, None),
           (s[4], s[5], "Cantik berkilat", "✨", LOW, "sparkle"),
           (s[5], s[6], "Warna brown yang timeless", "\U0001F90E", LOW, None),
           (s[6], s[7], "Handle comel", None, TY, None),
           (s[7], s[8], "Harga dah turun!", "\U0001F525", LOW, "ding")])

T3v = [(39.96, 41.38), (41.42, 44.15), (15.34, 17.62), (33.70, 35.10), (35.22, 36.22), (36.42, 37.36), (28.38, 30.95), (31.00, 32.88)]
s = starts(T3v)
T3 = dict(voice=T3v,
    cut=[(s[7], s[8], "r2", 6.0)],                       # "pakai raya" -> bag front
    stickers=[stk(s[3] + 0.1, s[6], CLASP, 190, 760, 290, -7),
              stk(s[3] + 0.6, s[6], FRONT, 920, 900, 270, 6),
              stk(s[4] + 0.2, s[6], INSIDE, 190, 1180, 260, 4)],
    texts=[(s[0], s[1], "HARGA DAH TURUN!", "\U0001F525", LOW, "ding"),
           (s[1], s[2], "Grab sementara murah", "\U0001F6CD️", LOW, None),
           (s[2], s[3], "Kisslock lain dari yang lain", None, BOT, "sparkle"),
           (s[3], s[4], "Boleh sling...", None, WIDE, None),
           (s[4], s[6], "...atau hand carry", None, WIDE, None),
           (s[6], s[7], "Masih ada stok", "\U0001F6CD️", LOW, None),
           (s[7], s[8], "Ready untuk Raya!", None, LOW, "ding")])

# ---------------- OVERLAY ONLY ----------------
O1 = dict(clips=[("hb", 0.0, 3.0), ("r2", 1.0, 2.0), ("hb", 14.0, 3.0), ("r1", 5.5, 1.5),
                 ("hb", 31.0, 1.5), ("hb", 33.2, 2.0), ("r2", 6.5, 2.0)],
    stickers=[stk(11.1, 13.0, CLASP, 190, 760, 290, -7), stk(11.5, 13.0, INSIDE, 920, 1000, 270, 6)],
    texts=[(0.0, 3.0, "KISSLOCK BAG IS BACK!", "\U0001F90E", TY, "ding"),
           (3.0, 5.0, "Vintage & classy design", None, LOW, None),
           (5.0, 8.0, "Elegant gold kisslock detail", None, BOT, "sparkle"),
           (8.0, 11.0, "Hand carry + sling style", None, LOW, None),
           (11.0, 13.0, "Perfect for Raya & daily wear", None, WIDE, None),
           (13.0, 15.0, "BACK IN STOCK!", "\U0001F6CD️", LOW, "ding")])

O2 = dict(clips=[("r1", 0.0, 2.5), ("hb", 14.5, 2.5), ("hb", 17.6, 2.5), ("r1", 5.5, 2.5),
                 ("r2", 2.0, 2.5), ("hb", 33.2, 2.5), ("r2", 6.5, 2.0)],
    stickers=[stk(12.6, 15.0, CHAIN, 190, 760, 290, -7), stk(13.0, 15.0, FRONT, 920, 1000, 270, 6)],
    texts=[(0.0, 2.5, "5 sebab ramai cari beg ni", "\U0001F440", TY, None),
           (2.5, 5.0, "1. Kisslock emas yang classy", None, BOT, "sparkle"),
           (5.0, 7.5, "2. Kecil tapi muat macam-macam", None, INSIDE_Y, None),
           (7.5, 10.0, "3. Ada chain, boleh sling", None, LOW, None),
           (10.0, 12.5, "4. Solid & berkilat", "✨", TY, "sparkle"),
           (12.5, 15.0, "5. Sesuai untuk Raya", None, WIDE, None),
           (15.0, 17.0, "Tekan beg kuning sekarang", "\U0001F6CD️", LOW, "ding")])

O3 = dict(clips=[("hb", 33.0, 4.5), ("r1", 0.0, 3.0), ("r2", 4.5, 3.0), ("hb", 38.0, 2.5)],
    stickers=[stk(0.4, 4.5, CLASP, 190, 640, 300, -7),
              stk(1.2, 4.5, FRONT, 920, 860, 280, 6),
              stk(2.0, 4.5, INSIDE, 190, 1090, 280, 4)],
    texts=[(0.0, 2.2, "Beg Raya tahun ni?", "✨", WIDE, None),
           (2.2, 4.5, "Classy • Vintage • Elegant", None, WIDE, None),
           (4.5, 7.5, "Gold kisslock + chain", None, LOW, "sparkle"),
           (7.5, 10.5, "Warna brown yang timeless", "\U0001F90E", LOW, None),
           (10.5, 13.0, "Grab sebelum habis!", "\U0001F6CD️", LOW, "ding")])

VIDEOS = {"T1_ramai_tanya": T1, "T2_setahun_pakai": T2, "T3_harga_turun": T3,
          "O1_kisslock_back": O1, "O2_5_sebab": O2, "O3_raya_collage": O3}

if __name__ == "__main__":
    rawdir, work, outdir = sys.argv[1:4]
    names = sys.argv[4:] or list(VIDEOS)
    raws = {k: f"{rawdir}/{k}.mov" for k in ("hb", "r1", "r2")}
    os.makedirs(outdir, exist_ok=True)
    for nm in names:
        tot = render(VIDEOS[nm], raws, f"{work}/sfx", f"{work}/{nm}", f"{outdir}/{nm}.mp4")
        print(nm, round(tot, 2), "s")
