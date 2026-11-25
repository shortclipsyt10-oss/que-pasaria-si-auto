"""Convierte una historia (JSON) en un short 1080x1920 con voz, animación, subtítulos, música y miniatura."""
import hashlib
import json
import math
import multiprocessing as mp
import os
import shutil
import subprocess

import cairo

from . import dibujo as D
from .dibujo import W, H, FPS, PI, back, ease, col, text, chip, emoji, mascot
from .voz import narrar, trozos, norm
from .musica import musica

MARCA = "¿QUÉ PASARÍA SI?"

PALETAS = {
    "historia": [("#ffd98a", "#d9822b"), ("#ffe6b0", "#b5651d"), ("#f6c177", "#8c4a1c")],
    "animales": [("#b8f5a0", "#2f9e44"), ("#a0e8ff", "#1c7ed6"), ("#ffe08a", "#f08c00")],
    "oceano": [("#9be7ff", "#1864ab"), ("#7fd8e8", "#0b7285"), ("#a5d8ff", "#364fc7")],
    "ciencia": [("#d0bfff", "#5f3dc4"), ("#99e9f2", "#1098ad"), ("#b2f2bb", "#2b8a3e")],
    "espacio": [("#748ffc", "#1a1b4b"), ("#9775fa", "#22114a"), ("#4dabf7", "#0b1d3a")],
    "cuerpo": [("#ffc9c9", "#c92a2a"), ("#fcc2d7", "#a61e4d"), ("#ffd8a8", "#d9480f")],
    "comida": [("#fff3bf", "#f59f00"), ("#ffe8cc", "#e8590c"), ("#d3f9d8", "#37b24d")],
    "rareza": [("#ffec99", "#e67700"), ("#c5f6fa", "#0c8599"), ("#eebefa", "#9c36b5")],
}


def ffmpeg_exe():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        exe = shutil.which("ffmpeg")
        if not exe: raise RuntimeError("No encuentro ffmpeg. Ejecuta: pip install imageio-ffmpeg")
        return exe


def semilla(h):
    return int(hashlib.md5(h["id"].encode()).hexdigest()[:8], 16)


# ---------------- escenas ----------------
def _pop(u, k=0, delay=0.15, speed=3.0):
    return back((u - k * delay) * speed)


def _emojis_grupo(c, ems, u, t, cy=800):
    n = len(ems)
    pos = {1: [(540, cy, 470)], 2: [(300, cy, 340), (780, cy, 340)], 3: [(540, cy - 150, 290), (290, cy + 140, 270), (790, cy + 140, 270)]}[min(n, 3)]
    for k, (e, (x, y, s)) in enumerate(zip(ems, pos)):
        p = _pop(u, k)
        emoji(c, e, x, y + math.sin(t * 2 + k) * 18, s * p, rot=math.sin(t * 1.6 + k) * 0.08)


def _decor(c, ems, t, sd):
    """Emojis pequeños y transparentes flotando al fondo."""
    import random
    rnd = random.Random(sd)
    for k in range(7):
        e = ems[k % len(ems)]
        x = rnd.uniform(60, W - 60); sp = rnd.uniform(25, 55)
        y = (rnd.uniform(0, H) - t * sp) % (H + 200) - 100
        emoji(c, e, x, y, rnd.uniform(70, 120), rot=math.sin(t + k) * 0.3, alpha=0.18, shadow=False)


