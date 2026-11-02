"""Small TikTok edit engine for the Larissa Kisslock videos.

A spec describes one video:
  voice    : [(src_in, src_out), ...] cut from the talking RAW (hb). Base video = same pieces.
             None for overlay-only videos.
  clips    : [(raw, src_in, dur), ...] base video for overlay-only videos.
  cut      : [(start, end, raw, src_in)] full-frame B-roll pasted over the base (output time).
  stickers : [(start, end, raw, src_t, cx, cy, w, rot, crop)] photo cards that pop in.
             crop = (cx, cy, wfrac) of the source frame, 4:5 crop.
  texts    : [(start, end, text, emoji, y, sfx)] white text, fade + slide-up.
  sfx      : [(t, name, gain)] extra sound effects.

Colours are untouched (no grade / filter); only range-correct scaling to 1080x1920.
"""
import os, subprocess, math, shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "Poppins-SemiBold.ttf")
TEXT_SIZE = 46
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
TEXT_Y = 1400
FULL_RANGE = {"r1", "r2"}  # iPhone clips tagged yuvj420p


def emoji_img(ch, size):
    f = ImageFont.truetype(EMOJI, 109)
    im = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 0), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox())
    return im.resize((max(1, int(im.width * size / im.height)), size), Image.LANCZOS)


def text_png(path, txt, emo):
    size = TEXT_SIZE
    f = ImageFont.truetype(FONT, size)
    while f.getlength(txt) > W - 200:
        size -= 2; f = ImageFont.truetype(FONT, size)
    e = emoji_img(emo, int(size * 1.05)) if emo else None
    gap = 12 if e else 0
    tw = f.getlength(txt) + gap + (e.width if e else 0)
    img = Image.new("RGBA", (W, 200), (0, 0, 0, 0))
    x0, y0 = (W - tw) / 2, 50
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((x0, y0 + 3), txt, font=f, fill=(0, 0, 0, 150), stroke_width=3, stroke_fill=(0, 0, 0, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(6))
    ImageDraw.Draw(img).text((x0, y0), txt, font=f, fill=(255, 255, 255, 255))
    out = Image.alpha_composite(sh, img)
    if e:
        bb = f.getbbox(txt)
        out.alpha_composite(e, (int(x0 + f.getlength(txt) + gap), int(y0 + (bb[1] + bb[3]) / 2 - e.height / 2)))
    out.save(path)


def grab(raw_path, t, out):
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{t}", "-i", raw_path,
                    "-frames:v", "1", "-q:v", "1", out], check=True)


POP = [0.25, 0.55, 0.85, 1.08, 1.05, 1.0]
OUTF = [1.0, 0.92, 0.8, 0.65]


