import numpy as np, wave, sys
sr=44100; bpm=118; beat=60/bpm; dur=float(sys.argv[2]); N=int(sr*dur)
L=np.zeros(N); R=np.zeros(N); rng=np.random.default_rng(7)
def add(sig,t,pan=0.0,g=1.0):
    i=int(t*sr); 
    if i>=N: return
    s=sig[:N-i]*g; L[i:i+len(s)]+=s*(1-pan)/1; R[i:i+len(s)]+=s*(1+pan)/1
def env(n,a=0.005,d=0.2):
    t=np.arange(n)/sr; return np.minimum(1,t/a)*np.exp(-t/d)
def kick():
    n=int(.35*sr); t=np.arange(n)/sr; f=50+90*np.exp(-t*30); ph=2*np.pi*np.cumsum(f)/sr
    return np.sin(ph)*env(n,.001,.16)*0.9
def hat(o=False):
    n=int((.18 if o else .05)*sr); x=rng.standard_normal(n); x=x-np.convolve(x,np.ones(4)/4,'same')
    return x*env(n,.001,.06 if o else .015)*0.18
def clap():
    n=int(.25*sr); x=rng.standard_normal(n); x=np.convolve(x,np.ones(3)/3,'same')-np.convolve(x,np.ones(30)/30,'same')
    e=sum(env(n,.001,.012)*(np.arange(n)>=int(k*sr)) for k in (0,.01,.02))*0+env(n,.002,.09)
    return x*e*0.35
def note(f,n,kind='pad'):
    t=np.arange(n)/sr
    if kind=='bass':
        x=np.sin(2*np.pi*f*t)+.3*np.sin(4*np.pi*f*t); return x*env(n,.005,.18)*.38
    x=sum(np.sin(2*np.pi*f*d*t+p) for d,p in ((1,0),(1.004,1),(0.996,2),(2,0.5)))/4
    x=np.convolve(x,np.ones(6)/6,'same'); return x*env(n,.01,.25)*.11
mid=lambda m:440*2**((m-69)/12)
prog=[[57,60,64,67],[53,57,60,64],[48,52,55,60],[55,59,62,67]]  # Am7 Fmaj7 C G
roots=[45,41,48,43]
nb=int(dur/beat)+1
for b in range(nb):
    t=b*beat; bar=b//4; ch=prog[bar%4]
    intro = t<float(sys.argv[3])
    if not intro or b%2==0: add(kick(),t,g=0.75 if intro else 1)
    if not intro and b%4 in (1,3): add(clap(),t,.1)
    add(hat(),t+beat/2,-.3); add(hat(),t+beat/4,.3,.4); add(hat(),t+3*beat/4,.3,.4)
    for k,o in enumerate((0.5,)):  # offbeat chord stabs
        for m in ch: add(note(mid(m),int(.35*sr)),t+beat*o,(k-.5)*.4)
    add(note(mid(roots[bar%4]),int(beat*.45*sr),'bass'),t+beat/2)
    if b%4==0 and not intro: add(note(mid(roots[bar%4]),int(beat*.4*sr),'bass'),t)
# simple stereo reverb-ish
for d,g in ((0.031,.25),(0.047,.2),(0.071,.15)):
    k=int(d*sr); L[k:]+=R[:-k]*g; R[k:]+=L[:-k]*g*.8
fo=int(1.5*sr); fin=int(.3*sr)
for ch in (L,R): ch[:fin]*=np.linspace(0,1,fin); ch[-fo:]*=np.linspace(1,0,fo)
m=max(abs(L).max(),abs(R).max()); st=np.stack([L,R],1)/m*0.89
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((st*32767).astype(np.int16).tobytes())
