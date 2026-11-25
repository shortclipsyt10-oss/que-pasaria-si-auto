"""Subida a YouTube con la API oficial (YouTube Data API v3).

Las credenciales NUNCA van al repositorio: se guardan en la carpeta de datos (~/.que-pasaria-si/):
  client_secret.json  -> lo descargas tú de Google Cloud (ver README)
  token.json          -> se crea solo al ejecutar `python -m quepasaria autorizar`
"""
import json
import os
import random
import time

SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.readonly"]


class CuotaAgotada(Exception):
    pass


def _rutas(cfg):
    d = cfg["carpeta_datos"]
    return os.path.join(d, "client_secret.json"), os.path.join(d, "token.json")


def autorizar(cfg):
    from google_auth_oauthlib.flow import InstalledAppFlow
    secreto, token = _rutas(cfg)
    if not os.path.exists(secreto):
        raise SystemExit(f"No encuentro {secreto}. Descárgalo de Google Cloud (paso 4 del README) y guárdalo ahí con ese nombre.")
    flow = InstalledAppFlow.from_client_secrets_file(secreto, SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")
    with open(token, "w", encoding="utf-8") as f:
        f.write(creds.to_json())
    yt = _cliente_con(creds)
    ch = yt.channels().list(part="snippet", mine=True).execute().get("items", [])
    nombre = ch[0]["snippet"]["title"] if ch else "(sin canal)"
    print(f"Autorizado. Canal: {nombre}")
    return nombre


def _cliente_con(creds):
    from googleapiclient.discovery import build
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def cliente(cfg):
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    _, token = _rutas(cfg)
    if not os.path.exists(token):
        raise SystemExit("Falta autorizar YouTube. Ejecuta: python -m quepasaria autorizar")
    creds = Credentials.from_authorized_user_file(token, SCOPES)
    if not creds.valid:
        creds.refresh(Request())
        with open(token, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
    return _cliente_con(creds)


def _es_cuota(e):
    txt = str(getattr(e, "content", b"")) + str(e)
    return "quotaExceeded" in txt or "uploadLimitExceeded" in txt or "dailyLimitExceeded" in txt


def subir(cfg, mp4, meta, publicar_en=None, miniatura=None):
    """Sube el video. publicar_en: datetime con zona horaria (se programa) o None (público ya). Devuelve el id."""
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload
    yt = cliente(cfg)
    status = {"selfDeclaredMadeForKids": False, "embeddable": True, "license": "youtube"}
    if publicar_en:
        status["privacyStatus"] = "private"
        status["publishAt"] = publicar_en.astimezone().isoformat()
    else:
        status["privacyStatus"] = "public"
    body = {
        "snippet": {
            "title": meta["titulo"], "description": meta["descripcion"], "tags": meta["etiquetas"],
            "categoryId": cfg["categoria_youtube"], "defaultLanguage": "es", "defaultAudioLanguage": "es",
        },
        "status": status,
    }
    media = MediaFileUpload(mp4, mimetype="video/mp4", chunksize=8 * 1024 * 1024, resumable=True)
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    resp = None; intento = 0
    while resp is None:
        try:
            _, resp = req.next_chunk()
        except HttpError as e:
            if _es_cuota(e): raise CuotaAgotada(str(e))
            if e.resp.status in (500, 502, 503, 504) and intento < 6:
                intento += 1; time.sleep(min(60, 2 ** intento + random.random())); continue
            raise
        except (ConnectionError, TimeoutError, OSError):
            if intento < 6:
                intento += 1; time.sleep(min(60, 2 ** intento + random.random())); continue
            raise
    vid = resp["id"]
    if miniatura and os.path.exists(miniatura):
        try:
            yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(miniatura, mimetype="image/png")).execute()
        except HttpError as e:
            # Los Shorts y los canales sin verificar por teléfono no siempre aceptan miniatura personalizada.
            print(f"  Aviso: YouTube no aceptó la miniatura ({e.resp.status}). El video se sube igual.")
    return vid
