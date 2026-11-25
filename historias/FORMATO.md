# Formato de un guion de "¿Qué pasaría si...?"

Cada video es un JSON en `historias/pendientes/NNN-slug.json`. Se publican por orden de nombre, así que el número manda.

```json
{
 "id": "001-todos-saltan-a-la-vez",             // igual que el nombre del archivo, sin .json
 "titulo": "¿Qué pasaría si todos saltáramos a la vez? 🌍",   // máx. 90 caracteres; se añade #shorts solo
 "descripcion": "Dos frases que enganchen.",
 "hashtags": ["#quepasariasi", "#ciencia", "#shorts"],
 "etiquetas": ["qué pasaría si", "tierra"],
 "paleta": "espacio",                      // historia | animales | oceano | ciencia | espacio | cuerpo | comida | rareza
 "miniatura": {"texto": "¿Y SI TODOS SALTAMOS?", "emojis": ["🌍", "🤸"]},
 "nota_veracidad": "Qué dicen los cálculos y qué es simplificación.",
 "fuentes": ["Autor (año), publicación"],
 "claves": ["palabras", "que", "salen", "en", "verde"],
 "escenas": [ { "texto": "Frase narrada", "tipo": "emoji", "emojis": ["🌍"], "rotulo": "Texto del cartel",
               "fondo": "tierra", "animo": "sorpresa", "personajes": ["chica"], "accion": "celebrar" } ]
}
```

## Tipos de escena

| tipo | campos | qué se ve |
|---|---|---|
| `emoji` | `emojis` (1-3), `rotulo` | emojis grandes que rebotan |
| `numero` | `valor` ("8.000.000.000"), `unidad`, `emojis` (1), `rotulo` | número gigante que cuenta hacia arriba |
| `fecha` | `anio`, `emojis` (1), `rotulo` | año grande con línea de tiempo |
| `versus` | `emojis` (2), `rotulos` (2), `rotulo` | dos cosas enfrentadas con un VS |
| `sello` | `emojis`, `sello` | emojis y un sello rojo encima ("¡NADA!", "¡BOOM!") |
| `duda` | `emojis`, `sello` (por defecto "¿LEYENDA?") | sello naranja: para lo que es especulación |
| `lista` | `items`: [["🥶","Frío"], ...] (máx. 3) | filas que aparecen una a una |
| `pregunta` | `emojis` (opcional) | la mascota "?" con emojis girando (ideal para la primera escena) |
| `final` | — | mascota + "¡SÍGUENOS!" + confeti (siempre la última) |

## Escenario y personajes (dibujo animado plano y limpio)

Cada escena (menos `pregunta` y `final`) lleva un escenario dibujado y, si encaja, personajes:

- `fondo`:
  - Propios de este canal: **tierra** (la Tierra con cara en el centro; usa `animo`: sorpresa, feliz, triste, miedo; con este fondo usa tipo `emoji` o `sello`, los emojis giran alrededor), **espacio** (estrellas y la Tierra de lado), **luna** (suelo lunar con la Tierra al fondo), **ciudad_color** (edificios de colores y césped), **ciudad_noche**, **bosque**, **playa**, **volcan**, **casa** (salón por dentro), **cielo** (nubes, para cosas que vuelan o caen), **oceano_profundo**, **marte** (suelo rojo).
  - Heredados: desierto, campo, pueblo, pueblo_noche, ciudad, noche, mar, bajo_agua, egipto, nieve, palacio, laboratorio.
- `personajes` (máx. 4): chica, chico, hombre, mujer, nino, anciano, cientifico, medico, astronauta, soldado, rey, reina, granjero, marinero, explorador, atleta, gente (grupo), multitud (grupo grande); animales dibujados: emu, oso, conejo, pulpo, abeja. Otros animales u objetos van como `emojis`.
- `accion` (opcional): andar, correr, bailar, celebrar, hablar, senalar, triste, tumbado
- Con `fondo`, los `emojis` se dibujan como objetos sobre la escena.

## Reglas editoriales

- **Un "¿qué pasaría si...?" con historia.** Cada video plantea UNA situación imposible o extrema (todos saltamos a la vez, la Luna desaparece, dejamos de dormir, un agujero atraviesa la Tierra…) y la cuenta como una mini-historia en orden: planteamiento, qué pasaría en el primer segundo, después, la consecuencia más sorprendente y un remate. Tono narrativo y divertido, como si se lo contaras a un amigo.
- La primera escena es la pregunta, dicha tal cual ("¿Qué pasaría si todas las personas del mundo saltaran a la vez?"), con el fondo `tierra` o con tipo `pregunta`.
- 10-12 escenas, unas 130-160 palabras en total: dura entre 45 y 65 segundos.
- Español neutro, frases cortas, números escritos con letra en `texto` (la voz los lee mejor) y con cifras en `valor`/`anio`.
- **Ciencia de verdad.** Las cifras salen de cálculos o fuentes reales (física, biología, NASA, divulgadores como Randall Munroe o Kurzgesagt…). Si algo es especulación, dilo ("según algunos cálculos", "probablemente") y explica el matiz en `nota_veracidad`.
- Nada de temas repetidos: revisa `historias/pendientes/` y `estado/registro.json` antes de escribir.
- Nada morboso ni que dé miedo de verdad (muertes, enfermedades graves reales): el humor va por lo absurdo.
- Emojis: solo emojis estándar (Twemoji 15.1); se comprueban al validar.
- La última escena es `final` y termina con "Síguenos para más preguntas imposibles." o una variante.
