"""Genera la imagen de perfil (800x800) y el banner (2560x1440) del canal con los mismos dibujos de los videos.

  python canal/generar_marca.py RUTA/InterDisplay-Black.otf
"""
import math
import os
import sys

import cairo
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from quepasaria import ilustrado as I  # noqa: E402
from quepasaria import dibujo as D  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
FUENTE = sys.argv[1] if len(sys.argv) > 1 else "InterDisplay-Black.otf"


def fondo_espacio(c, w, h, seed=7):
    g = cairo.RadialGradient(w / 2, h / 2, 50, w / 2, h / 2, max(w, h) * 0.8)
    g.add_color_stop_rgba(0, *I.hexc("#2b3a8c")); g.add_color_stop_rgba(1, *I.hexc("#070b1f"))
    c.set_source(g); c.paint()
    import random
    rnd = random.Random(seed)
    for k in range(int(w * h / 9000)):
        I.col(c, "#ffffff", rnd.uniform(0.3, 0.95)); c.arc(rnd.uniform(0, w), rnd.uniform(0, h), rnd.uniform(1.5, 4.5), 0, 2 * math.pi); c.fill()


def estrella(c, x, y, r, colr, rot=0):
    c.save(); c.translate(x, y); c.rotate(rot)
    for i in range(10):
        a = i * math.pi / 5 - math.pi / 2; rr = r if i % 2 == 0 else r * 0.45
        c.line_to(rr * math.cos(a), rr * math.sin(a))
    c.close_path(); I.col(c, colr); c.fill_preserve(); I.col(c, "#111111"); c.set_line_width(r * 0.12); c.stroke(); c.restore()


def texto(im, s, xy, size, fill, stroke=10, anchor="mm"):
    d = ImageDraw.Draw(im); f = ImageFont.truetype(FUENTE, size)
    d.text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill="#111111")


def logo(ruta):
    S = 800
    sf = cairo.ImageSurface(cairo.FORMAT_ARGB32, S, S); c = cairo.Context(sf)
    fondo_espacio(c, S, S)
    I.planet_earth(c, 375, 385, 235, 0.4, "sorpresa")
    D.mascot(c, 590, 545, 250, 0.18)
    p = os.path.join(AQUI, "_tmp.png"); sf.write_to_png(p)
    im = Image.open(p).convert("RGB"); os.remove(p)
    im.save(ruta)


def banner(ruta):
    Wb, Hb = 2560, 1440
    sf = cairo.ImageSurface(cairo.FORMAT_ARGB32, Wb, Hb); c = cairo.Context(sf)
    fondo_espacio(c, Wb, Hb, 3)
    # Zona segura (visible en todos los dispositivos): 1546x423 centrada.
    I.planet_earth(c, 655, 720, 125, 0.4, "sorpresa")
    D.mascot(c, 1935, 720, 230, 0.15)
    for x, y, r, cc, rot in [(520, 330, 46, "#ffd23f", 0.2), (2050, 380, 40, "#ff6b6b", -0.3), (430, 1080, 38, "#69db7c", 0.4),
                             (2140, 1040, 50, "#ffd23f", 0.1), (1280, 300, 30, "#ffffff", 0), (1300, 1150, 30, "#ffffff", 0.5)]:
        estrella(c, x, y, r, cc, rot)
    I.planet_earth(c, 260, 260, 110, 0.0, face=False)
    c.save(); I.col(c, "#f1f3f5"); c.arc(2330, 1180, 80, 0, 2 * math.pi); c.fill()
    I.col(c, "#ced4da")
    for dx, dy, r in [(-25, -20, 18), (20, 15, 12), (30, -30, 9)]: c.arc(2330 + dx, 1180 + dy, r, 0, 2 * math.pi); c.fill()
    c.restore()
    p = os.path.join(AQUI, "_tmp.png"); sf.write_to_png(p)
    im = Image.open(p).convert("RGB"); os.remove(p)
    texto(im, "¿QUÉ PASARÍA SI?", (1290, 670), 104, "#ffd23f", 11)
    d = ImageDraw.Draw(im); f = ImageFont.truetype(FUENTE, 44)
    sub = "Lo imposible, explicado en 1 minuto"
    w = d.textlength(sub, font=f)
    d.rounded_rectangle((1290 - w / 2 - 40, 790 - 45, 1290 + w / 2 + 40, 790 + 45), radius=45, fill="#111111")
    d.text((1290, 790), sub, font=f, fill="#ffffff", anchor="mm")
    im.save(ruta)


if __name__ == "__main__":
    logo(os.path.join(AQUI, "logo.png"))
    banner(os.path.join(AQUI, "banner.png"))
    print("Listo: canal/logo.png y canal/banner.png")
