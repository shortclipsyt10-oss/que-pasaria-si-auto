"""Configuración: config.json (en el repo, sin secretos) + config.local.json (solo en tu PC, opcional)."""
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFECTO = {
    # Dónde se guardan los videos terminados (uno por carpeta).
    "carpeta_salida": "~/Desktop/q pasaria si",
    # Modelos de voz, emojis descargados y archivos temporales.
    "carpeta_datos": "~/.que-pasaria-si",
    # Zona horaria de las horas de publicación.
    "zona_horaria": "Europe/Madrid",
    # Una entrada por video al día. Con la cuota por defecto de YouTube caben 6 subidas al día;
    # cuando Google te amplíe la cuota, añade "03:00" y "06:00" para llegar a 8 (uno cada 3 horas).
    "horas_publicacion": ["09:00", "12:00", "15:00", "18:00", "21:00", "00:00"],
    # Cuántas horas por delante se rellenan en cada ejecución.
    "horizonte_horas": 24,
    # Margen mínimo entre la subida y la publicación (YouTube necesita procesar el video).
    "margen_minutos": 45,
    "subir_a_youtube": True,
    "categoria_youtube": "27",
    "voz": "em_alex",
    "velocidad_voz": 1.12,
    # Fuente de los textos. En Windows se usa "Arial Black" si no tienes Inter instalada.
    "fuente": None,
    "procesos_render": None,
}


def _expand(p):
    return os.path.abspath(os.path.expanduser(os.path.expandvars(p)))


def cargar():
    cfg = dict(DEFECTO)
    for nombre in ("config.json", "config.local.json"):
        ruta = os.path.join(RAIZ, nombre)
        if os.path.exists(ruta):
            with open(ruta, encoding="utf-8") as f:
                cfg.update({k: v for k, v in json.load(f).items() if not k.startswith("_")})
    cfg["carpeta_salida"] = _expand(cfg["carpeta_salida"])
    cfg["carpeta_datos"] = _expand(cfg["carpeta_datos"])
    if not cfg.get("fuente"):
        cfg["fuente"] = "Arial Black" if sys.platform == "win32" else "Inter Display Black"
    if not cfg.get("procesos_render"):
        cfg["procesos_render"] = max(1, min(6, (os.cpu_count() or 2) - 1))
    os.makedirs(cfg["carpeta_salida"], exist_ok=True)
    os.makedirs(cfg["carpeta_datos"], exist_ok=True)
    return cfg
