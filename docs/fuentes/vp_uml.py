"""Mini motor para dibujar diagramas de clases UML con estilo Visual Paradigm (SVG)."""
from __future__ import annotations

import math
from html import escape

FONT = "Arial, Helvetica, sans-serif"
CHAR_W = 6.6          # ancho medio de un carácter Arial 12px
BOLD_W = 7.6
LINE_H = 16
PAD_X = 10

FILL_TOP = "#FFFFF4"   # degradado típico de Visual Paradigm (blanco → amarillo pálido)
FILL_BOT = "#FFFFC4"
STROKE = "#A0522D"
ENUM_TOP, ENUM_BOT = "#FBFBFF", "#DDE7F7"
ENUM_STROKE = "#4A6FA5"
TEXT = "#000000"
EDGE = "#404040"


def m(text: str, static: bool = False, abstract: bool = False) -> tuple[str, bool, bool]:
    """Miembro de clase: texto + si es estático (subrayado) o abstracto (cursiva)."""
    return (text, static, abstract)


class Box:
    def __init__(self, name, x, y, attrs=(), ops=(), stereotype=None, abstract=False,
                 enum=False, min_w=150):
        self.name, self.x, self.y = name, x, y
        self.attrs = [a if isinstance(a, tuple) else m(a) for a in attrs]
        self.ops = [o if isinstance(o, tuple) else m(o) for o in ops]
        self.stereotype, self.abstract, self.enum = stereotype, abstract, enum
        lines = [t for t, *_ in self.attrs + self.ops]
        ancho = max([len(t) * CHAR_W for t in lines] +
                    [len(name) * BOLD_W, len(f"«{stereotype}»") * CHAR_W if stereotype else 0])
        self.w = max(min_w, math.ceil(ancho + 2 * PAD_X))
        self.name_h = 26 + (14 if stereotype else 0)
        self.attr_h = len(self.attrs) * LINE_H + 10 if self.attrs else 10
        self.ops_h = 0 if enum else (len(self.ops) * LINE_H + 10 if self.ops else 10)
        self.h = self.name_h + self.attr_h + self.ops_h

    # Anclajes
    @property
    def right(self): return self.x + self.w
    @property
    def bottom(self): return self.y + self.h
    @property
    def cx(self): return self.x + self.w / 2
    @property
    def cy(self): return self.y + self.h / 2

    def svg(self, gid: str) -> str:
        top, bot, stroke = (ENUM_TOP, ENUM_BOT, ENUM_STROKE) if self.enum else (FILL_TOP, FILL_BOT, STROKE)
        out = [f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
               f'<stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bot}"/>'
               f'</linearGradient></defs>',
               f'<rect x="{self.x+3}" y="{self.y+3}" width="{self.w}" height="{self.h}" fill="#000" opacity="0.12"/>',
               f'<rect x="{self.x}" y="{self.y}" width="{self.w}" height="{self.h}" '
               f'fill="url(#{gid})" stroke="{stroke}" stroke-width="1"/>']
        y = self.y + 18
        if self.stereotype:
            out.append(self._text(self.cx, y, f"«{self.stereotype}»", anchor="middle"))
            y += 15
        out.append(self._text(self.cx, y, self.name, anchor="middle", bold=True, italic=self.abstract))
        y_sep = self.y + self.name_h
        out.append(f'<line x1="{self.x}" y1="{y_sep}" x2="{self.right}" y2="{y_sep}" stroke="{stroke}"/>')
        y = y_sep + 17
        for text, static, abstract in self.attrs:
            out.append(self._text(self.x + PAD_X, y, text, italic=abstract, underline=static))
            y += LINE_H
        if not self.enum:
            y_sep2 = self.y + self.name_h + self.attr_h
            out.append(f'<line x1="{self.x}" y1="{y_sep2}" x2="{self.right}" y2="{y_sep2}" stroke="{stroke}"/>')
            y = y_sep2 + 17
            for text, static, abstract in self.ops:
                out.append(self._text(self.x + PAD_X, y, text, italic=abstract, underline=static))
                y += LINE_H
        return "\n".join(out)

    @staticmethod
    def _text(x, y, text, anchor="start", bold=False, italic=False, underline=False):
        style = []
        if bold: style.append("font-weight:bold")
        if italic: style.append("font-style:italic")
        if underline: style.append("text-decoration:underline")
        return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-family="{FONT}" '
                f'font-size="12" fill="{TEXT}" style="{";".join(style)}">{escape(text)}</text>')


def _unit(p, q):
    dx, dy = q[0] - p[0], q[1] - p[1]
    d = math.hypot(dx, dy) or 1
    return dx / d, dy / d


