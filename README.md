# ¿Qué Pasaría Si?: canal automático de shorts

Segundo canal, hermano de [dato-curioso-auto](https://github.com/shortclipsyt10-oss/dato-curioso-auto). Convierte guiones de "¿qué pasaría si…?" en shorts verticales (1080x1920, ~1 min) con dibujos animados planos y los publica solos en YouTube.

1. **Guiones** (`historias/pendientes/*.json`): pregunta imposible contada como mini-historia, con cifras reales y fuentes. Los escribe Claude y llegan al repo solos cada día. Formato en [`historias/FORMATO.md`](historias/FORMATO.md).
2. **Video** (`quepasaria/video.py` + `ilustrado.py`): voz Kokoro, escenarios dibujados (la Tierra con cara, espacio, Luna, Marte, ciudad de colores…), subtítulos palabra a palabra, música generada por código y miniatura.
3. **Publicación** (`.github/workflows/publicar.yml`): cada 3 horas en GitHub Actions genera y sube a YouTube los videos programados en los huecos de `horas_publicacion`. El PC puede estar apagado.
4. **Imagen del canal** (`canal/`): logo, banner y descripción.

Secreto necesario en GitHub (Settings > Secrets and variables > Actions): `YT_TOKEN` con el contenido de `token.json`.

## Conectar YouTube (solo una vez)

Las credenciales **nunca** se suben al repo: viven en `C:\Users\<tú>\.que-pasaria-si\`.

1. Entra en <https://console.cloud.google.com/> con la cuenta de Google del canal y crea un proyecto llamado `¿Qué Pasaría Si?`.
2. En **APIs y servicios → Biblioteca**, busca **YouTube Data API v3** y pulsa **Habilitar**.
3. En **Google Auth Platform** (antes "Pantalla de consentimiento de OAuth"):
   - Tipo de usuario: **Externo**. Nombre de la app: `¿Qué Pasaría Si?`. Pon tu email de contacto.
   - En **Público**, añade tu cuenta como usuario de prueba y después pulsa **Publicar app** para pasarla a **En producción**. Si la dejas en "Prueba", el permiso caduca cada 7 días y la subida automática se para.
4. En **Clientes** (o **Credenciales → Crear credenciales → ID de cliente de OAuth**): tipo **App de escritorio**, nombre `que-pasaria-si-pc`. Descarga el JSON, renómbralo a `client_secret.json` y guárdalo en `C:\Users\<tú>\.que-pasaria-si\client_secret.json`.
5. En la carpeta del repo ejecuta:
   ```powershell
   .venv\Scripts\python -m quepasaria autorizar
   ```
   Se abre el navegador. Elige la cuenta (o la cuenta de marca) del canal. Verás "Google no ha verificado esta app": es tu propia app, pulsa **Configuración avanzada → Ir a ¿Qué Pasaría Si?** y acepta. Al terminar, la consola muestra el nombre del canal.

### Límites de la API de YouTube (importante)

- **Videos privados hasta la auditoría.** Google bloquea en privado los videos subidos por API desde proyectos nuevos sin auditar. Para quitar el bloqueo hay que rellenar el formulario gratuito *YouTube API Services – Audit and Quota Extension*: <https://support.google.com/youtube/contact/yt_api_form>. Explica que es una herramienta interna que sube los shorts de tu propio canal.
- **Cuota.** Cada subida cuesta ~1.600 unidades y la cuota diaria por defecto es 10.000, así que caben **6 subidas al día**. Pide **20.000 unidades/día** en el mismo formulario. Cuando la aprueben, añade más horas a `horas_publicacion` en `config.json`.
- **Miniaturas.** La API solo deja poner miniatura personalizada si el canal está verificado por teléfono (<https://www.youtube.com/verify>). En los Shorts YouTube a veces muestra igualmente un fotograma del video.

## Comandos

```text
python -m quepasaria comprobar   revisa instalación, modelos y credenciales
python -m quepasaria autorizar   conecta el canal de YouTube
python -m quepasaria previa ID   imagen con todas las escenas (rápido)
python -m quepasaria render ID   genera el video sin subirlo
python -m quepasaria lote        lo que hace la tarea programada (--sin-subir para solo generar)
python -m quepasaria estado      lo programado y lo que queda en cola
```

## Formato de las historias

Ver [`historias/FORMATO.md`](historias/FORMATO.md).

## Créditos

Emojis: [Twemoji](https://github.com/jdecked/twemoji), CC-BY 4.0 (se acredita en cada descripción). Voz: [Kokoro](https://github.com/thewh1teagle/kokoro-onnx).
