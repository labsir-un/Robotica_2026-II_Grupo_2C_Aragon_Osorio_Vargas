import re, sys, numpy as np

def q2m(w,x,y,z):
    return np.array([[1-2*(y*y+z*z), 2*(x*y-z*w),   2*(x*z+y*w)],
                     [2*(x*y+z*w),   1-2*(x*x+z*z), 2*(y*z-x*w)],
                     [2*(x*z-y*w),   2*(y*z+x*w),   1-2*(x*x+y*y)]])

n = r'(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)'
txt = open(sys.argv[1], encoding='utf-8', errors='replace').read()
pat = r'(pTCP_Point\d+):=\[\[' + ','.join([n]*3) + r'\],\[' + ','.join([n]*4) + r'\]'
poses = [(m.group(1), np.array([float(m.group(i)) for i in (2,3,4)]),
          q2m(*[float(m.group(i)) for i in (5,6,7,8)])) for m in re.finditer(pat, txt)]
print(f"Puntos de calibracion leidos: {len(poses)}\n")

# Incognitas: p (TCP en coords del flange, 3) y c (punto fijo en el mundo, 3)
# Ecuacion por pose:  t_i + R_i p = c   ->   R_i p - c = -t_i
A = np.zeros((3*len(poses), 6)); b = np.zeros(3*len(poses))
for k,(_,t,R) in enumerate(poses):
    A[3*k:3*k+3, 0:3] = R
    A[3*k:3*k+3, 3:6] = -np.eye(3)
    b[3*k:3*k+3] = -t
sol, *_ = np.linalg.lstsq(A, b, rcond=None)
p, c = sol[:3], sol[3:]

print(f"TCP calculado (coords del flange, tool0): [{p[0]:.3f}, {p[1]:.3f}, {p[2]:.3f}]")
print(f"Punto fijo de referencia en el mundo    : [{c[0]:.2f}, {c[1]:.2f}, {c[2]:.2f}]\n")

print("Error residual por punto (distancia al punto fijo ajustado):")
errs = []
for name, t, R in poses:
    e = np.linalg.norm(t + R @ p - c); errs.append(e)
    print(f"   {name}: {e:7.3f} mm")
print(f"\n   error medio {np.mean(errs):.3f} mm | maximo {np.max(errs):.3f} mm | RMS {np.sqrt(np.mean(np.square(errs))):.3f} mm")

decl = np.array([81.849, -2.987, 164.221])
print(f"\nTool2C declarado en el modulo : [{decl[0]:.3f}, {decl[1]:.3f}, {decl[2]:.3f}]")
d = p - decl
print(f"Diferencia (calculado - decl) : [{d[0]:+.3f}, {d[1]:+.3f}, {d[2]:+.3f}]  -> norma {np.linalg.norm(d):.3f} mm")
print(f"Longitud del TCP: calculado {np.linalg.norm(p):.3f} mm | declarado {np.linalg.norm(decl):.3f} mm")

print("\n--- Condicionamiento de la calibracion ---")
import itertools, math
print("Variacion angular entre las orientaciones usadas:")
for (n1,_,R1),(n2,_,R2) in itertools.combinations(poses,2):
    tr=(np.trace(R1.T@R2)-1)/2
    print(f"   {n1[-6:]} vs {n2[-6:]}: {math.degrees(math.acos(max(-1,min(1,tr)))):5.1f} deg")
print(f"\nNumero de condicion del sistema de minimos cuadrados: {np.linalg.cond(A):.1f}")
