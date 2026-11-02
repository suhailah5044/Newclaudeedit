"""Mix continuous voice + ducked music + SFX onto the rendered video."""
import json, subprocess, sys, os
S = os.environ.get("EDIT_WORK", "/tmp/claude-0/-home-user/6eee6c8c-269a-541e-ab77-cbd188a23c83/scratchpad")
B = f"{S}/build3"
out, vopts = sys.argv[1], sys.argv[2:]
tl = json.load(open(f"{B}/timeline.json")); total = tl["total"]
ins = ["-i", f"{B}/video.mp4", "-i", f"{B}/voice.wav", "-i", f"{S}/audio/music.wav"]
fc = ["[1:a]asplit=2[voice][key]",
      f"[2:a]atrim=0:{total:.3f},volume=0.30,afade=t=out:st={total-1.2:.3f}:d=1.2[mus]",
      "[mus][key]sidechaincompress=threshold=0.015:ratio=10:attack=15:release=350:makeup=1[mduck]"]
mix = ["[voice]", "[mduck]"]
for k, pt in enumerate(tl["pops"]):
    ins += ["-i", f"{S}/audio/{'pop' if k % 2 == 0 else 'whoosh'}.wav"]
    ms = int(pt * 1000)
    fc.append(f"[{k+3}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={0.22 if k % 2 == 0 else 0.16},adelay={ms}|{ms}[x{k}]")
    mix.append(f"[x{k}]")
fc.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=first,atrim=0:{total:.3f},loudnorm=I=-14:TP=-1.5:LRA=11[a]")
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fc), "-map", "0:v", "-map", "[a]",
                *vopts, "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", out], check=True)
print("done", out, round(total, 2))
