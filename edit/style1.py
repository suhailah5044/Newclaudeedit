"""Style-1 (ref: "Outfit of The Day" TikTok): big white script title sitting BEHIND the person.

Pipeline: render base with engine (cuts/B-roll/voice/SFX) -> person mask per frame (rembg
u2net_human_seg, temporally smoothed) -> title layer between background and person.
No colour filter on the footage.
"""
import os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
MW, MH = 384, 683  # mask resolution (upscaled + feathered at composite)


def title_png(path, fonts, big="Bag", small="of", line2="The Day", top=150):
    script, serif = fonts
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fb = ImageFont.truetype(script, 400)
    fs = ImageFont.truetype(serif, 120)
    f2 = ImageFont.truetype(script, 250)
    bw = fb.getlength(big)
    d.text(((W - bw) / 2 - 60, top), big, font=fb, fill=(255, 255, 255, 255))
    d.text((W / 2 + 60, top + 385), small, font=fs, fill=(255, 255, 255, 255))
    lw = f2.getlength(line2)
    d.text(((W - lw) / 2 + 20, top + 470), line2, font=f2, fill=(255, 255, 255, 255))
    a = img.getchannel("A")
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh.putalpha(a.point(lambda v: int(v * 0.35)).filter(ImageFilter.GaussianBlur(7)))
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.alpha_composite(sh, (0, 4)); out.alpha_composite(img)
    out.save(path)


def masks(video, outdir):
    from rembg import new_session, remove
    os.makedirs(outdir, exist_ok=True)
    sess = new_session("u2net_human_seg")
    p = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-i", video, "-vf", f"scale={MW}:{MH}",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    raw = []
    while True:
        b = p.stdout.read(MW * MH * 3)
        if len(b) < MW * MH * 3:
            break
        im = Image.frombytes("RGB", (MW, MH), b)
        raw.append(np.asarray(remove(im, session=sess, only_mask=True), dtype=np.float32))
    p.wait()
    n = len(raw)
    for i in range(n):  # 3-frame temporal average against flicker
        m = (raw[max(0, i - 1)] + 2 * raw[i] + raw[min(n - 1, i + 1)]) / 4
        Image.fromarray(np.clip(m, 0, 255).astype(np.uint8)).save(f"{outdir}/{i:05d}.png")
    return n


def composite(base, maskdir, title, out, fade_in=0.4, crf="16"):
    fc = (f"[2:v]format=rgba,fade=t=in:st=0:d={fade_in}:alpha=1[tt];"
          f"[0:v][tt]overlay=0:0:eof_action=repeat[wt];"
          f"[1:v]scale={W}:{H}:flags=bicubic,gblur=sigma=2,format=gray[m];"
          f"[0:v][m]alphamerge[person];"
          f"[wt][person]overlay=0:0[v]")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", base,
                    "-framerate", f"{FPS}", "-i", f"{maskdir}/%05d.png", "-loop", "1", "-i", title,
                    "-filter_complex", fc, "-map", "[v]", "-map", "0:a", "-shortest",
                    "-c:v", "libx264", "-preset", "medium", "-crf", crf, "-profile:v", "high", "-pix_fmt", "yuv420p",
                    "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
                    "-c:a", "copy", "-movflags", "+faststart", out], check=True)
