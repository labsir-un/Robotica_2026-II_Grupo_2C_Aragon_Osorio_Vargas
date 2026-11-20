from robodk.robolink import *
from robodk.robomath import *

from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties

import math



# ==========================================
# 1. CONEXIÓN CON EL MOTOMAN FÍSICO
# ==========================================

RDK = Robolink()

robot = RDK.ItemUserPick(
    "Selecciona un robot",
    ITEM_TYPE_ROBOT
)

if not robot.Valid():
    raise Exception("Robot no válido")

# Conectar al controlador físico
robot.Connect()

# Comprobar estado de conexión
estado, mensaje = robot.ConnectedState()

if estado != ROBOTCOM_READY:
    raise Exception(        "Robot no preparado: " + mensaje    )

print("Motoman conectado correctamente")

# Habilitar ejecución en el robot físico
RDK.setRunMode(RUNMODE_RUN_ROBOT)

print("Modo ejecución física activado")


##___________________________________________________________________




T_H = RDK.Item("Target_Home", ITEM_TYPE_TARGET)
frame = RDK.Item("Frame_from_Target1", ITEM_TYPE_FRAME)

if not T_H.Valid():
    raise Exception("No se encontró Target_Home")

if not frame.Valid():
    raise Exception("No se encontró el Frame")

robot.setPoseFrame(frame)
robot.setSpeed(50)
robot.setRounding(0)


# ==========================================
# 2. PARÁMETROS GENERALES
# ==========================================

A = 50
num_points = 120

z_surface = 0
z_safe = 50

alto_letra = 30
ancho_max = 140

# Rotación de toda la trayectoria
ANGULO_DIBUJO = -90

OFFSET_X = 100
OFFSET_Y = 0

# Espejo aplicado SOLO a las letras
ESPEJO_LETRAS = True


# ==========================================
# 3. TRANSFORMACIÓN DE COORDENADAS
# ==========================================

def pose_dibujo(x, y, z):

    angulo = math.radians(ANGULO_DIBUJO)

    x_rot = (
        x * math.cos(angulo)
        - y * math.sin(angulo)
    )

    y_rot = (
        x * math.sin(angulo)
        + y * math.cos(angulo)
    )

    x_rot += OFFSET_X
    y_rot += OFFSET_Y

    return transl(x_rot, y_rot, z)


# ==========================================
# 4. FUNCIÓN PARA DIBUJAR TEXTO
# ==========================================

def dibujar_texto(texto, y_base, alto_mm=30):

    fuente = FontProperties(family="DejaVu Sans")

    path = TextPath(
        (0, 0),
        texto,
        size=20,
        prop=fuente
    )

    caja = path.get_extents()

    if caja.width <= 0 or caja.height <= 0:
        return

    escala = min(
        alto_mm / caja.height,
        ancho_max / caja.width
    )

    contornos = path.to_polygons(
        closed_only=False
    )

    cantidad = sum(len(c) for c in contornos)
    print(f"{texto}: {cantidad} puntos")

    for contorno in contornos:

        if len(contorno) < 2:
            continue

        # Coordenadas locales centradas del texto
        puntos = []

        for punto in contorno:

            x = (
                punto[0] - caja.x0
                - caja.width / 2
            ) * escala

            y = y_base + (
                punto[1] - caja.y0
            ) * escala

            # ESPEJO SOLO PARA LAS LETRAS
            if ESPEJO_LETRAS:
                x = -x

            puntos.append((x, y))

        # Primer punto del contorno
        x0, y0 = puntos[0]

        # Acercamiento
        robot.MoveL(
            pose_dibujo(x0, y0, z_safe)
        )

        # Bajar herramienta
        robot.MoveL(
            pose_dibujo(x0, y0, z_surface)
        )

        # Dibujar letra
        for x, y in puntos[1:]:
            robot.MoveL(
                pose_dibujo(x, y, z_surface)
            )

        # Levantar herramienta
        robot.MoveL(
            pose_dibujo(x, y, z_safe)
        )


# ==========================================
# 5. ESPIRAL DE ARQUÍMEDES (POLAR)
# ==========================================

def punto_espiral(theta):

    # Dos vueltas: 0 <= theta <= 4*pi
    r = A * theta / (4 * math.pi)

    # Conversión polar a cartesiana
    x = r * math.cos(theta)
    y = r * math.sin(theta)

    return x, y


# ==========================================
# 6. IR A HOME
# ==========================================

print("Moviendo a Home...")
robot.MoveJ(T_H)


# ==========================================
# 7. DIBUJAR ESPIRAL
# ==========================================

print("Dibujando espiral polar...")

x0, y0 = punto_espiral(0)

# Aproximación
robot.MoveJ(
    pose_dibujo(x0, y0, z_safe)
)

# Bajar al plano
robot.MoveL(
    pose_dibujo(x0, y0, z_surface)
)

# Recorrer la espiral
for i in range(1, num_points + 1):

    theta = 4 * math.pi * i / num_points

    x, y = punto_espiral(theta)

    robot.MoveL(
        pose_dibujo(x, y, z_surface)
    )

# Levantar herramienta
robot.MoveL(
    pose_dibujo(x, y, z_safe)
)

print("Espiral completada")


# ==========================================
# 8. DIBUJAR NOMBRES
# ==========================================

nombre1 = "JHON"
nombre2 = "FELIPE"
nombre3 = "JESUS"

dibujar_texto(
    nombre1,
    y_base=-A-45,
    alto_mm=alto_letra
)

dibujar_texto(
    nombre2,
    y_base=-A-85,
    alto_mm=alto_letra
)

dibujar_texto(
    nombre3,
    y_base=-A-125,
    alto_mm=alto_letra
)

print("Nombres completados")


# ==========================================
# 9. REGRESAR A HOME
# ==========================================

robot.MoveJ(T_H)

print("Programa finalizado")
