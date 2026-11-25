"""Primitivas de dibujo con Cairo, la mascota del canal y los emojis (Twemoji, CC-BY 4.0)."""
import io
import math
import os
import random
import urllib.request

import cairo

W, H, FPS = 1080, 1920, 30
PI = math.pi
FUENTE = {"nombre": "Inter Display Black"}


def set_fuente(nombre):
    FUENTE["nombre"] = nombre


def _font(c):
    # "Arial Black" ya es gruesa; pedir negrita encima la deforma en Windows.
    peso = cairo.FONT_WEIGHT_NORMAL if "black" in FUENTE["nombre"].lower() and "inter" not in FUENTE["nombre"].lower() else cairo.FONT_WEIGHT_BOLD
    c.select_font_face(FUENTE["nombre"], cairo.FONT_SLANT_NORMAL, peso)


def ease(x):
    x = max(0, min(1, x)); return 1 - (1 - x) ** 3


def back(x):
    x = max(0, min(1, x)); k = 2.2; return max(0.001, 1 + (k + 1) * (x - 1) ** 3 + k * (x - 1) ** 2)


def hexc(h, a=1):
    h = h.lstrip('#'); h = ''.join(ch * 2 for ch in h) if len(h) == 3 else h
    return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)


def col(c, hx, a=1):
    c.set_source_rgba(*hexc(hx, a))


def rrect(c, x, y, w, h, r):
    c.new_sub_path(); c.arc(x + w - r, y + r, r, -PI / 2, 0); c.arc(x + w - r, y + h - r, r, 0, PI / 2)
    c.arc(x + r, y + h - r, r, PI / 2, PI); c.arc(x + r, y + r, r, PI, 3 * PI / 2); c.close_path()


def ell(c, x, y, rx, ry):
    c.save(); c.translate(x, y); c.scale(rx, ry); c.arc(0, 0, 1, 0, 2 * PI); c.restore()


def text_w(c, s, size):
    _font(c); c.set_font_size(size); return c.text_extents(s).x_advance


def text(c, s, x, y, size, fill="#ffffff", stroke="#111111", sw=0.16, anchor="c", rot=0, alpha=1, shadow=False):
    c.save(); _font(c); c.set_font_size(size); e = c.text_extents(s)
    c.translate(x, y); c.rotate(rot)
    ox = -e.x_advance / 2 if anchor == "c" else (0 if anchor == "l" else -e.x_advance)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    if shadow:
        c.move_to(ox + size * 0.05, size * 0.43); c.text_path(s)
        c.set_line_width(size * sw); col(c, "#000000", 0.35 * alpha); c.stroke_preserve(); c.fill()
    c.move_to(ox, size * 0.36); c.text_path(s)
    if stroke:
        c.set_line_width(size * sw); col(c, stroke, alpha); c.stroke_preserve()
    col(c, fill, alpha); c.fill(); c.restore()
    return e.x_advance


def fit_text(c, s, x, y, size, maxw, **kw):
    w = text_w(c, s, size)
    if w > maxw: size *= maxw / w
    return text(c, s, x, y, size, **kw)


def wrap(c, s, size, maxw):
    """Parte un texto en líneas que quepan en maxw."""
    words, lines, cur = s.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if cur and text_w(c, t, size) > maxw:
            lines.append(cur); cur = wd
        else:
            cur = t
    if cur: lines.append(cur)
    return lines


def chip(c, s, x, y, bg="#ff3b30", fg="#ffffff", size=50, a=1, sc=1, maxw=980):
    w = text_w(c, s, size) + size * 1.1
    if w > maxw: size *= maxw / w; w = maxw
    h = size * 1.6
    c.save(); c.translate(x, y); c.scale(sc, sc)
    col(c, "#000000", 0.25 * a); rrect(c, -w / 2 + 6, -h / 2 + 8, w, h, h / 2); c.fill()
    col(c, bg, a); rrect(c, -w / 2, -h / 2, w, h, h / 2); c.fill(); c.restore()
    text(c, s, x, y, size * sc, fill=fg, stroke=None, alpha=a)