def escena(c, sc, idx, u, d, t, pal, sd):
    c1, c2 = pal[idx % len(pal)]
    tipo = sc.get("tipo", "emoji")
    ems = sc.get("emojis") or ([sc["emoji"]] if sc.get("emoji") else [])
    ilustrada = bool(sc.get("fondo")) and tipo not in ("pregunta", "final")
    if ilustrada:
        from . import ilustrado as I
        gy = I.fondo(c, sc["fondo"], t, sc.get("animo"))
        I.personajes(c, sc.get("personajes"), gy, t, sc.get("accion"), sd + idx)
        if tipo == "emoji":
            # Con escenario, los emojis son objetos que flotan sobre la escena, más pequeños.
            n = len(ems)
            if sc["fondo"] == "tierra":
                # La Tierra con cara ocupa el centro: los objetos giran a su alrededor.
                for k, e in enumerate(ems[:3]):
                    a = t * 0.9 + k * 2 * PI / max(1, min(n, 3)) - PI / 2
                    emoji(c, e, 540 + math.cos(a) * 430, 800 + math.sin(a) * 400, 180 * _pop(u, k))
                ems = []; n = 0
            pos = {1: [(540, 760, 300)], 2: [(330, 760, 240), (750, 760, 240)], 3: [(540, 640, 200), (300, 860, 190), (780, 860, 190)]}
            for k, (e, (x, y, sz)) in enumerate(zip(ems[:3], pos.get(min(n, 3), []))):
                emoji(c, e, x, y + math.sin(t * 2 + k) * 14, sz * _pop(u, k), rot=math.sin(t * 1.6 + k) * 0.08)
            ems = []
    else:
        D.radial_bg(c, t, c1, c2)
        if ems: _decor(c, ems, t, sd + idx)
        D.sparkles(c, t, seed=sd + idx)
    p = u / max(d, 0.01)
    if sc.get("rotulo") and tipo not in ("versus",):
        colr = sc.get("color", ["#ff3b30", "#1c7ed6", "#2b8a3e", "#e67700", "#862e9c", "#c2255c"][idx % 6])
        chip(c, sc["rotulo"].upper(), 540, 360, colr, size=66, sc=_pop(u, 0, speed=4))

    if tipo == "emoji":
        if not ilustrada: _emojis_grupo(c, ems or ["🤔"], u, t)
    elif tipo == "numero":
        if ems: emoji(c, ems[0], 540, 620 + math.sin(t * 2) * 14, 270 * _pop(u), rot=math.sin(t * 1.5) * 0.08)
        v = str(sc.get("valor", ""))
        digits = v.replace(".", "").replace(",", "")
        if digits.isdigit() and len(digits) <= 9:
            val = int(digits) * ease(min(1, u / 1.2)); s = f"{int(round(val)):,}".replace(",", ".")
            if val >= int(digits): s = v
        else:
            s = v
        D.fit_text(c, s, 540, 930, 230 * back(u * 3), 960, fill="#ffd23f", stroke="#111111", sw=0.12, shadow=True)
        if sc.get("unidad"): D.fit_text(c, sc["unidad"].upper(), 540, 1080, 70 * back(u * 3 - 0.3), 960, fill="#ffffff", stroke="#111111", sw=0.2)
    elif tipo == "fecha":
        if ems: emoji(c, ems[0], 540, 600 + math.sin(t * 2) * 14, 280 * _pop(u))
        D.fit_text(c, str(sc.get("anio", "")), 540, 900, 250 * back(u * 3), 960, fill="#ffffff", stroke="#111111", sw=0.12, shadow=True)
        col(c, "#111111", 0.8); c.set_line_width(16); c.set_line_cap(1)
        c.move_to(140, 1060); c.line_to(140 + 800 * ease(u * 1.5), 1060); c.stroke()
        col(c, "#ffd23f"); c.arc(140 + 800 * ease(u * 1.5), 1060, 26, 0, 2 * PI); c.fill()
    elif tipo == "versus":
        r = sc.get("rotulos", ["", ""])
        for k, (x, e) in enumerate(zip((280, 800), ems[:2])):
            pp = _pop(u, k, 0.25)
            emoji(c, e, x, 760 + math.sin(t * 3 + k * 2) * 20, 330 * pp, rot=(1 if k else -1) * 0.1 * math.sin(t * 2))
            if k < len(r) and r[k]: D.fit_text(c, r[k].upper(), x, 1020, 64 * pp, 460, fill="#ffffff", stroke="#111111", sw=0.2)
        pv = back((u - 0.3) * 4)
        D.burst_vs = None
        c.save(); c.translate(540, 760); c.rotate(t * 0.8); col(c, "#ff3b30")
        for i in range(10):
            a = i * PI / 5; c.line_to(110 * pv * math.cos(a), 110 * pv * math.sin(a)); c.line_to(65 * pv * math.cos(a + PI / 10), 65 * pv * math.sin(a + PI / 10))
        c.close_path(); c.fill(); c.restore()
        text(c, "VS", 540, 760, 80 * pv, fill="#ffffff", stroke="#111111", sw=0.12)
        if sc.get("rotulo"): chip(c, sc["rotulo"].upper(), 540, 360, "#111111", "#ffd23f", size=60, sc=_pop(u, 0, speed=4))
    elif tipo in ("sello", "duda"):
        if not (ilustrada and (sc.get("personajes") or sc.get("fondo") == "tierra")): _emojis_grupo(c, ems or ["🤔"], u, t)
        txt = sc.get("sello") or ("¿LEYENDA?" if tipo == "duda" else "¡VERDAD!")
        colr = "#e67700" if tipo == "duda" else sc.get("color_sello", "#e03131")
        D.stamp(c, txt.upper(), 540, 1000, (p - 0.3) * 1.6, 120, colr, -0.12)
    elif tipo == "lista":
        items = sc.get("items", [])[:3]
        n = max(1, len(items)); step = min(1.2, d * 0.7 / n)
        for k, (e, s) in enumerate(items):
            pp = back((u - k * step) * 3)
            if pp <= 0.002: continue
            y = 600 + k * 210
            c.save(); col(c, "#ffffff", 0.85); D.rrect(c, 70, y - 90, 940, 180, 40); c.fill(); c.restore()
            emoji(c, e, 180, y, 140 * pp, shadow=False)
            sz = 62; w = D.text_w(c, s.upper(), sz)
            if w > 700: sz *= 700 / w
            text(c, s.upper(), 290, y, sz * pp, fill="#111111", stroke=None, anchor="l")
    elif tipo == "pregunta":
        mascot(c, 540, 800 + math.sin(t * 3) * 20, 620 * _pop(u), rot=math.sin(t * 2.2) * 0.12)
        for k, e in enumerate(ems[:3]):
            a = t * 1.2 + k * 2 * PI / max(1, len(ems[:3]))
            emoji(c, e, 540 + math.cos(a) * 380, 800 + math.sin(a) * 300, 170 * _pop(u, k + 1))
    elif tipo == "final":
        D.confetti(c, u, seed=sd)
        mascot(c, 540, 780 + math.sin(t * 3) * 20, 560 * _pop(u), rot=math.sin(t * 2.5) * 0.15)
        chip(c, "¡SÍGUENOS!", 540, 1080, "#ff3b30", size=90, sc=back((u - 0.4) * 3) * (1 + 0.05 * math.sin(t * 8)))
    else:
        _emojis_grupo(c, ems or ["🤔"], u, t)


