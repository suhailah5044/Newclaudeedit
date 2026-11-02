import numpy as np,wave,sys
sr=44100
def save(fn,x):
    x=x/abs(x).max()*.8; w=wave.open(fn,'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((x*32767).astype(np.int16).tobytes())
n=int(.12*sr); t=np.arange(n)/sr; f=900*np.exp(-t*12)+500
save(sys.argv[1]+'/pop.wav', np.sin(2*np.pi*np.cumsum(f)/sr)*np.minimum(1,t/.002)*np.exp(-t/.035))
n=int(.35*sr); t=np.arange(n)/sr; x=np.random.default_rng(1).standard_normal(n)
x=np.convolve(x,np.ones(20)/20,'same'); e=np.sin(np.pi*t/t[-1])**2
save(sys.argv[1]+'/whoosh.wav', x*e)
