"""¿Qué Pasaría Si?: generación y publicación automática de shorts.

  python -m quepasaria comprobar        revisa que todo esté instalado
  python -m quepasaria autorizar        conecta tu canal de YouTube (una sola vez)
  python -m quepasaria previa [ID]      genera una imagen con todas las escenas (rápido)
  python -m quepasaria render [ID]      genera el video sin subirlo
  python -m quepasaria lote             rellena los huecos de publicación de las próximas horas (lo que ejecuta la tarea programada)
  python -m quepasaria estado           muestra lo programado y lo que queda en cola
"""
import argparse
import datetime as dt
import json
import os
import sys
import shutil
import traceback

from . import config, historias, metadatos

try:
    sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


def _tz(cfg):
    from zoneinfo import ZoneInfo
    return ZoneInfo(cfg["zona_horaria"])


def _reg_path(cfg):
    if cfg.get("archivo_registro"):
        p = os.path.join(config.RAIZ, cfg["archivo_registro"]); os.makedirs(os.path.dirname(p), exist_ok=True); return p
    return os.path.join(cfg["carpeta_salida"], "registro.json")


def usadas(reg):
    """Historias ya subidas, o generadas cuyo video sigue en disco."""
    return {k for k, v in reg["videos"].items() if v.get("youtube_id") or (v.get("mp4") and os.path.exists(v["mp4"]))}


def leer_registro(cfg):
    p = _reg_path(cfg)
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f: return json.load(f)
    return {"videos": {}}


def guardar_registro(cfg, reg):
    p = _reg_path(cfg); tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f: json.dump(reg, f, ensure_ascii=False, indent=1)
    os.replace(tmp, p)


def log(cfg, msg):
    linea = f"[{dt.datetime.now():%Y-%m-%d %H:%M}] {msg}"
    print(linea)
    with open(os.path.join(cfg["carpeta_salida"], "registro.log"), "a", encoding="utf-8") as f: f.write(linea + "\n")


def huecos(cfg, reg, ahora):
    tz = _tz(cfg); ahora = ahora.astimezone(tz)
    ocupados = {v.get("publicar_en") or v.get("reservado") for v in reg["videos"].values()} - {None}
    ini = ahora + dt.timedelta(minutes=cfg["margen_minutos"]); fin = ahora + dt.timedelta(hours=cfg["horizonte_horas"])
    out = []
    por_dia = {}
    for o in ocupados:
        try: d = dt.datetime.fromisoformat(o).astimezone(tz).date(); por_dia[d] = por_dia.get(d, 0) + 1
        except ValueError: pass
    for dia in range(0, 3):
        fecha = (ahora + dt.timedelta(days=dia)).date()
        # Nunca más videos en un día que horas de publicación hay (p. ej. 1 al día).
        if por_dia.get(fecha, 0) >= len(cfg["horas_publicacion"]): continue
        for hh in cfg["horas_publicacion"]:
            h, m = map(int, hh.split(":"))
            s = dt.datetime(fecha.year, fecha.month, fecha.day, h, m, tzinfo=tz)
            if ini <= s <= fin and s.isoformat() not in ocupados: out.append(s)
    return sorted(set(out))


def buscar(cfg, ident):
    reg = leer_registro(cfg)
    if ident:
        for r, h in historias.todas():
            if h["id"] == ident or os.path.basename(r).startswith(ident): return h
        raise SystemExit(f"No encuentro la historia {ident}")
    pend = historias.siguientes(usadas(reg))
    if not pend: raise SystemExit("No quedan historias pendientes.")
    return pend[0]


def listos_pendientes(reg):
    """Videos ya terminados en listos/<id>/ (con su historia.json) que aún no se han subido."""
    base = os.path.join(config.RAIZ, "listos")
    if not os.path.isdir(base): return []
    out = []
    for d in sorted(os.listdir(base)):
        c = os.path.join(base, d)
        if os.path.exists(os.path.join(c, f"{d}.mp4")) and d not in reg["videos"]:
            out.append(c)
    return out