def stamp(c, s, x, y, p, size=150, colr="#e74c3c", rot=-0.2):
    if p <= 0: return
    w0 = text_w(c, s, size)
    if w0 > 860: size *= 860 / w0
    sc = 1 + 2.5 * (1 - ease(p * 3)) if p < 0.34 else 1
    a = min(1, p * 4)
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(sc, sc)
    w = text_w(c, s, size) + 80
    col(c, "#ffffff", 0.85 * a); rrect(c, -w / 2, -size * 0.75, w, size * 1.5, 24); c.fill()
    c.set_line_width(14); col(c, colr, a); rrect(c, -w / 2, -size * 0.75, w, size * 1.5, 24); c.stroke()
    c.restore()
    text(c, s, x, y, size * sc, fill=colr, stroke=None, rot=rot, alpha=a)


def radial_bg(c, t, c1, c2, rays=True):
    g = cairo.RadialGradient(540, 820, 50, 540, 820, 1400)
    g.add_color_stop_rgba(0, *hexc(c1)); g.add_color_stop_rgba(1, *hexc(c2))
    c.set_source(g); c.paint()
    if rays:
        for k in range(16):
            c.save(); c.translate(540, 820); c.rotate(k * PI / 8 + t * 0.15)
            col(c, "#ffffff", 0.07); c.move_to(0, 0); c.line_to(1700, -140); c.line_to(1700, 140); c.close_path(); c.fill(); c.restore()


def burst(c, cx, cy, R, a, b, n=24, rot=0):
    col(c, a); c.paint(); col(c, b)
    for i in range(n):
        t0 = rot + i * 2 * PI / n; t1 = t0 + PI / n
        c.move_to(cx, cy); c.line_to(cx + R * math.cos(t0), cy + R * math.sin(t0)); c.line_to(cx + R * math.cos(t1), cy + R * math.sin(t1)); c.close_path(); c.fill()
    g = cairo.RadialGradient(cx, cy, 0, cx, cy, R * 0.7); g.add_color_stop_rgba(0, 1, 1, 1, 0.18); g.add_color_stop_rgba(1, 0, 0, 0, 0.25)
    c.set_source(g); c.paint()


def confetti(c, u, seed=1, n=70):
    rnd = random.Random(seed)
    for k in range(n):
        x = rnd.uniform(0, W); sp = rnd.uniform(200, 500); y = (rnd.uniform(0, H) + u * sp) % H
        col(c, rnd.choice(["#ffd23f", "#ffffff", "#00cec9", "#ff7675", "#55efc4"]))
        c.save(); c.translate(x, y); c.rotate(u * 3 + k); c.rectangle(-10, -5, 20, 10); c.fill(); c.restore()


def sparkles(c, t, seed=3, n=14, colr="#ffffff"):
    rnd = random.Random(seed)
    for k in range(n):
        x = rnd.uniform(60, W - 60); y = rnd.uniform(300, 1150); ph = (t * rnd.uniform(0.4, 0.9) + rnd.random()) % 1
        r = 10 + 18 * math.sin(ph * PI)
        col(c, colr, 0.55 * math.sin(ph * PI)); c.save(); c.translate(x, y); c.rotate(PI / 4)
        c.move_to(0, -r); c.line_to(r * 0.25, 0); c.line_to(0, r); c.line_to(-r * 0.25, 0); c.close_path(); c.fill()
        c.move_to(-r, 0); c.line_to(0, r * 0.25); c.line_to(r, 0); c.line_to(0, -r * 0.25); c.close_path(); c.fill(); c.restore()


