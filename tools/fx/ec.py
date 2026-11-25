"""EffectCraft helpers (lock-aware). import ec; ec.frames(proj, [(comp,t,out)...]); ec.render(...)"""
import subprocess, os, time, re
EC="/Volumes/WORK/Auto Film Factory/tools/effectcraft/target/release/effectcraft-cli"
LOCK="/Volumes/WORK/Auto Film Factory/Politics/tools/fx/.eclock"
import signal
class Lock:
    def __init__(self, full=False): self.full=full
    def __enter__(self):
        signal.signal(signal.SIGTERM, lambda *a: (_ for _ in ()).throw(KeyboardInterrupt()))
        while self.full and float(re.search(r"averages?: ([\d.]+)",subprocess.run(["uptime"],capture_output=True,text=True).stdout).group(1))>12: time.sleep(20)
        while True:
            try: os.mkdir(LOCK); break
            except FileExistsError: time.sleep(15)
        if self.full:
            while subprocess.run(["pgrep","-f","effectcraft-cli.* render "],capture_output=True).stdout.strip(): time.sleep(15)
    def __exit__(self,*a):
        try: os.rmdir(LOCK)
        except OSError: pass
def frames(proj, items, ms=640, half=False):
    with Lock():
        for comp,t,out in items:
            r=subprocess.run(["nice","-n","10",EC,"--project",proj,"render-frame","--comp",comp,"--time",str(t),*(["--scale","0.5"] if half else ["--max-side",str(ms)]),"--out",out],capture_output=True,text=True)
            if r.returncode: print("ERR",comp,t,r.stderr[-200:])
def render(proj, comp, out, half=False):
    with Lock(full=True):
        r=subprocess.run(["nice","-n","10",EC,"--project",proj,"render","--comp",comp,"--out",out,"--format","h264","--audio","off"]+(["--resolution","half"] if half else []),capture_output=True,text=True)
        print(r.stdout[-300:], r.stderr[-300:])
def tile(out, files, cols=3, w=640, h=360):
    n=len(files); lay="|".join(f"{(i%cols)*w}_{(i//cols)*h}" for i in range(n))
    cmd=["ffmpeg","-y","-loglevel","error"]
    for f in files: cmd+=["-i",f]
    cmd+=["-filter_complex",f"xstack=inputs={n}:layout={lay}",out]; subprocess.run(cmd)
