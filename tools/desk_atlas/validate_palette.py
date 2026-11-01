"""Python port of the dataviz skill's validate_palette.js (categorical checks)."""
import math, sys, itertools
BAND = {"light": (0.43, 0.77), "dark": (0.48, 0.67)}
MACHADO = {
 "protan": [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]],
 "deutan": [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]],
 "tritan": [[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]]}
def srgb(h): h=h.strip().lstrip('#'); return [int(h[i:i+2],16)/255 for i in (0,2,4)]
def s2l(c): return c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4
def lin(h): return [s2l(c) for c in srgb(h)]
def rl(h): r,g,b=lin(h); return 0.2126*r+0.7152*g+0.0722*b
def contrast(a,b): x,y=sorted([rl(a),rl(b)],reverse=True); return (x+0.05)/(y+0.05)
def oklab_lin(c):
    r,g,b=c; cb=lambda v: math.copysign(abs(v)**(1/3),v)
    l=cb(0.4122214708*r+0.5363325363*g+0.0514459929*b); m=cb(0.2119034982*r+0.6806995451*g+0.1073969566*b); s=cb(0.0883024619*r+0.2817188376*g+0.6299787005*b)
    return [0.2104542553*l+0.7936177850*m-0.0040720468*s, 1.9779984951*l-2.4285922050*m+0.4505937099*s, 0.0259040371*l+0.7827717662*m-0.8086757660*s]
def oklch(h): L,a,b=oklab_lin(lin(h)); return L, math.hypot(a,b)
def sim(h,k):
    r,g,b=lin(h); M=MACHADO[k]; cl=lambda v:max(0,min(1,v))
    return [cl(M[i][0]*r+M[i][1]*g+M[i][2]*b) for i in range(3)]
def dE(a,b,k=None):
    A=oklab_lin(sim(a,k) if k else lin(a)); B=oklab_lin(sim(b,k) if k else lin(b)); return 100*math.dist(A,B)
def validate(pal, mode, surface, pairs="all"):
    lo,hi=BAND[mode]; ok=True
    print(f"\nPalette {pal} ({mode}, surface {surface})")
    off=[(c,round(oklch(c)[0],3)) for c in pal if not lo<=oklch(c)[0]<=hi]
    print(" Lightness band   ", "FAIL" if off else "PASS", off or "")
    lowc=[(c,round(oklch(c)[1],3)) for c in pal if oklch(c)[1]<0.10]
    print(" Chroma floor     ", "FAIL" if lowc else "PASS", lowc or ""); ok&=not off and not lowc
    pl=list(itertools.combinations(range(len(pal)),2)) if pairs=="all" else [(i,i+1) for i in range(len(pal)-1)]
    w=min(((dE(pal[i],pal[j],k),k,pal[i],pal[j]) for k in ("protan","deutan") for i,j in pl))
    tri=min(dE(pal[i],pal[j],"tritan") for i,j in pl)
    st="PASS" if w[0]>=8 else "WARN" if w[0]>=6 else "FAIL"; ok&=st!="FAIL"
    print(f" CVD separation    {st} worst {w[2]}<->{w[3]} dE {w[0]:.1f} ({w[1]}) tritan {tri:.1f}")
    n=min((dE(pal[i],pal[j]),pal[i],pal[j]) for i,j in pl); ok&=n[0]>=15
    print(f" Normal floor      {'PASS' if n[0]>=15 else 'FAIL'} worst {n[1]}<->{n[2]} dE {n[0]:.1f}")
    low=[(c,round(contrast(c,surface),2)) for c in pal if contrast(c,surface)<3]
    print(" Contrast surface ", "WARN" if low else "PASS", low or "")
    print(" ->", "ALL CHECKS PASS" if ok else "FAILED"); return ok
if __name__=="__main__":
    validate(sys.argv[1].split(","), sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv)>4 else "all")
