"""Continuous-voice edit: voice lines play back-to-back, visuals cut between
synced talking shots and silent B-roll laid over the voice."""
import subprocess, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = os.environ.get("EDIT_WORK", "/tmp/claude-0/-home-user/6eee6c8c-269a-541e-ab77-cbd188a23c83/scratchpad")
RAW, OUT = f"{S}/raw", f"{S}/build3"
os.makedirs(OUT, exist_ok=True)
FONT = f"{S}/fonts/Fredoka.ttf"
W, H, FPS = 1080, 1920, 30
GAP = 0.10  # pause between voice lines


def T(title, sub, y):
    return (title, sub, y)


CONT = "cont"  # keep previous text on screen, no new animation

# Each voice piece: (audio clip, in, out, gap_after, shots)
# shot: (video clip, video in, duration or None = rest of piece, text|CONT|None)
# A shot whose clip == audio clip at the same in-point is lip-synced.
Z = lambda z, cx=0.5, cy=0.5: (z, cx, cy)  # punch-in "angle" on the same footage
GAP = 0.06
PIECES = [
    ("c11", 2.00, 4.55, GAP, [("c02", 0.30, 1.25, T("Stand tablet 7SKIN", "7S-06 Metal Tablet Stand", 1240)),
                              ("c02", 2.60, None, CONT, Z(1.35, 0.5, 0.45))]),
    ("c14", 3.40, 5.55, GAP, [("c14", 3.40, 1.10, T("FULL METAL", "besi solid, bukan plastik", 150)),
                              ("c14", 4.50, None, CONT, Z(1.35, 0.55, 0.62))]),
    ("c05", 9.75, 11.65, GAP, [("c05", 9.75, 0.95, T("Rotate 360°", "tapak pusing ke semua arah", 170)),
                               ("c01", 1.00, None, T("Dual-axis", "tinggi & sudut boleh laras", 170))]),
    ("c14", 15.85, 18.20, GAP, [("c14", 15.85, 1.15, T("Silikon anti-slip", "tablet tak calar, tak tergelincir", 150)),
                                ("c02", 5.30, None, T("Getah di setiap penjuru", "tablet & iPad selamat", 1240))]),
    ("c14", 25.00, 28.10, GAP, [("c12", 38.00, 1.50, T("Stabil", "tak goyang masa guna", 200)),
                                ("c12", 26.00, None, CONT)]),
    ("c13", 20.60, 22.75, GAP, [("c13", 20.60, 1.00, T("Travel friendly", "boleh lipat, muat dalam beg", 150)),
                                ("c03", 0.20, None, CONT)]),
    ("c07", 12.95, 16.05, GAP, [("c09", 9.40, 1.50, T("Harga murah", "kualiti premium", 150)),
                                ("c07", 14.45, None, CONT)]),
    ("c13", 32.45, 35.20, 0.0, [("c13", 32.45, 1.40, T("Highly recommended!", "tekan beg kuning sekarang", 150)),
                                ("c13", 33.85, None, CONT, Z(1.25, 0.5, 0.45))]),
]
if len(sys.argv) > 1:
    PIECES = json.loads(sys.argv[1])  # allow overriding the whole timeline


def text_png(path, title, sub):
    img = Image.new("RGBA", (W, 330), (0, 0, 0, 0))
    def fnt(size, name, txt):
        while True:
            f = ImageFont.truetype(FONT, size); f.set_variation_by_name(name)
            if f.getlength(txt) <= W - 120: return f
            size -= 4
    ft, fs = fnt(92, "Bold", title), fnt(58, "Medium", sub)
    lines = [(title, ft, 30), (sub, fs, 150)]
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(shadow)
    for txt, f, y in lines:
        sd.text(((W - f.getlength(txt)) / 2, y + 4), txt, font=f, fill=(0, 0, 0, 170), stroke_width=6, stroke_fill=(0, 0, 0, 170))
    shadow = shadow.filter(ImageFilter.GaussianBlur(9))
    d = ImageDraw.Draw(img)
    for txt, f, y in lines:
        d.text(((W - f.getlength(txt)) / 2, y), txt, font=f, fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(40, 40, 40, 90))
    out = Image.alpha_composite(shadow, img)
    ImageDraw.Draw(out).rounded_rectangle(((W - 90) / 2, 132, (W + 90) / 2, 140), 4, fill=(255, 140, 0, 255))
    out.save(path)


