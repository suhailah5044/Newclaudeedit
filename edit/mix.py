import json,subprocess,sys
S="/tmp/claude-0/-home-user/6eee6c8c-269a-541e-ab77-cbd188a23c83/scratchpad"
out=sys.argv[1]; vopts=sys.argv[2:]
parts=json.load(open(f"{S}/build/parts.json"))
open(f"{S}/build/list.txt","w").write("".join(f"file '{p}'\n" for p,_,_ in parts))
subprocess.run(["ffmpeg","-nostdin","-v","error","-y","-f","concat","-safe","0","-i",f"{S}/build/list.txt","-c","copy",f"{S}/build/joined.mov"],check=True)
t=0; pops=[]
for p,d,v in parts: pops.append(t+0.08); t+=d
total=t
ins=["-i",f"{S}/build/joined.mov","-i",f"{S}/audio/music.wav"]
fc=["[0:a]asplit=2[voice][key]",
    "[1:a]atrim=0:%.3f,volume=0.30,afade=t=out:st=%.3f:d=1.2[mus]"%(total,total-1.2),
    "[mus][key]sidechaincompress=threshold=0.015:ratio=10:attack=15:release=350:makeup=1[mduck]"]
mix=["[voice]","[mduck]"]
for k,pt in enumerate(pops):
    ins+=["-i",f"{S}/audio/{'pop' if k%2==0 else 'whoosh'}.wav"]
    fc.append(f"[{k+2}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={0.22 if k%2==0 else 0.16},adelay={int(pt*1000)}|{int(pt*1000)}[x{k}]")
    mix.append(f"[x{k}]")
fc.append("".join(mix)+f"amix=inputs={len(mix)}:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
subprocess.run(["ffmpeg","-nostdin","-v","error","-y",*ins,"-filter_complex",";".join(fc),"-map","0:v","-map","[a]",
  *vopts,"-c:a","aac","-b:a","192k","-ar","48000","-movflags","+faststart",out],check=True)
print("total",round(total,2))
