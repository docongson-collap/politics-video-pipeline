#!/usr/bin/env python3
"""tile8.py <mp4> <out.png> : 8 evenly spaced frames (4x2, 960x540 each) for eye QC."""
import subprocess, sys
f, o = sys.argv[1], sys.argv[2]
d = float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f]))
ts = [d*(i+0.5)/8 for i in range(8)]
cmd = ["ffmpeg","-v","error","-y"]
for t in ts: cmd += ["-ss",f"{t:.3f}","-i",f]
fc = "".join(f"[{i}:v]scale=960:540,setpts=PTS-STARTPTS[s{i}];" for i in range(8))
fc += "".join(f"[s{i}]" for i in range(8)) + "xstack=inputs=8:layout=" + "|".join(f"{(i%4)*960}_{(i//4)*540}" for i in range(8))
subprocess.run(cmd+["-filter_complex",fc,"-frames:v","1",o],check=True)
print(o, [round(t,2) for t in ts])