def cmd_estadisticas(cfg, args):
    """Guarda visitas, likes y comentarios de cada video subido en estado/estadisticas.json."""
    from . import youtube
    reg = leer_registro(cfg)
    ids = {v["youtube_id"]: k for k, v in reg["videos"].items() if v.get("youtube_id")}
    if not ids: print("Aún no hay videos subidos."); return
    yt = youtube.cliente(cfg); filas = []
    lista = list(ids)
    for i in range(0, len(lista), 50):
        r = yt.videos().list(part="statistics,snippet,contentDetails", id=",".join(lista[i:i + 50])).execute()
        for it in r.get("items", []):
            st = it.get("statistics", {}); k = ids[it["id"]]; v = reg["videos"][k]
            pub = it["snippet"].get("publishedAt", "")
            try:
                horas = max(1.0, (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(pub.replace("Z", "+00:00"))).total_seconds() / 3600)
            except Exception:
                horas = 1.0
            vis = int(st.get("viewCount", 0))
            filas.append({"id": k, "youtube_id": it["id"], "titulo": it["snippet"]["title"], "paleta": v.get("paleta"),
                          "publicado": pub, "horas": round(horas, 1), "visitas": vis, "likes": int(st.get("likeCount", 0)),
                          "comentarios": int(st.get("commentCount", 0)), "visitas_por_hora": round(vis / horas, 2)})
    filas.sort(key=lambda x: -x["visitas_por_hora"])
    p = os.path.join(config.RAIZ, "estado", "estadisticas.json"); os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump({"actualizado": dt.datetime.now(dt.timezone.utc).isoformat(timespec="minutes"), "videos": filas}, f, ensure_ascii=False, indent=1)
    for x in filas[:10]: print(f"{x['visitas']:>7} visitas  {x['visitas_por_hora']:>7}/h  {x['titulo']}")


def puede_subir(cfg, reg):
    if not cfg["subir_a_youtube"]: return False
    subidos = sum(1 for x in reg["videos"].values() if x.get("youtube_id"))
    return cfg.get("auditoria_aprobada", True) or subidos < cfg.get("subidas_antes_de_auditoria", 1)


def cmd_lote(cfg, args):
    if cfg.get("ejecutar_en") == "nube" and not os.environ.get("GITHUB_ACTIONS"):
        print("La publicación se hace en GitHub Actions (config.json: ejecutar_en = nube). Este PC no sube nada."); return
    if cfg.get("pausado"):
        log(cfg, "Publicación en pausa (config.json: pausado = true)."); return
    from . import video, youtube
    lock = os.path.join(cfg["carpeta_datos"], "lote.lock")
    if os.path.exists(lock) and (dt.datetime.now().timestamp() - os.path.getmtime(lock)) < 3 * 3600:
        print("Ya hay un lote en marcha; salgo."); return
    open(lock, "w").close()
    try:
        reg = leer_registro(cfg)
        libres = huecos(cfg, reg, dt.datetime.now(dt.timezone.utc))
        if args.ahora:
            libres = [None] + libres
        if args.max: libres = libres[:args.max]
        if not libres:
            log(cfg, "Nada que hacer: todos los huecos de las próximas horas ya están programados."); return
        log(cfg, f"Huecos por rellenar: {', '.join('ahora' if s is None else s.strftime('%d/%m %H:%M') for s in libres)}")
        for slot in libres:
            # Reutiliza un video ya renderizado que no se pudo subir; si no, la siguiente historia.
            pend_subida = [k for k, v in reg["videos"].items() if not v.get("youtube_id") and v.get("mp4") and os.path.exists(v["mp4"])
                          and (puede_subir(cfg, reg) and not args.sin_subir or not v.get("reservado"))]
            if pend_subida:
                hid = pend_subida[0]; h = json.load(open(os.path.join(reg["videos"][hid]["carpeta"], "historia.json"), encoding="utf-8"))
            elif listos_pendientes(reg):
                carpeta = listos_pendientes(reg)[0]; h = json.load(open(os.path.join(carpeta, "historia.json"), encoding="utf-8")); hid = h["id"]
                log(cfg, f"Video ya hecho: {hid}")
                reg["videos"][hid] = {"carpeta": carpeta, "mp4": os.path.join(carpeta, f"{hid}.mp4"), "titulo": h["titulo"], "listo": True,
                                      "paleta": h.get("paleta")}
                guardar_registro(cfg, reg)
            else:
                cola = historias.siguientes(usadas(reg))
                if not cola:
                    log(cfg, "⚠️ No quedan historias en la cola (haz git pull o espera a que lleguen más)."); break
                h = cola[0]; hid = h["id"]
                log(cfg, f"Renderizando {hid}...")
                carpeta = video.renderizar(h, cfg)
                reg["videos"][hid] = {"carpeta": carpeta, "mp4": os.path.join(carpeta, f"{hid}.mp4"), "titulo": h["titulo"],
                                      "paleta": h.get("paleta"), "renderizado_en": dt.datetime.now().isoformat(timespec="seconds")}
                guardar_registro(cfg, reg)
            v = reg["videos"][hid]
            meta = metadatos.generar(h)
            with open(os.path.join(v["carpeta"], "metadatos.json"), "w", encoding="utf-8") as f: json.dump(meta, f, ensure_ascii=False, indent=1)
            subidos = sum(1 for x in reg["videos"].values() if x.get("youtube_id"))
            bloqueo = not cfg.get("auditoria_aprobada", True) and subidos >= cfg.get("subidas_antes_de_auditoria", 1)
            if bloqueo and not getattr(cmd_lote, "_aviso", False):
                log(cfg, "Auditoría de YouTube pendiente: solo genero los videos (los subidos ahora quedarían bloqueados en privado).")
                cmd_lote._aviso = True
            if not cfg["subir_a_youtube"] or args.sin_subir or bloqueo:
                # Reserva el hueco para no generar más videos de la cuenta; se subirá cuando se active la subida.
                v["reservado"] = (slot or dt.datetime.now(_tz(cfg))).isoformat(); guardar_registro(cfg, reg)
                log(cfg, f"Listo (sin subir): {v['mp4']}"); continue
            try:
                yid = youtube.subir(cfg, v["mp4"], meta, publicar_en=slot, miniatura=os.path.join(v["carpeta"], "miniatura.png"))
            except youtube.CuotaAgotada:
                log(cfg, "Cuota diaria de YouTube agotada. Lo reintento en la próxima ejecución."); break
            v.update(youtube_id=yid, publicar_en=(slot or dt.datetime.now(_tz(cfg))).isoformat(timespec="seconds"), subido_en=dt.datetime.now().isoformat(timespec="seconds"))
            if v.get("listo"):
                shutil.rmtree(v["carpeta"], ignore_errors=True)
            guardar_registro(cfg, reg)
            log(cfg, f"Subido {hid} -> https://youtube.com/shorts/{yid} ({'publicado ya' if slot is None else f'se publica {slot:%d/%m %H:%M}'})")
        quedan = len(historias.siguientes(usadas(reg)))
        if quedan < len(cfg["horas_publicacion"]) * 2:
            log(cfg, f"Aviso: solo quedan {quedan} historias en cola.")
    finally:
        try: os.remove(lock)
        except OSError: pass