def edge(points, kind="association", labels=()):
    """kind: generalization | composition | association | dependency.
    labels: (x, y, texto[, anchor])."""
    dashed = kind in ("dependency", "realization")
    pts = list(points)
    out = []
    # Recorta la línea para que no atraviese el marcador final/inicial
    end, prev = pts[-1], pts[-2]
    ux, uy = _unit(prev, end)
    if kind in ("generalization", "realization"):
        size = 14
        base = (end[0] - ux * size, end[1] - uy * size)
        pts[-1] = base
        px, py = -uy, ux
        tri = [end, (base[0] + px * 8, base[1] + py * 8), (base[0] - px * 8, base[1] - py * 8)]
        marker = f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in tri)}" fill="#FFFFFF" stroke="{EDGE}"/>'
    elif kind in ("association", "dependency"):
        a = (end[0] - ux * 11 - uy * 5, end[1] - uy * 11 + ux * 5)
        b = (end[0] - ux * 11 + uy * 5, end[1] - uy * 11 - ux * 5)
        marker = (f'<polyline points="{a[0]:.1f},{a[1]:.1f} {end[0]:.1f},{end[1]:.1f} {b[0]:.1f},{b[1]:.1f}" '
                  f'fill="none" stroke="{EDGE}"/>')
    else:
        marker = ""
    if kind == "composition":
        s, nxt = pts[0], pts[1]
        vx, vy = _unit(s, nxt)
        tip2 = (s[0] + vx * 22, s[1] + vy * 22)
        mid = (s[0] + vx * 11, s[1] + vy * 11)
        dia = [s, (mid[0] - vy * 6, mid[1] + vx * 6), tip2, (mid[0] + vy * 6, mid[1] - vx * 6)]
        marker = f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in dia)}" fill="{EDGE}" stroke="{EDGE}"/>'
        pts[0] = tip2
    dash = ' stroke-dasharray="6,4"' if dashed else ""
    out.append(f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="none" '
               f'stroke="{EDGE}" stroke-width="1"{dash}/>')
    out.append(marker)
    for lab in labels:
        x, y, text, *rest = lab
        anchor = rest[0] if rest else "start"
        out.append(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-family="{FONT}" '
                   f'font-size="11" fill="{TEXT}">{escape(text)}</text>')
    return "\n".join(out)


def package(name, boxes, pad=22, extra_w=0, extra_h=0, x=None, y=None, w=None, h=None):
    """Paquete UML (carpeta con pestaña) que envuelve a sus clases, estilo Visual Paradigm."""
    x0 = x if x is not None else min(b.x for b in boxes) - pad
    y0 = y if y is not None else min(b.y for b in boxes) - pad - 22
    x1 = (x0 + w) if w is not None else max(b.right for b in boxes) + pad + extra_w
    y1 = (y0 + h) if h is not None else max(b.bottom for b in boxes) + pad + extra_h
    tab_w = max(90, len(name) * 7.4 + 20)
    svg = (f'<rect x="{x0}" y="{y0}" width="{tab_w}" height="20" fill="#F4F1E1" stroke="#8C7B4F"/>'
           f'<rect x="{x0}" y="{y0+20}" width="{x1-x0}" height="{y1-y0-20}" fill="#FBFAF2" stroke="#8C7B4F"/>'
           f'<text x="{x0+8}" y="{y0+15}" font-family="{FONT}" font-size="12" font-weight="bold" '
           f'fill="{TEXT}">{escape(name)}</text>')
    return Frame(svg, x0, y0 + 20, x1 - x0, y1 - y0 - 20)


class Frame:
    def __init__(self, svg, x, y, w, h):
        self.svg, self.x, self.y, self.w, self.h = svg, x, y, w, h
    @property
    def right(self): return self.x + self.w
    @property
    def bottom(self): return self.y + self.h
    @property
    def cx(self): return self.x + self.w / 2
    @property
    def cy(self): return self.y + self.h / 2


def anchor(p, q):
    """Línea discontinua que une una nota con el elemento que comenta."""
    return (f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}" '
            f'stroke="#7F7F7F" stroke-dasharray="3,3"/>')


def note(x, y, lines, w=None):
    """Nota UML (esquina doblada), como las de Visual Paradigm."""
    w = w or math.ceil(max(len(t) for t in lines) * 6.0 + 24)
    h = len(lines) * 15 + 14
    f = 12
    path = f"M{x},{y} L{x+w-f},{y} L{x+w},{y+f} L{x+w},{y+h} L{x},{y+h} Z"
    out = [f'<path d="{path}" fill="#FFFFFF" stroke="#7F7F7F"/>',
           f'<path d="M{x+w-f},{y} L{x+w-f},{y+f} L{x+w},{y+f}" fill="none" stroke="#7F7F7F"/>']
    for i, t in enumerate(lines):
        out.append(f'<text x="{x+10}" y="{y+19+i*15}" font-family="{FONT}" font-size="11" '
                   f'fill="#333">{escape(t)}</text>')
    return "\n".join(out), (x, y, w, h)


def render(title, boxes, edges, extras=(), path=None, frames=()):
    maxx = max([b.right for b in boxes] + [f.right for f in frames]) + 40
    maxy = max([b.bottom for b in boxes] + [f.bottom for f in frames]) + 40
    for _, (x, y, w, h) in [e for e in extras if isinstance(e, tuple)]:
        maxx, maxy = max(maxx, x + w + 40), max(maxy, y + h + 40)
    body = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{maxx}" height="{maxy}" '
            f'viewBox="0 0 {maxx} {maxy}">',
            f'<title>{escape(title)}</title>',
            f'<rect width="{maxx}" height="{maxy}" fill="#FFFFFF"/>']
    body += [f.svg for f in frames]
    body += edges
    body += [b.svg(f"g{i}") for i, b in enumerate(boxes)]
    body += [e[0] if isinstance(e, tuple) else e for e in extras]
    body.append("</svg>")
    svg = "\n".join(body)
    if path:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(svg)
    return svg
