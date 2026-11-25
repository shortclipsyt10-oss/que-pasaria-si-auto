"""Título, descripción y etiquetas de YouTube a partir de la historia."""

PIE = (
    "🤔 En ¿Qué Pasaría Si? imaginamos lo imposible y lo explicamos con ciencia en 1 minuto.\n"
    "🔔 Suscríbete y cuéntanos en comentarios qué quieres que imaginemos la próxima vez.\n\n"
    "Narración con voz sintética. Ilustraciones: Twemoji (CC-BY 4.0) y animación propia."
)

FIJAS = ["qué pasaría si", "que pasaria si", "ciencia", "curiosidades", "experimento mental", "shorts en español"]


def generar(h):
    titulo = h["titulo"].strip()
    if "#shorts" not in titulo.lower() and len(titulo) + 8 <= 100:
        titulo += " #shorts"
    tags = list(dict.fromkeys(h.get("hashtags", [])))
    if "#shorts" not in [t.lower() for t in tags]: tags.append("#shorts")
    partes = [h["descripcion"].strip()]
    if h.get("nota_veracidad"): partes.append("📌 " + h["nota_veracidad"].strip())
    if h.get("fuentes"): partes.append("📚 Fuentes:\n" + "\n".join(f"- {f}" for f in h["fuentes"]))
    partes.append(PIE)
    partes.append(" ".join(tags[:8]))
    desc = "\n\n".join(partes).replace("<", "").replace(">", "")[:4900]
    etiquetas = list(dict.fromkeys(h.get("etiquetas", []) + FIJAS))
    # YouTube limita las etiquetas a ~500 caracteres en total.
    out, n = [], 0
    for e in etiquetas:
        if n + len(e) + 1 > 480: break
        out.append(e); n += len(e) + 1
    return {"titulo": titulo[:100], "descripcion": desc, "etiquetas": out}
