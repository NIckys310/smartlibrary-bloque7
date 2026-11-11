"""Entregable 4: diagrama de secuencia de POST /api/prestamos (estilo Visual Paradigm)."""
import sys
from html import escape

FONT = "Arial, Helvetica, sans-serif"
FILL_TOP, FILL_BOT, STROKE = "#FFFFF4", "#FFFFC4", "#A0522D"
EDGE = "#404040"
ACT_FILL = "#FFFFFF"

participantes = [
    ("usuario", "Usuario", "actor"),
    ("ctrl", ":PrestamoController", "box"),
    ("svc", ":PrestamoService", "box"),
    ("rest", ":EstudianteRepository", "box"),
    ("rlib", ":LibroRepository", "box"),
    ("libro", "libro : Libro", "box"),
    ("rpre", ":PrestamoRepository", "box"),
]
SP = 190
X = {k: 90 + i * SP for i, (k, _, _) in enumerate(participantes)}
HEAD_Y, HEAD_H = 40, 40

out = []
y = HEAD_Y + HEAD_H + 40
acts = []          # (participante, y_ini, y_fin, nivel)
abiertas = {}


def T(x, y, t, anchor="middle", size=11, bold=False, italic=False, fill="#000"):
    st = ";".join(s for s in ("font-weight:bold" if bold else "", "font-style:italic" if italic else "") if s)
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-family="{FONT}" font-size="{size}" '
            f'fill="{fill}" style="{st}">{escape(t)}</text>')


def act_x(p, lado):
    n = abiertas.get(p, [])
    off = 5 * max(len(n), 1)
    return X[p] + (off if lado > 0 else -off)


def abrir(p, y0):
    abiertas.setdefault(p, []).append(y0)


def cerrar(p, y1):
    y0 = abiertas[p].pop()
    acts.append((p, y0, y1, len(abiertas[p])))


def msg(a, b, texto, y, ret=False, n=None):
    xa = X[a] + (5 if X[b] > X[a] else -5) if a in abiertas and abiertas[a] else X[a]
    xb = X[b] + (-5 if X[b] > X[a] else 5)
    if ret:
        xa = X[a] + (-5 if X[b] < X[a] else 5)
        xb = X[b] + (5 if X[b] < X[a] else -5)
    dash = ' stroke-dasharray="6,4"' if ret else ""
    out.append(f'<line x1="{xa:.1f}" y1="{y}" x2="{xb:.1f}" y2="{y}" stroke="{EDGE}"{dash}/>')
    d = 1 if xb > xa else -1
    if ret:
        out.append(f'<polyline points="{xb-d*10:.1f},{y-5} {xb:.1f},{y} {xb-d*10:.1f},{y+5}" fill="none" stroke="{EDGE}"/>')
    else:
        out.append(f'<polygon points="{xb-d*10:.1f},{y-5} {xb:.1f},{y} {xb-d*10:.1f},{y+5}" fill="{EDGE}"/>')
    etiqueta = f"{n}: {texto}" if n else texto
    out.append(T(min(xa, xb) + 14, y - 6, etiqueta, anchor="start"))


def self_msg(p, texto, y, n):
    x0 = X[p] + 5
    out.append(f'<polyline points="{x0},{y} {x0+40},{y} {x0+40},{y+22} {x0+10},{y+22}" fill="none" stroke="{EDGE}"/>')
    out.append(f'<polygon points="{x0+20},{y+17} {x0+10},{y+22} {x0+20},{y+27}" fill="{EDGE}"/>')
    out.append(T(x0 + 46, y + 4, f"{n}: {texto}", anchor="start"))


def fragment(x0, y0, x1, y1, op, guardias):
    """guardias: [(y_separador o None, texto)]"""
    frag = [f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="none" stroke="#5B5B5B"/>',
            f'<path d="M{x0},{y0+18} L{x0+40},{y0+18} L{x0+48},{y0+10} L{x0+48},{y0}" fill="#F2F2F2" stroke="#5B5B5B"/>',
            T(x0 + 22, y0 + 13, op, bold=True)]
    for ysep, g in guardias:
        if ysep is not None:
            frag.append(f'<line x1="{x0}" y1="{ysep}" x2="{x1}" y2="{ysep}" stroke="#5B5B5B" stroke-dasharray="5,4"/>')
        frag.append(T(x0 + 56 if ysep is None else x0 + 10, (ysep if ysep is not None else y0) + 14, g,
                      anchor="start", bold=True))
    return frag


ST = 34  # espacio entre mensajes
n = 0


def nx():
    global n
    n += 1
    return n


# ---------------- Mensajes ----------------
abrir("usuario", y - 10)
msg("usuario", "ctrl", 'POST /api/prestamos {estudianteId, libroId}', y, n=nx()); abrir("ctrl", y)
y += ST
out.append(T(X["ctrl"] + 10, y - 8, "@Valid PrestamoRequest (400 si es inválido)", anchor="start", size=10, fill="#555"))
y += 10
msg("ctrl", "svc", "registrarPrestamo(request)", y, n=nx()); abrir("svc", y)
y += ST
msg("svc", "rest", "findById(estudianteId)", y, n=nx()); abrir("rest", y)
y += ST
msg("rest", "svc", "Optional<Estudiante>", y, ret=True); cerrar("rest", y)
y += ST
msg("svc", "rlib", "findById(libroId)", y, n=nx()); abrir("rlib", y)
y += ST
msg("rlib", "svc", "Optional<Libro>", y, ret=True); cerrar("rlib", y)
y += ST
msg("svc", "rpre", "existsByLibroIdAndFechaDevolucionIsNull(libroId)", y, n=nx()); abrir("rpre", y)
y += ST
msg("rpre", "svc", "activo : boolean", y, ret=True); cerrar("rpre", y)
y += ST

