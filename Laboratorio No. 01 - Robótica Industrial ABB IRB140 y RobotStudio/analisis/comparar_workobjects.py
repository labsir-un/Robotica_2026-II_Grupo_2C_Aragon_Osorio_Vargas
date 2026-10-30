import re
def q2m(w,x,y,z):
    return [[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]]
def mul(A,B): return [[sum(A[i][k]*B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def mv(A,v): return [sum(A[i][k]*v[k] for k in range(3)) for i in range(3)]
def ang(R):  # angulo de rotacion total
    import math; t=(R[0][0]+R[1][1]+R[2][2]-1)/2
    return math.degrees(math.acos(max(-1,min(1,t))))

U="../rapid/historico/Module1_wobjA.txt"
F="../rapid/Module1_final.txt"
n=r'(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)'
txtU, txtF = (open(p,encoding='utf-8',errors='replace').read() for p in (U,F))

pts={}
for m in re.finditer(r'(Target_\d+):=\[\['+n+','+n+','+n, txtU):
    pts[m.group(1)]=[float(m.group(i)) for i in (2,3,4)]

frames={}
for name,txt in (("A  (USB, enfrente del robot)",txtU),("B  (final, sobre la banda)",txtF)):
    v=[float(x) for x in re.findall(n, re.search(r'^\s*TASK PERS wobjdata \w+:=\[(.*?)\];',txt,re.M).group(1))]
    ot,orot,ut,urot=v[0:3],v[3:7],v[7:10],v[10:14]
    Ru=q2m(*urot); R=mul(Ru,q2m(*orot))
    o=[ut[i]+mv(Ru,ot)[i] for i in range(3)]
    frames[name]=(R,o)
    W=[[o[i]+mv(R,p)[i] for i in range(3)] for p in pts.values()]
    print(f"{name}")
    print(f"   origen del object frame : [{o[0]:7.1f}, {o[1]:7.1f}, {o[2]:7.1f}]   rotacion total {ang(R):5.1f} deg")
    for i,ax in enumerate("XYZ"):
        print(f"   {ax} de los {len(W)} puntos : {min(w[i] for w in W):7.1f} .. {max(w[i] for w in W):7.1f}")
    print()
RA,_=frames["A  (USB, enfrente del robot)"]; RB,_=frames["B  (final, sobre la banda)"]
Rrel=mul([[RA[j][i] for j in range(3)] for i in range(3)],RB)
print(f"Rotacion relativa entre los dos WorkObjects: {ang(Rrel):.1f} deg")