# ---------------- vídeo completo ----------------
class Render:
    def __init__(self, historia, meta, fuente, carpeta_emojis):
        self.h = historia; self.meta = meta
        D.set_fuente(fuente); D.set_carpeta_emojis(carpeta_emojis)
        self.TOTAL = meta[-1]["end"] + 1.2
        self.chunks = trozos(meta)
        self.keys = {norm(k) for k in historia.get("claves", [])}
        self.pal = PALETAS.get(historia.get("paleta", "rareza"), PALETAS["rareza"])
        self.sd = semilla(historia)

    def frame(self, t):
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(surf)
        meta = self.meta; li = 0
        for k, m in enumerate(meta):
            if t >= m["start"] - 0.09: li = k
        st = meta[li]["start"] - 0.09
        en = meta[li + 1]["start"] - 0.09 if li + 1 < len(meta) else self.TOTAL
        u = max(0, t - st); d = en - st
        z = 1.0 + 0.05 * (u / d)
        c.save(); c.translate(W / 2, H / 2); c.scale(z, z); c.translate(-W / 2, -H / 2)
        escena(c, self.h["escenas"][li], li, u, d, t, self.pal, self.sd)
        c.restore()
        if u < 0.12 and li > 0:
            col(c, "#ffffff", 0.6 * (1 - u / 0.12)); c.paint()
        chip(c, MARCA, 540, 170, "#111111", "#ffd23f", 44)
        col(c, "#000000", 0.3); c.rectangle(0, H - 14, W, 14); c.fill()
        col(c, "#ffd23f"); c.rectangle(0, H - 14, W * t / self.TOTAL, 14); c.fill()
        self.subtitulos(c, t)
        return surf

    def subtitulos(self, c, t):
        for ch in self.chunks:
            if ch[0]["s"] - 0.02 <= t < ch[-1]["e"] + 0.05:
                size = 100; gap = 46
                ws = [w["w"].upper() for w in ch]
                widths = [D.text_w(c, w, size) for w in ws]
                total = sum(widths) + gap * (len(ws) - 1)
                k = min(1, (W - 120) / total)
                pin = back((t - ch[0]["s"]) * 7)
                y = 1270; x = 540 - total * k / 2
                for w, wd, wobj in zip(ws, widths, ch):
                    active = wobj["s"] <= t < wobj["e"] + 0.05
                    fill = "#ffd23f" if active else ("#7CFC00" if norm(wobj["w"]) in self.keys else "#ffffff")
                    s2 = size * k * (1.08 if (active and k >= 1) else 1) * (0.6 + 0.4 * pin)
                    text(c, w, x + wd * k / 2, y, s2, fill=fill, stroke="#000000", sw=0.2)
                    x += (wd + gap) * k
                break


