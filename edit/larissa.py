"""Larissa Kisslock Bag - 15s TikTok preview.

Clean cut, original colours (no filter), original audio, no music.
White bold overlay text, simple fade + slide-up animation.

usage: python3 larissa.py RAW.mov WORKDIR OUT.mp4 [crf]
"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

RAW, WORK, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
CRF = sys.argv[4] if len(sys.argv) > 4 else "18"
os.makedirs(WORK, exist_ok=True)
W, H = 1080, 1920
FONT = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
TEXT_Y = 1400  # lower third: clear of face and above TikTok caption area

# source clips: (src_in, duration)
CLIPS = [
    (0.0, 3.0),   # hook: bag pushed to camera
    (6.5, 2.0),   # bag presented close - shape / design
    (14.0, 3.0),  # gold kisslock clasp close-up, then opening it
    (22.0, 1.5),  # hand carry by the handle
    (31.0, 1.5),  # chain over shoulder - sling
    (34.0, 2.0),  # full outfit look
    (40.5, 2.0),  # bag to camera - outro
]
TOP_Y = 200  # used when the bag fills the lower frame
# overlays: (start, end, text, emoji, y)
TEXTS = [
    (0.0, 3.0, "KISSLOCK BAG IS BACK!", "\U0001F90E", TEXT_Y),
    (3.0, 5.0, "Vintage & classy design", None, TEXT_Y),
    (5.0, 8.0, "Elegant gold kisslock detail", None, TOP_Y),
    (8.0, 11.0, "Hand carry + sling style", None, TEXT_Y),
    (11.0, 13.0, "Perfect for Raya & daily wear", None, TEXT_Y),
    (13.0, 15.0, "BACK IN STOCK!", "\U0001F6CD️", TEXT_Y),
]


def emoji_img(ch, size):
    f = ImageFont.truetype(EMOJI, 109)
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 0), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox())
    return im.resize((int(im.width * size / im.height), size), Image.LANCZOS)


def text_png(path, txt, emo):
    size = 64
    f = ImageFont.truetype(FONT, size)
    while f.getlength(txt) > W - 200:
        size -= 2; f = ImageFont.truetype(FONT, size)
    e = emoji_img(emo, int(size * 1.05)) if emo else None
    gap = 18 if e else 0
    tw = f.getlength(txt) + gap + (e.width if e else 0)
    img = Image.new("RGBA", (W, 200), (0, 0, 0, 0))
    x0, y0 = (W - tw) / 2, 50
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((x0, y0 + 3), txt, font=f, fill=(0, 0, 0, 150), stroke_width=4, stroke_fill=(0, 0, 0, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(8))
    d = ImageDraw.Draw(img)
    d.text((x0, y0), txt, font=f, fill=(255, 255, 255, 255))
    out = Image.alpha_composite(sh, img)
    if e:
        bb = f.getbbox(txt)
        ey = int(y0 + (bb[1] + bb[3]) / 2 - e.height / 2)
        out.alpha_composite(e, (int(x0 + f.getlength(txt) + gap), ey))
    out.save(path)


cmd = ["ffmpeg", "-nostdin", "-v", "error", "-y"]
for s, d in CLIPS:
    cmd += ["-ss", f"{s}", "-t", f"{d}", "-i", RAW]
n = len(CLIPS)
fc = []
for i, (s, d) in enumerate(CLIPS):
    fc.append(f"[{i}:v]scale={W}:{H},fps=30,setsar=1,setpts=PTS-STARTPTS[v{i}]")
    fc.append(f"[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS,"
              f"afade=t=in:d=0.03,afade=t=out:st={d-0.04:.3f}:d=0.04[a{i}]")
fc.append("".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[vb][ab]")
last = "vb"
for k, (st, en, txt, emo, ty) in enumerate(TEXTS):
    png = f"{WORK}/txt{k}.png"; text_png(png, txt, emo)
    dur = en - st
    cmd += ["-loop", "1", "-t", f"{dur}", "-i", png]
    idx = n + k
    fc.append(f"[{idx}:v]format=rgba,fade=t=in:st=0:d=0.3:alpha=1,"
              f"fade=t=out:st={dur-0.25:.2f}:d=0.25:alpha=1,setpts=PTS+{st}/TB[t{k}]")
    fc.append(f"[{last}][t{k}]overlay=x=0:y='{ty}+28*max(0,1-(t-{st})/0.35)':eval=frame:"
              f"enable='between(t,{st},{en})'[o{k}]")
    last = f"o{k}"
fc.append("[ab]loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
cmd += ["-filter_complex", ";".join(fc), "-map", f"[{last}]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "slow", "-crf", CRF, "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", "15", "-movflags", "+faststart", OUT]
subprocess.run(cmd, check=True)
print("done", OUT)
