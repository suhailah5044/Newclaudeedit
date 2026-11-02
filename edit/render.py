import subprocess, json, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = os.path.dirname(os.path.abspath(__file__))
RAW, OUT = f"{S}/raw", f"{S}/build"
os.makedirs(OUT, exist_ok=True)
FONT = f"{S}/fonts/Fredoka.ttf"
W, H, FPS = 1080, 1920, 30

# (video clip, v_in, v_out, audio clip or None, a_in, title, subtitle, text_y)
# Voice: one take only per line (best tone, usually the last take).
SEGS = [
    ("c02", 0.30, None, "c14", 3.40, 5.55, "Stand tablet FULL METAL", "besi solid, bukan plastik", 250),
    ("c11", 2.00, None, "c11", 2.00, 4.55, "7SKIN 7S-06", "Metal Tablet Stand", 200),
    ("c05", 7.25, None, "c05", 7.25, 11.65, "Rotate 360°", "tapak pusing ke semua arah", 170),
    ("c01", 1.00, 3.30, None, 0, 0, "Dual-axis", "tinggi & sudut boleh laras", 170),
    ("c12", 38.0, 41.0, None, 0, 0, "Laras ikut selesa", "tengok video, baca, meeting", 200),
    ("c14", 15.85, None, "c14", 15.85, 21.45, "Silikon anti-slip", "tablet tak calar, tak tergelincir", 150),
    ("c14", 24.75, None, "c14", 24.75, 28.10, "Stabil", "tak goyang masa guna", 150),
    ("c08", 1.30, 4.30, None, 0, 0, "FREE Allen key", "ketatkan skru kalau longgar", 150),
    ("c07", 4.35, None, "c07", 4.35, 7.15, "Tablet • Phone • E-reader", "sesuai untuk banyak peranti", 150),
    ("c13", 20.60, None, "c13", 20.60, 25.95, "Boleh lipat & travel friendly", "muat dalam beg, beg sekolah, drawer", 150),
    ("c02", 5.30, 8.30, None, 0, 0, "Panel 17.5cm • Tapak 13.4cm", "nipis 11.4cm bila dilipat", 230),
    ("c07", 11.53, None, "c07", 11.53, 16.05, "Harga murah", "kualiti premium", 150),
    ("c13", 32.45, None, "c13", 32.45, 35.20, "Highly recommended!", "tekan beg kuning sekarang", 150),
]
# optional per-segment override of text y from argv json
if len(sys.argv) > 1:
    for k, v in json.loads(sys.argv[1]).items():
        s = list(SEGS[int(k)]); s[8] = v; SEGS[int(k)] = tuple(s)


def text_png(path, title, sub):
    img = Image.new("RGBA", (W, 330), (0, 0, 0, 0))
    ft = ImageFont.truetype(FONT, 92); ft.set_variation_by_name("Bold")
    fs = ImageFont.truetype(FONT, 58); fs.set_variation_by_name("Medium")
    def fit(f, txt, size, name):
        while f.getlength(txt) > W - 120:
            size -= 4; f = ImageFont.truetype(FONT, size); f.set_variation_by_name(name)
        return f
    ft = fit(ft, title, 92, "Bold"); fs = fit(fs, sub, 58, "Medium")
    lines = [(title, ft, 30), (sub, fs, 150)]
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(shadow)
    d = ImageDraw.Draw(img)
    for txt, f, y in lines:
        x = (W - f.getlength(txt)) / 2
        sd.text((x, y + 4), txt, font=f, fill=(0, 0, 0, 170), stroke_width=6, stroke_fill=(0, 0, 0, 170))
    shadow = shadow.filter(ImageFilter.GaussianBlur(9))
    for txt, f, y in lines:
        x = (W - f.getlength(txt)) / 2
        d.text((x, y), txt, font=f, fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(40, 40, 40, 90))
    out = Image.alpha_composite(shadow, img)
    # orange accent bar under title (product colour)
    ad = ImageDraw.Draw(out)
    tw = ft.getlength(title)
    ad.rounded_rectangle(((W - 90) / 2, 132, (W + 90) / 2, 140), 4, fill=(255, 140, 0, 255))
    out.save(path)


GRADE = "eq=brightness=0.025:contrast=1.05:saturation=1.08:gamma=1.02,unsharp=5:5:0.45:5:5:0"
PUNCH = f"scale=w='trunc({W}*(1+0.06*max(0\\,1-t/0.3))/2)*2':h=-2:eval=frame,crop={W}:{H}"

parts = []
for i, (vc, vin, vout, ac, ain, aout, title, sub, ty) in enumerate(SEGS):
    dur = (aout - ain) if ac else (vout - vin)
    png = f"{OUT}/t{i:02d}.png"; text_png(png, title, sub)
    seg = f"{OUT}/s{i:02d}.mp4"
    cmd = ["ffmpeg", "-nostdin", "-v", "error", "-y",
           "-ss", f"{vin}", "-t", f"{dur}", "-i", f"{RAW}/{vc}.mov",
           "-loop", "1", "-t", f"{dur}", "-i", png]
    if ac:
        cmd += ["-ss", f"{ain}", "-t", f"{dur}", "-i", f"{RAW}/{ac}.mov"]
        aud = "[2:a]aformat=sample_rates=48000:channel_layouts=stereo,highpass=f=80,afade=t=in:d=0.04,afade=t=out:st=%.3f:d=0.06[a]" % (dur - 0.06)
    else:
        cmd += ["-f", "lavfi", "-t", f"{dur}", "-i", "anullsrc=r=48000:cl=stereo"]
        aud = "[2:a]anull[a]"
    fc = (f"[0:v]fps={FPS},scale={W}:{H},setpts=PTS-STARTPTS,{GRADE},{PUNCH},setsar=1[v0];"
          f"[1:v]format=rgba,fade=t=in:st=0.08:d=0.22:alpha=1[tx];"
          f"[v0][tx]overlay=x=0:y='{ty}+28*max(0\\,1-(t-0.08)/0.25)':shortest=1,format=yuv420p[v];{aud}")
    cmd += ["-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-t", f"{dur}",
            "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-r", f"{FPS}",
            "-c:a", "pcm_s16le", "-ar", "48000", seg]
    subprocess.run(cmd, check=True)
    parts.append((seg, dur, bool(ac)))
    print(f"seg {i:2d} {vc} {dur:.2f}s {'voice' if ac else 'broll'}  {title}", flush=True)

json.dump(parts, open(f"{OUT}/parts.json", "w"))