_R = {}


def _worker_init(historia, meta, fuente, carpeta_emojis, rutas=None):
    _R["r"] = Render(historia, meta, fuente, carpeta_emojis)


def _render_part(args):
    a, b, out, ff = args
    r = _R["r"]
    p = subprocess.Popen([ff, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for f in range(a, b):
        s = r.frame(f / FPS); s.flush(); p.stdin.write(bytes(s.get_data()))
    p.stdin.close(); p.wait()
    if p.returncode: raise RuntimeError("ffmpeg falló al codificar un trozo")
    return out


def precargar_emojis(historia):
    ems = set()
    for sc in historia["escenas"]:
        ems.update(sc.get("emojis") or [])
        if sc.get("emoji"): ems.add(sc["emoji"])
        for it in sc.get("items", []): ems.add(it[0])
    ems.update(historia.get("miniatura", {}).get("emojis", []))
    for e in ems: D.emoji_png(e)


def miniatura(historia, ruta, fuente, carpeta_emojis):
    D.set_fuente(fuente); D.set_carpeta_emojis(carpeta_emojis)
    pal = PALETAS.get(historia.get("paleta", "rareza"), PALETAS["rareza"])
    sf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(sf)
    D.burst(c, 540, 1000, 2200, pal[0][1], pal[0][0], 22)
    m = historia.get("miniatura", {})
    ems = m.get("emojis") or historia["escenas"][0].get("emojis") or ["🤯"]
    _emojis_grupo(c, ems, 10, 0, cy=1080)
    mascot(c, 880, 1560, 380, 0.15)
    txt = m.get("texto", historia["titulo"]).upper()
    lines = D.wrap(c, txt, 150, 960)
    size = 150 * min(1, 3 / max(1, len(lines)))
    lines = D.wrap(c, txt, size, 960)
    y = 420 - (len(lines) - 1) * size * 0.55
    for k, ln in enumerate(lines):
        D.fit_text(c, ln, 540, y + k * size * 1.1, size, 980, fill="#ffd23f" if k % 2 == 0 else "#ffffff", stroke="#111111", sw=0.14, shadow=True)
    chip(c, MARCA, 540, 150, "#111111", "#ffd23f", 48)
    sf.write_to_png(ruta)


def guion_md(historia, meta):
    filas = "\n".join(f"| {i + 1} | {m['start']:.1f} s | {m['text']} |" for i, m in enumerate(meta))
    nota = historia.get("nota_veracidad", "")
    return (f"# {historia['titulo']} ({meta[-1]['end']:.0f} s)\n\n"
            + (f"**Nota de veracidad:** {nota}\n\n" if nota else "")
            + "## Guion\n\n| # | Tiempo | Texto |\n|---|---|---|\n" + filas + "\n\n"
            + "## Fuentes\n\n" + "\n".join(f"- {f}" for f in historia.get("fuentes", [])) + "\n")


def renderizar(historia, cfg, solo_previa=False):
    """Genera el MP4, la miniatura y el guion en carpeta_salida/<id>/. Devuelve la carpeta."""
    datos = cfg["carpeta_datos"]
    work = os.path.join(datos, "trabajo", historia["id"]); os.makedirs(work, exist_ok=True)
    emo = os.path.join(datos, "emojis"); D.set_carpeta_emojis(emo)
    precargar_emojis(historia)
    lineas = [s["texto"] for s in historia["escenas"]]
    meta = narrar(lineas, work, os.path.join(datos, "modelos"), cfg["voz"], cfg["velocidad_voz"])
    od = os.path.join(cfg["carpeta_salida"], historia["id"]); os.makedirs(od, exist_ok=True)
    miniatura(historia, os.path.join(od, "miniatura.png"), cfg["fuente"], emo)
    r = Render(historia, meta, cfg["fuente"], emo)
    rutas = None
    if solo_previa:
        from PIL import Image
        ims = []
        for i, m in enumerate(meta):
            tt = m["start"] + (m["end"] - m["start"]) * 0.6
            p = os.path.join(work, f"still_{i:02d}.png"); r.frame(tt).write_to_png(p); ims.append(Image.open(p).resize((360, 640)))
        cols = 6; rows = (len(ims) + cols - 1) // cols
        g = Image.new("RGB", (360 * cols, 640 * rows))
        for i, im in enumerate(ims): g.paste(im, ((i % cols) * 360, (i // cols) * 640))
        g.save(os.path.join(od, "previa.png"))
        return od
    ff = ffmpeg_exe()
    musica(os.path.join(work, "music.wav"), r.TOTAL, [m["start"] for m in meta[1:]], r.sd)
    N = int(r.TOTAL * FPS); P = cfg["procesos_render"]; q = N // P + 1
    jobs = [(i * q, min((i + 1) * q, N), os.path.join(work, f"part{i}.mp4"), ff) for i in range(P) if i * q < N]
    ctx = mp.get_context("spawn")
    with ctx.Pool(len(jobs), initializer=_worker_init, initargs=(historia, meta, cfg["fuente"], emo, rutas)) as pool:
        parts = pool.map(_render_part, jobs)
    lst = os.path.join(work, "list.txt")
    with open(lst, "w", encoding="utf-8") as f:
        f.write("".join(f"file '{p.replace(os.sep, '/')}'\n" for p in parts))
    vid = os.path.join(work, "video.mp4")
    subprocess.run([ff, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", vid], check=True)
    final = os.path.join(od, f"{historia['id']}.mp4")
    subprocess.run([ff, "-y", "-loglevel", "error", "-i", vid, "-i", os.path.join(work, "voz.wav"), "-i", os.path.join(work, "music.wav"),
                    "-filter_complex", "[1:a]aresample=44100[v];[2:a]volume=0.16[mu];[v][mu]amix=inputs=2:duration=longest:normalize=0,loudnorm=I=-14:TP=-1.5[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", final], check=True)
    with open(os.path.join(od, "guion.md"), "w", encoding="utf-8") as f:
        f.write(guion_md(historia, meta))
    with open(os.path.join(od, "historia.json"), "w", encoding="utf-8") as f:
        json.dump(historia, f, ensure_ascii=False, indent=1)
    shutil.rmtree(work, ignore_errors=True)
    return od
