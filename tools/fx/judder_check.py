import sys,subprocess,numpy as np
f=sys.argv[1]; W,H=480,270
b=subprocess.run(["ffmpeg","-v","error","-i",f,"-vf",f"scale={W}:{H},format=gray","-f","rawvideo","-"],capture_output=True).stdout
F=np.frombuffer(b,np.uint8).reshape(-1,H,W).astype(np.float32)
# global motion via phase correlation on center crop -> per-frame shift magnitude
def shift(a,b):
    A=np.fft.fft2(a);B=np.fft.fft2(b);R=A*np.conj(B);R/=np.abs(R)+1e-6;r=np.abs(np.fft.ifft2(R));y,x=np.unravel_index(r.argmax(),r.shape)
    if y>H//2:y-=H
    if x>W//2:x-=W
    return np.hypot(x,y)
fps=float(eval(subprocess.run(["ffprobe","-v","error","-select_streams","v","-show_entries","stream=r_frame_rate","-of","csv=p=0",f],capture_output=True,text=True).stdout.strip()))
m=[shift(F[i],F[i-1]) for i in range(1,len(F))]
d=[float(np.abs(F[i]-F[i-1]).mean()) for i in range(1,len(F))]
bad=[]
for i in range(1,len(d)-1):
    if d[i-1]>3 and d[i+1]>3 and d[i]<0.35*min(d[i-1],d[i+1]): bad.append(round((i+1)/fps,2))
print(f, "fps",round(fps,2),"frames",len(F),"stutter frames (held mid-motion):",len(bad), bad[:40])