def mascot(c, x, y, s, rot=0):
    """Signo de interrogación con cara (mascota del canal). x,y centro; s = altura."""
    c.save(); c.translate(x, y); c.rotate(rot)
    w = 0.24 * s; R = 0.22 * s; cy = -0.2 * s

    def path():
        c.new_path(); c.arc(0, cy, R, PI * 0.95, PI * 2.3); c.line_to(0, 0.13 * s)

    def dot():
        c.new_sub_path(); c.arc(0, 0.38 * s, 0.12 * s, 0, 2 * PI)

    c.set_line_cap(1); c.set_line_join(1)
    for dx, dy, clr, ww in [(0.04 * s, 0.06 * s, ("#000000", 0.35), w + 0.08 * s), (0, 0, ("#111111", 1), w + 0.08 * s), (0, 0, ("#ffd23f", 1), w)]:
        c.save(); c.translate(dx, dy); col(c, *clr)
        path(); c.set_line_width(ww); c.stroke()
        dot(); c.fill_preserve()
        if ww > w: c.set_line_width(ww - w); c.stroke()
        c.new_path(); c.restore()
    col(c, "#ffd23f"); dot(); c.fill()
    col(c, "#ffffff", 0.45); c.arc(-0.2 * s, -0.36 * s, 0.035 * s, 0, 2 * PI); c.fill()
    ey = -0.42 * s
    for dx in (-0.085, 0.085):
        col(c, "#ffffff"); c.arc(dx * s, ey, s * 0.068, 0, 2 * PI); c.fill_preserve(); col(c, "#111111"); c.set_line_width(s * 0.016); c.stroke()
        col(c, "#111111"); c.arc(dx * s + s * 0.015, ey + s * 0.01, s * 0.036, 0, 2 * PI); c.fill()
        col(c, "#ffffff"); c.arc(dx * s + s * 0.027, ey - s * 0.005, s * 0.012, 0, 2 * PI); c.fill()
    c.set_line_width(s * 0.016); col(c, "#111111"); c.arc(0, -0.34 * s, 0.04 * s, PI * 0.15, PI * 0.85); c.stroke()
    col(c, "#ff6b6b", 0.6)
    for dx in (-0.16, 0.16):
        c.save(); c.translate(dx * s, -0.35 * s); c.scale(1, 0.6); c.arc(0, 0, s * 0.03, 0, 2 * PI); c.fill(); c.restore()
    c.restore()


# ---------------- emojis ----------------
TWEMOJI = "https://raw.githubusercontent.com/jdecked/twemoji/v15.1.0/assets/svg/{}.svg"
_cache = {}
_dir = {"ruta": None}


def set_carpeta_emojis(ruta):
    os.makedirs(ruta, exist_ok=True); _dir["ruta"] = ruta


def _codigos(e):
    cps = [f"{ord(ch):x}" for ch in e]
    a = "-".join(cps)
    b = "-".join(x for x in cps if x != "fe0f")
    return [b, a] if "200d" not in cps else [a, b]


def emoji_png(e, size=512):
    """Devuelve la ruta a un PNG del emoji (lo descarga y lo rasteriza la primera vez)."""
    base = _dir["ruta"]
    for code in _codigos(e):
        p = os.path.join(base, f"{code}_{size}.png")
        if os.path.exists(p): return p
    import resvg_py
    for code in _codigos(e):
        try:
            with urllib.request.urlopen(TWEMOJI.format(code), timeout=20) as r:
                svg = r.read().decode("utf-8")
        except Exception:
            continue
        png = resvg_py.svg_to_bytes(svg_string=svg, width=size, height=size)
        p = os.path.join(base, f"{code}_{size}.png")
        with open(p, "wb") as f: f.write(bytes(png))
        return p
    raise ValueError(f"No encuentro el emoji {e!r} en Twemoji")


def emoji_surface(e):
    if e not in _cache:
        _cache[e] = cairo.ImageSurface.create_from_png(emoji_png(e))
    return _cache[e]


def emoji(c, e, x, y, size, rot=0, alpha=1, shadow=True):
    """Dibuja un emoji centrado en x,y con alto 'size'."""
    if size <= 1: return
    s = emoji_surface(e); k = size / s.get_width()
    if shadow:
        col(c, "#000000", 0.18 * alpha); ell(c, x, y + size * 0.52, size * 0.36, size * 0.06); c.fill()
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(k, k)
    c.set_source_surface(s, -s.get_width() / 2, -s.get_height() / 2)
    c.paint_with_alpha(alpha); c.restore()