def sticker_frames(dirp, still, w, rot, crop, dur):
    """Polaroid-style photo card: white border, rounded corners, soft shadow, pop in / out."""
    os.makedirs(dirp, exist_ok=True)
    src = Image.open(still).convert("RGB")
    cx, cy, wf = crop
    cw = src.width * wf; ch = cw * 5 / 4
    l = max(0, min(src.width - cw, cx * src.width - cw / 2)); t = max(0, min(src.height - ch, cy * src.height - ch / 2))
    ph = src.crop((int(l), int(t), int(l + cw), int(t + ch)))
    b = int(w * 0.045)
    ph = ph.resize((w - 2 * b, int((w - 2 * b) * 5 / 4)), Image.LANCZOS)
    card = Image.new("RGBA", (w, ph.height + 2 * b), (0, 0, 0, 0))
    m = Image.new("L", card.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, *card.size), int(w * 0.04), fill=255)
    card.paste((255, 255, 255, 255), (0, 0), m)
    pm = Image.new("L", ph.size, 0); ImageDraw.Draw(pm).rounded_rectangle((0, 0, *ph.size), int(w * 0.025), fill=255)
    card.paste(ph, (b, b), pm)
    S = int(math.hypot(*card.size) * 1.2) // 2 * 2
    pad = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    sh = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ox, oy = (S - card.width) // 2, (S - card.height) // 2
    shm = Image.new("L", card.size, 0); ImageDraw.Draw(shm).rounded_rectangle((0, 0, *card.size), int(w * 0.04), fill=110)
    sh.paste((0, 0, 0, 255), (ox + 6, oy + 14), shm)
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    pad.alpha_composite(sh); pad.alpha_composite(card, (ox, oy))
    base = pad.rotate(rot, resample=Image.BICUBIC)
    n = int(round(dur * FPS))
    for i in range(n):
        if i < len(POP):
            s, a = POP[i], min(1, (i + 1) / 3)
        elif i >= n - len(OUTF):
            k = i - (n - len(OUTF)); s, a = OUTF[k], 1 - k / len(OUTF)
        else:
            s, a = 1.0, 1.0
        fr = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        im = base.resize((max(2, int(S * s)), max(2, int(S * s))), Image.BILINEAR)
        if a < 1:
            im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
        fr.alpha_composite(im, ((S - im.width) // 2, (S - im.height) // 2))
        fr.save(f"{dirp}/{i:04d}.png", compress_level=1)
    return S


def vscale(raw):
    rng = "pc" if raw in FULL_RANGE else "tv"
    return f"scale={W}:{H}:in_range={rng}:out_range=tv:flags=lanczos,fps={FPS},setsar=1,format=yuv420p"


def render(spec, raws, sfxdir, work, out, crf="16"):
    shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
    ins, fc = [], []

    def add(*a):
        ins.extend(a); return sum(1 for x in ins if x == "-i") - 1

    voice = spec.get("voice")
    if voice:
        pieces = [("hb", a, b - a) for a, b in voice]
    else:
        pieces = spec["clips"]
    total = sum(d for _, _, d in pieces)
    # base video (+ voice)
    for k, (raw, s, d) in enumerate(pieces):
        i = add("-ss", f"{s}", "-t", f"{d}", "-i", raws[raw])
        fc.append(f"[{i}:v]{vscale(raw)},trim=duration={d},setpts=PTS-STARTPTS[bv{k}]")
        if voice:
            fc.append(f"[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=duration={d},asetpts=PTS-STARTPTS,"
                      f"afade=t=in:d=0.015,afade=t=out:st={d-0.03:.3f}:d=0.03[ba{k}]")
    n = len(pieces)
    fc.append("".join(f"[bv{k}]" for k in range(n)) + f"concat=n={n}:v=1:a=0[v0]")
    if voice:
        fc.append("".join(f"[ba{k}]" for k in range(n)) + f"concat=n={n}:v=0:a=1,loudnorm=I=-15:TP=-2:LRA=9[voice]")
    last = "v0"; lk = 0
    sfx = list(spec.get("sfx", []))
    if not voice:  # whoosh on every hard cut of overlay videos
        t = 0
        for _, _, d in pieces[:-1]:
            t += d; sfx.append((t - 0.18, "whoosh", 0.35))

    def ov(src, x="0", y="0", st=0, en=None):
        nonlocal last, lk
        en = total if en is None else en
        fc.append(f"[{last}][{src}]overlay=x={x}:y={y}:eof_action=pass:eval=frame:enable='between(t,{st},{en})'[o{lk}]")
        last = f"o{lk}"; lk += 1

    for k, (st, en, raw, s) in enumerate(spec.get("cut", [])):
        i = add("-ss", f"{s}", "-t", f"{en-st}", "-i", raws[raw])
        fc.append(f"[{i}:v]{vscale(raw)},setpts=PTS-STARTPTS+{st}/TB[c{k}]")
        ov(f"c{k}", st=st, en=en)
        sfx.append((st - 0.15, "whoosh", 0.25 if voice else 0.35))
    for k, (st, en, raw, s, cx, cy, w, rot, crop) in enumerate(spec.get("stickers", [])):
        still = f"{work}/still{k}.jpg"; grab(raws[raw], s, still)
        S = sticker_frames(f"{work}/st{k}", still, w, rot, crop, en - st)
        i = add("-framerate", f"{FPS}", "-i", f"{work}/st{k}/%04d.png")
        fc.append(f"[{i}:v]format=rgba,setpts=PTS-STARTPTS+{st}/TB[s{k}]")
        ov(f"s{k}", x=f"{int(cx - S/2)}", y=f"{int(cy - S/2)}", st=st, en=en)
        sfx.append((st, "pop", 0.3)); sfx.append((st + 0.02, "shutter", 0.18))
    for k, (st, en, txt, emo, y, tsfx) in enumerate(spec.get("texts", [])):
        png = f"{work}/txt{k}.png"; text_png(png, txt, emo)
        d = en - st
        i = add("-loop", "1", "-t", f"{d}", "-i", png)
        fc.append(f"[{i}:v]format=rgba,fade=t=in:st=0:d=0.3:alpha=1,fade=t=out:st={d-0.25:.2f}:d=0.25:alpha=1,"
                  f"setpts=PTS+{st}/TB[t{k}]")
        ov(f"t{k}", y=f"'{y}+28*max(0,1-(t-{st})/0.35)'", st=st, en=en)
        if tsfx:
            sfx.append((st, tsfx, {"sparkle": 0.3, "ding": 0.3}.get(tsfx, 0.3)))
        else:
            sfx.append((st, "tick", 0.15))
    # audio: voice (if any) + sfx, no music
    mix = ["[voice]"] if voice else []
    if not voice:
        i = add("-f", "lavfi", "-t", f"{total}", "-i", "anullsrc=r=48000:cl=stereo")
        mix.append(f"[{i}:a]")
    for k, (t, name, g) in enumerate(sorted(sfx)):
        t = max(0.0, t)
        if t >= total - 0.05:
            continue
        i = add("-i", f"{sfxdir}/{name}.wav")
        ms = int(t * 1000)
        fc.append(f"[{i}:a]volume={g},adelay={ms}|{ms}[x{k}]"); mix.append(f"[x{k}]")
    fc.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=first,atrim=0:{total:.3f},"
              "alimiter=limit=0.9:level=false[aout]")
    cmd = ["ffmpeg", "-nostdin", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fc),
           "-map", f"[{last}]", "-map", "[aout]", "-t", f"{total:.3f}",
           "-c:v", "libx264", "-preset", "medium", "-crf", crf, "-profile:v", "high", "-pix_fmt", "yuv420p",
           "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    return total