def cmd_estado(cfg, args):
    reg = leer_registro(cfg)
    prog = sorted((v["publicar_en"], k, v.get("youtube_id")) for k, v in reg["videos"].items() if v.get("publicar_en"))
    print("Programados / publicados:")
    for p, k, y in prog[-20:]: print(f"  {p[:16].replace('T', ' ')}  {k}  https://youtube.com/shorts/{y}")
    cola = historias.siguientes(usadas(reg))
    print(f"\nHistorias en cola: {len(cola)}")
    for h in cola[:10]: print(f"  {h['id']}: {h['titulo']}")


def cmd_comprobar(cfg, args):
    ok = True
    print(f"Carpeta de videos: {cfg['carpeta_salida']}\nCarpeta de datos:  {cfg['carpeta_datos']}\nFuente: {cfg['fuente']}")
    for mod in ["cairo", "kokoro_onnx", "soundfile", "numpy", "PIL", "resvg_py", "imageio_ffmpeg", "googleapiclient", "google_auth_oauthlib"]:
        try: __import__(mod); print(f"  ✔ {mod}")
        except Exception as e: ok = False; print(f"  ✘ {mod}: {e}")
    try:
        from zoneinfo import ZoneInfo; ZoneInfo(cfg["zona_horaria"]); print(f"  ✔ zona horaria {cfg['zona_horaria']}")
    except Exception as e: ok = False; print(f"  ✘ zona horaria: {e} (pip install tzdata)")
    try:
        n = len(historias.todas()); print(f"  ✔ {n} historias válidas")
    except Exception as e: ok = False; print(f"  ✘ historias: {e}")
    from .voz import descargar_modelos
    descargar_modelos(os.path.join(cfg["carpeta_datos"], "modelos")); print("  ✔ modelos de voz")
    for nombre in ("client_secret.json", "token.json"):
        p = os.path.join(cfg["carpeta_datos"], nombre)
        print(f"  {'✔' if os.path.exists(p) else '·'} {nombre} {'' if os.path.exists(p) else '(falta)'}")
    print("\nTodo bien." if ok else "\nHay que arreglar lo marcado con ✘.")


def main():
    ap = argparse.ArgumentParser(prog="quepasaria", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("comprobar"); sub.add_parser("autorizar"); sub.add_parser("estado"); sub.add_parser("estadisticas")
    for n in ("previa", "render"):
        p = sub.add_parser(n); p.add_argument("id", nargs="?")
    p = sub.add_parser("lote"); p.add_argument("--sin-subir", action="store_true"); p.add_argument("--max", type=int); p.add_argument("--ahora", action="store_true")
    args = ap.parse_args()
    cfg = config.cargar()
    try:
        if args.cmd == "comprobar": cmd_comprobar(cfg, args)
        elif args.cmd == "autorizar":
            from . import youtube; youtube.autorizar(cfg)
        elif args.cmd == "estado": cmd_estado(cfg, args)
        elif args.cmd in ("previa", "render"):
            from . import video
            h = buscar(cfg, args.id)
            print(video.renderizar(h, cfg, solo_previa=args.cmd == "previa"))
        elif args.cmd == "lote": cmd_lote(cfg, args)
        elif args.cmd == "estadisticas": cmd_estadisticas(cfg, args)
    except SystemExit:
        raise
    except Exception:
        log(cfg, "ERROR:\n" + traceback.format_exc()); sys.exit(1)


if __name__ == "__main__":
    main()
