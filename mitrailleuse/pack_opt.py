import math, random, sys, json
def relax(n,Rc,iters=3000):
    pts=[]
    while len(pts)<n:
        x,y=random.uniform(-Rc,Rc),random.uniform(-Rc,Rc)
        if x*x+y*y<=Rc*Rc: pts.append([x,y])
    step=0.1
    for it in range(iters):
        f=[[0,0] for _ in pts]; e=0
        for i in range(n):
            for j in range(i+1,n):
                dx=pts[i][0]-pts[j][0];dy=pts[i][1]-pts[j][1];d=math.hypot(dx,dy)
                if d<1:
                    d=max(d,1e-9);o=1-d;e+=o*o
                    f[i][0]+=dx/d*o;f[i][1]+=dy/d*o;f[j][0]-=dx/d*o;f[j][1]-=dy/d*o
            r=math.hypot(*pts[i])
            if r>Rc:
                o=r-Rc;e+=o*o;f[i][0]-=pts[i][0]/r*o;f[i][1]-=pts[i][1]/r*o
        for p,g in zip(pts,f): p[0]+=g[0]*0.5;p[1]+=g[1]*0.5
        if e<1e-12: return pts
    return None
def best(n,lo,hi,tries):
    bestp=None
    for _ in range(tries):
        # shrink from hi
        R=hi
        while R>lo:
            p=None
            for _ in range(3):
                p=relax(n,R)
                if p: break
            if p: bestp=(R,p);hi=R;R-=0.01
            else: break
    return bestp
random.seed(1)
res={}
for n,lo,hi in [(19,1.8,2.2),(24,2.3,2.8),(25,2.35,2.9)]:
    b=best(n,lo,hi,4)
    print(n,"Rc=%.3f p"%b[0],"Ø=%.0f"%(2*b[0]*40+38),flush=True)
    res[n]=b
json.dump({k:v for k,v in res.items()},open("opt.json","w"))