frag_y0 = y - 6
y += 30
alt1_y = y - 30
msg("svc", "libro", "marcarPrestado()", y, n=nx()); abrir("libro", y)
y += 26
out.append(T(X["libro"] + 10, y - 6, "disponible = false  (R3)", anchor="start", size=10, fill="#555"))
y += 8
cerrar("libro", y)
y += ST - 6
msg("svc", "rpre", "save(new Prestamo(estudiante, libro, hoy))", y, n=nx()); abrir("rpre", y)
y += ST
msg("rpre", "svc", "prestamo : Prestamo", y, ret=True); cerrar("rpre", y)
y += ST
msg("svc", "ctrl", "PrestamoResponse", y, ret=True)
y += ST
msg("ctrl", "usuario", "201 Created + Location + PrestamoResponse", y, ret=True)
y += 26
sep_y = y
y += 34
msg("svc", "svc", "", y) if False else None
self_msg("svc", "throw LibroNoDisponibleException", y, nx())
y += 44
msg("svc", "ctrl", "LibroNoDisponibleException  (rollback)", y, ret=True)
y += ST
msg("ctrl", "usuario", "409 Conflict (ProblemDetail)  — sin nuevo préstamo", y, ret=True)
y += 22
frag_y1 = y
x_f0, x_f1 = X["usuario"] - 60, X["rpre"] + 120
out[:0] = fragment(x_f0, frag_y0, x_f1, frag_y1, "alt",
                   [(None, "[ !activo && libro.isDisponible() ]  préstamo exitoso"),
                    (sep_y, "[ else ]  libro no disponible (R1, R5)")])
y += 20
cerrar("svc", frag_y1 - 30)
cerrar("ctrl", frag_y1 - 10)
cerrar("usuario", frag_y1 - 4)
y_fin = y + 70

# Nota sobre 404
nota = [
    "Si findById devuelve Optional vacío, el Service lanza",
    "RecursoNoEncontradoException y ManejadorErrores responde",
    "404 Not Found (estudiante o libro inexistente).",
]
nx0, ny0 = X["rlib"] - 20, y_fin - 60
nw, nh = 340, len(nota) * 15 + 14
nota_svg = [f'<path d="M{nx0},{ny0} L{nx0+nw-12},{ny0} L{nx0+nw},{ny0+12} L{nx0+nw},{ny0+nh} L{nx0},{ny0+nh} Z" fill="#FFFFFF" stroke="#7F7F7F"/>',
            f'<path d="M{nx0+nw-12},{ny0} L{nx0+nw-12},{ny0+12} L{nx0+nw},{ny0+12}" fill="none" stroke="#7F7F7F"/>']
nota_svg += [T(nx0 + 10, ny0 + 19 + i * 15, t, anchor="start", fill="#333") for i, t in enumerate(nota)]
y_fin += nh

# ---------------- Cabeceras, líneas de vida y activaciones ----------------
fondo = []
for k, nombre, tipo in participantes:
    x = X[k]
    fondo.append(f'<line x1="{x}" y1="{HEAD_Y + HEAD_H}" x2="{x}" y2="{y_fin - 40}" stroke="#7F7F7F" stroke-dasharray="6,4"/>')
    if tipo == "actor":
        hy = HEAD_Y - 10
        fondo.append(f'<circle cx="{x}" cy="{hy+8}" r="7" fill="{FILL_BOT}" stroke="{STROKE}"/>'
                     f'<line x1="{x}" y1="{hy+15}" x2="{x}" y2="{hy+32}" stroke="{STROKE}"/>'
                     f'<line x1="{x-11}" y1="{hy+21}" x2="{x+11}" y2="{hy+21}" stroke="{STROKE}"/>'
                     f'<polyline points="{x-9},{hy+44} {x},{hy+32} {x+9},{hy+44}" fill="none" stroke="{STROKE}"/>')
        fondo.append(T(x, HEAD_Y + HEAD_H + 8, nombre, bold=True, size=12))
    else:
        w = max(120, len(nombre) * 7.2 + 20)
        fondo.append(f'<defs><linearGradient id="h{k}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{FILL_TOP}"/>'
                     f'<stop offset="1" stop-color="{FILL_BOT}"/></linearGradient></defs>')
        fondo.append(f'<rect x="{x-w/2+3}" y="{HEAD_Y+3}" width="{w}" height="{HEAD_H}" fill="#000" opacity="0.12"/>')
        fondo.append(f'<rect x="{x-w/2}" y="{HEAD_Y}" width="{w}" height="{HEAD_H}" fill="url(#h{k})" stroke="{STROKE}"/>')
        fondo.append(T(x, HEAD_Y + 25, nombre, bold=True, size=12))
for p, y0, y1, nivel in acts:
    x = X[p] - 5 + nivel * 5
    fondo.append(f'<rect x="{x}" y="{y0}" width="10" height="{y1-y0}" fill="{ACT_FILL}" stroke="{STROKE}"/>')

W = X["rpre"] + 160
H = y_fin
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
       "<title>SmartLibrary - Secuencia POST /api/prestamos</title>",
       f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>',
       f'<path d="M10,8 L300,8 L300,22 L290,32 L10,32 Z" fill="#F2F2F2" stroke="#5B5B5B"/>',
       T(18, 25, "sd Registrar préstamo", anchor="start", bold=True, size=12),
       f'<rect x="10" y="8" width="{W-20}" height="{H-18}" fill="none" stroke="#5B5B5B"/>']
svg += fondo + out + nota_svg + ["</svg>"]
with open(sys.argv[1], "w", encoding="utf-8") as fh:
    fh.write("\n".join(svg))