GRADE = "eq=brightness=0.025:contrast=1.05:saturation=1.08:gamma=1.02,unsharp=5:5:0.45:5:5:0"
PUNCH = f"scale=w='trunc({W}*(1+0.05*max(0\\,1-t/0.3))/2)*2':h=-2:eval=frame,crop={W}:{H}"

shots, audio, pops = [], [], []
t = 0.0
cur_text = None
for pi, (ac, a0, a1, gap, plan) in enumerate(PIECES):
    plen = (a1 - a0) + gap
    audio.append((ac, a0, a1, gap))
    used = 0.0
    for si, sh in enumerate(plan):
        vc, vin, dur, txt = sh[:4]; zm = sh[4] if len(sh) > 4 else None
        d = (plen - used) if dur is None else dur
        anim = txt not in (CONT, None)
        if anim:
            cur_text = txt; pops.append(t + 0.08)
        elif txt is None:
            cur_text = None
        shots.append(dict(vc=vc, vin=vin, dur=d, text=cur_text, anim=anim, zoom=zm))
        used += d; t += d
total = t

parts = []
for i, s in enumerate(shots):
    seg = f"{OUT}/v{i:02d}.mp4"
    cmd = ["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{s['vin']}", "-t", f"{s['dur']+0.1}", "-i", f"{RAW}/{s['vc']}.mov"]
    zf = ""
    if s["zoom"]:
        z, cx, cy = s["zoom"]; zw, zh = int(W * z) // 2 * 2, int(H * z) // 2 * 2
        zf = f"scale={zw}:{zh},crop={W}:{H}:{int((zw-W)*cx)}:{int((zh-H)*cy)},"
    base = f"[0:v]fps={FPS},scale={W}:{H},{zf}setpts=PTS-STARTPTS,{GRADE},{PUNCH},setsar=1[v0]"
    if s["text"]:
        png = f"{OUT}/t{i:02d}.png"; text_png(png, s["text"][0], s["text"][1]); ty = s["text"][2]
        cmd += ["-loop", "1", "-t", f"{s['dur']+0.1}", "-i", png]
        if s["anim"]:
            tx = "[1:v]format=rgba,fade=t=in:st=0.08:d=0.22:alpha=1[tx]"
            yexp = f"'{ty}+28*max(0\\,1-(t-0.08)/0.25)'"
        else:
            tx = "[1:v]format=rgba[tx]"; yexp = f"{ty}"
        fc = f"{base};{tx};[v0][tx]overlay=x=0:y={yexp}:shortest=1,format=yuv420p[v]"
    else:
        fc = f"{base};[v0]format=yuv420p[v]"
    cmd += ["-filter_complex", fc, "-map", "[v]", "-frames:v", str(round(s["dur"] * FPS)),
            "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-r", f"{FPS}", seg]
    subprocess.run(cmd, check=True)
    parts.append(seg)
    print(f"shot {i:2d} {s['vc']} {s['vin']:6.2f} {s['dur']:.2f}s {'*' if s['anim'] else ' '} {s['text'][0] if s['text'] else ''}", flush=True)

open(f"{OUT}/list.txt", "w").write("".join(f"file '{p}'\n" for p in parts))
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{OUT}/list.txt", "-c", "copy", f"{OUT}/video.mp4"], check=True)

# voice track: pieces back-to-back with short gaps, tiny fades to avoid clicks
ins, fc, labels = [], [], []
for k, (ac, a0, a1, gap) in enumerate(audio):
    ins += ["-ss", f"{a0}", "-t", f"{a1-a0}", "-i", f"{RAW}/{ac}.mov"]
    d = a1 - a0
    fc.append(f"[{k}:a]aformat=sample_rates=48000:channel_layouts=stereo,highpass=f=80,"
              f"afade=t=in:d=0.03,afade=t=out:st={d-0.05:.3f}:d=0.05,apad=pad_dur={gap:.3f}[p{k}]")
    labels.append(f"[p{k}]")
fc.append("".join(labels) + f"concat=n={len(labels)}:v=0:a=1[voice]")
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fc), "-map", "[voice]",
                "-c:a", "pcm_s16le", f"{OUT}/voice.wav"], check=True)
json.dump(dict(total=total, pops=pops), open(f"{OUT}/timeline.json", "w"))
print("total", round(total, 2))
