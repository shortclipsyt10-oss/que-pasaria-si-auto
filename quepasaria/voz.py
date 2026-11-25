"""Narración con Kokoro TTS (local, gratis) y reparto de subtítulos por palabra."""
import json
import os
import re
import urllib.request

import numpy as np

MODELOS = {
    "kokoro-v1.0.onnx": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx",
    "voices-v1.0.bin": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin",
}


def descargar_modelos(carpeta):
    os.makedirs(carpeta, exist_ok=True)
    for nombre, url in MODELOS.items():
        p = os.path.join(carpeta, nombre)
        if os.path.exists(p) and os.path.getsize(p) > 1_000_000:
            continue
        print(f"Descargando {nombre} (solo la primera vez)...")
        tmp = p + ".part"
        urllib.request.urlretrieve(url, tmp)
        os.replace(tmp, p)


def norm(w):
    return re.sub(r"[^\wáéíóúñü]", "", w.lower())


def narrar(lineas, workdir, carpeta_modelos, voz="em_alex", velocidad=1.12):
    import soundfile as sf
    tj = os.path.join(workdir, "timing.json")
    if os.path.exists(tj):
        old = json.load(open(tj, encoding="utf-8"))
        if old and old[0].get("lines") == lineas and os.path.exists(os.path.join(workdir, "voz.wav")):
            return old
    descargar_modelos(carpeta_modelos)
    from kokoro_onnx import Kokoro
    k = Kokoro(os.path.join(carpeta_modelos, "kokoro-v1.0.onnx"), os.path.join(carpeta_modelos, "voices-v1.0.bin"))
    out = []; t = 0; meta = []; gap = 0.18; sr = 24000
    for l in lineas:
        s, sr = k.create(l, voice=voz, speed=velocidad, lang="es"); s = np.asarray(s)
        idx = np.where(np.abs(s) > 0.01)[0]
        if len(idx): s = s[max(idx[0] - 200, 0):idx[-1] + 400]
        d = len(s) / sr; meta.append({"text": l, "start": t, "end": t + d})
        out.append(s); out.append(np.zeros(int(gap * sr))); t += d + gap
    meta[0]["lines"] = lineas
    sf.write(os.path.join(workdir, "voz.wav"), np.concatenate(out), sr)
    json.dump(meta, open(tj, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return meta


def trozos(meta):
    """Reparte el tiempo de cada frase entre sus palabras y las agrupa de 3 en 3 para los subtítulos."""
    words = []
    for li, m in enumerate(meta):
        toks = m["text"].split(); wts = []
        for tk in toks:
            w = len(norm(tk)) + 2
            if tk.endswith((",", ":", ";")): w += 3
            if tk.endswith((".", "?", "…", "!")): w += 6
            wts.append(w)
        tot = sum(wts); t = m["start"]; dur = m["end"] - m["start"]
        for tk, w in zip(toks, wts):
            d = dur * w / tot; words.append(dict(w=tk, s=t, e=t + d, line=li)); t += d
    chunks = []; cur = []
    for i, wd in enumerate(words):
        cur.append(wd); nxt = words[i + 1] if i + 1 < len(words) else None
        if len(cur) >= 3 or wd["w"][-1] in ",.?:…!;" or nxt is None or nxt["line"] != wd["line"]:
            chunks.append(cur); cur = []
    return chunks
