"""Cola de historias: los JSON de historias/pendientes/ se usan en orden de nombre."""
import glob
import json
import os

from .config import RAIZ

TIPOS = {"emoji", "numero", "fecha", "versus", "sello", "duda", "lista", "pregunta", "final"}
CAMPOS = ["id", "titulo", "descripcion", "hashtags", "escenas"]


def cargar(ruta):
    with open(ruta, encoding="utf-8") as f:
        h = json.load(f)
    validar(h, ruta)
    return h


def validar(h, ruta=""):
    for k in CAMPOS:
        if not h.get(k): raise ValueError(f"{ruta}: falta '{k}'")
    if len(h["titulo"]) > 90: raise ValueError(f"{ruta}: título de más de 90 caracteres")
    if not 6 <= len(h["escenas"]) <= 14: raise ValueError(f"{ruta}: debe tener entre 6 y 14 escenas")
    for i, sc in enumerate(h["escenas"]):
        if not sc.get("texto"): raise ValueError(f"{ruta}: escena {i + 1} sin texto")
        if sc.get("tipo", "emoji") not in TIPOS: raise ValueError(f"{ruta}: escena {i + 1} tipo desconocido {sc.get('tipo')}")
        if sc.get("tipo") == "versus" and len(sc.get("emojis", [])) < 2: raise ValueError(f"{ruta}: escena {i + 1} versus necesita 2 emojis")
        if sc.get("tipo") == "lista" and not sc.get("items"): raise ValueError(f"{ruta}: escena {i + 1} lista sin items")


def todas():
    rutas = sorted(glob.glob(os.path.join(RAIZ, "historias", "pendientes", "*.json")))
    return [(r, cargar(r)) for r in rutas]


def siguientes(usadas):
    return [h for _, h in todas() if h["id"] not in usadas]
