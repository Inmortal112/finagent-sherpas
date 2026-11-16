# Visitas — David (voz: `voice.py`)

<!-- Añade tu entrada más reciente justo debajo de esta línea. Plantilla en visitas/README.md -->
<!-- Las entradas del 12 nov vienen tal cual de `comunicacion.md`, sustituido por esta carpeta. -->

## 2026-11-16 17:00 — feat/voice-rain-drops — Claude Code
- **Hecho:** fusionado el PR #66 de Raúl (rediseño + cámaras; check.sh en verde). Probado en el iPhone de David:
  fluido. La lluvia no sonaba a lluvia: rehecha con gotas (golpecitos, «plics», estéreo) en `web/house_sound.js`.
- **Estado:** `bash check.sh` pasa. Medido: −30 dB bajo la voz como antes; sin errores en la página.
- **Decisiones:** sigue sin archivos de audio; la lluvia se genera justo después del primer toque para no congelarlo.
- **Para Raúl:** no toco `stage_page.html` ni `house3d.js`; solo cambia el sonido de la lluvia.
- **Siguiente:** que David la vuelva a oír en el iPhone; botón «Send to …» de la nota para la pareja.

## 2026-11-16 13:30 — feat/voice-house-sound — Claude Code
- **Hecho:** la casa suena: lluvia suave con nota baja, pájaros con nota alta y un «ding» con «I've done this»
  (`web/house_sound.js`, Web Audio, sin archivos). Mismo `healthOf(score)` que el cielo 3D. Ficha `voz-casa-suena.md`.
- **Estado:** `bash check.sh` pasa. Probado en el navegador: niveles medidos y enganches funcionando, sin errores.
  Falta oírlo en el iPhone.
- **Decisiones:** fondo muy bajo (lluvia −30 dB respecto a la voz) y ducking de −9 dB mientras habla la voz.
- **Bloqueos:** el PR #63 se quedó atascado en GitHub (502): esta rama va encima de la suya y lo incluye.
- **Para Raúl:** 6 líneas en `stage_page.html` (busca `houseSound`): cargar el módulo, `paint()`, `markDone()` y el
  botón de sonido. Si chocan con lo tuyo, consérvalas al resolver.
- **Siguiente:** oírlo en el iPhone; botón de la nota para la pareja cuando suba Raúl.

## 2026-11-16 13:05 — feat/voice-partner-note — Claude Code
- **Hecho:** nota de voz para la pareja: `partner_note.py` + `GET /partner-note` y `/partner-note/{id}.mp3`. Quien
  recorre el plan manda a su pareja ~15 s con su preocupación y el paso elegido (nota antes → después). Revisadas
  además las 92 narraciones finales con `to_speech` y Whisper: suenan bien, nada que cambiar.
- **Estado:** `bash check.sh` pasa. Probada con el servidor y edge: Whisper oye el texto palabra por palabra.
- **Decisiones:** frases fijas sin modelo; solo cifras del plan; sin pronombres; solo parejas. Ficha `voz-nota-pareja.md`.
- **Bloqueos:** falta el botón en la página: espero a que Raúl suba lo suyo para no pisarle `stage_page.html`.
- **Para Samuel:** dos rutas nuevas en `server.py` (y su línea en el docstring); nada más cambia.
- **Para Raúl:** cuando subas, un botón «Send to {to}» tras elegir paso: `GET /partner-note?session_id=&person=` y,
  en iPhone, `navigator.share({files: [mp3]})`. Detalles en `VOICE.md`. Lo puedo hacer yo si prefieres.
- **Siguiente:** el botón; después añadirlo a `SUBMISSION.md` (aún no, porque la página no lo enseña).

## 2026-11-16 12:44 — docs/submission-draft — Claude Code
- **Hecho:** borrador de la entrega final en `SUBMISSION.md` (inglés, ~650 palabras): lista de las 4 cosas que pide
  BRIEF.md y, bajo la línea, el texto de «half a page to one page» para pegar en Discord.
- **Estado:** `bash check.sh` pasa. Solo documentación. Faltan dos enlaces (MVP y vídeo), marcados `TODO`.
- **Decisiones:** solo cuenta lo que ya está en `main` (3D por defecto en completo, «I've done this», día 3, nota del
  asesor). Cifras: solo las del README (82, 73 años).
- **Bloqueos:** ninguno.
- **Para Samuel y Raúl:** revisadlo y corregid lo que no sea cierto el día de la demo; si se recorta algo, su frase fuera.
- **Siguiente:** revisar cómo suenan las narraciones finales (`to_speech`).

## 2026-11-16 12:39 — docs/visitas-iphone-3d — Claude Code
- **Hecho:** probada la casa 3D nueva (PR #60) en el iPhone de David: `out/` regenerado (voz edge, sin gastar
  créditos: la narración sale de `narrations/`), servidor local y túnel `scripts/share.sh` (cloudflared).
- **Estado:** **en el iPhone va fluido.** En el navegador del ordenador, 3D activo y sin errores en consola.
  No probados aún en el iPhone: «I've done this», «Simply» en 2D y el micrófono.
- **Decisiones:** **el 3D se queda por defecto en el modo completo** (era la decisión del 17 a las 14:00).
- **Bloqueos:** ninguno. Ojo al copiar enlaces: un `**` pegado a la URL da un 500 en Windows (el `*` no vale en nombres).
- **Para Samuel y Raúl:** no hace falta volver al 2D; lo que queda es pulir.
- **Siguiente:** micrófono en el iPhone; README y párrafo de entrega.

## 2026-11-15 23:57 — docs/visitas-public-repo — Claude Code
- **Hecho:** regeneradas las páginas de las cuatro familias en los dos modos (`finagent.run --all`, voz edge; `out/`
  no va a git). Revisado el historial entero del repo antes de hacerlo público (ver «Para Samuel»).
- **Estado:** `bash check.sh` pasa (165). 8 páginas y 92 mp3; 56 de ellos nuevos por los textos cambiados.
- **Decisiones:** ninguna nueva.
- **Bloqueos:** solo el dueño del repo puede cambiar la visibilidad: David tiene permiso de escritura, no de admin.
- **Para Samuel:** **recuerda pasar el repo a público** antes de la entrega (mié 18, 23:59): Sherpas lo pide para
  mentores y jurado. Settings → General → Danger Zone → Change visibility. Revisado: en ningún commit hay `.env`,
  claves, tokens ni audios (`.env`, `.env.*` y `out/` están en `.gitignore`; el único `TEAM_KEY=` es el
  marcador «paste-…» del README de Sherpas). Los `cases/` ya son públicos en su repo. Avisa en tu `visitas/` al hacerlo.
- **Siguiente:** David prueba el micro en su iPhone; README en inglés y párrafo de entrega.

## 2026-11-15 23:53 — docs/stage-house-3d-for-raul — Claude Code
- **Hecho:** nota para Raúl al final de `02-DOCS/ftd/stage-casa-3d.md`: el 3D pasa a él, con tres caminos comparados.
- **Estado:** `bash check.sh` pasa (165). Solo documentación.
- **Decisiones:** a David el 3D actual le parece cutre (maqueta de formas simples, no como el vídeo). No pasa a ser lo
  normal tal como está; la página por defecto sigue en 2D.
- **Bloqueos:** ninguno.
- **Para Raúl:** **el 3D es tuyo desde ahora.** Lee la sección «Para Raúl» de la ficha y elige camino: pulir el 3D,
  imagen realista con cámara (el aspecto del vídeo, necesita una imagen generada) o quedarnos en 2D. Decisión el 17 a
  las 14:00 tras probar en el iPhone de David. Avisa en tu `visitas/raul.md` si lo coges o no.
- **Siguiente:** David sigue con la voz y la entrega (micro en iPhone, audio final, README, vídeo).

## 2026-11-15 23:32 — feat/stage-house-3d-camera — Claude Code
- **Hecho:** paso 3 de la casa 3D (sigue solo con `?house=3d`): la cámara. En `web/house3d.js`, una vista por parte
  (`VIEWS`); al cambiar el foco la cámara se desliza 0,9 s hasta esa parte y vuelve a la casa entera cuando no hay
  foco. Vale para el scroll por capítulos y para las preguntas (`turnHome`). `stage_page.html` no cambia.
- **Estado:** `bash check.sh` pasa (165). Navegador a 375×812 y 1280×800: las cinco partes con `goToPart` y una
  pregunta con `turnHome`. Consola sin errores de la página. **iPhone real sin probar.**
- **Decisiones:** solo se dibuja mientras la cámara se mueve. Dos deslizamientos a tirones (más de 45 ms por imagen)
  y la cámara pasa a saltar; más de 150 ms y vuelve la casa dibujada.
- **Bloqueos:** ninguno. `out/families/` sigue con páginas viejas (`finagent.run --all` para ver el 3D en todas).
- **Para Raúl:** el plan de la casa 3D está completo detrás del interruptor; el 17 se decide si pasa a ser lo normal.
- **Siguiente:** prueba en el iPhone de David; después, 3D por defecto en el modo completo si va bien.

## 2026-11-15 23:25 — feat/stage-house-3d-states — Claude Code
- **Hecho:** paso 2 de la casa 3D (sigue solo con `?house=3d`). `web/house3d.js` hace ya lo mismo que `paint()`:
  estados (grietas; roto = agujero en el tejado, ladrillo visto, fuga y charco, ramas secas), brillo de lo reparado,
  jardín que se seca con `lush` y partes sin foco en pálido. Una marca redonda por parte (✓ ! ✕) y tocar una parte
  lleva a su capítulo (`goToPart`).
- **Estado:** `bash check.sh` pasa (165). Navegador a 375×812: los cuatro estados, el foco y el toque, forzados a mano
  y con los datos de Samantha. Consola sin errores de la página. **iPhone real sin probar.**
- **Decisiones:** marcas en 3D aunque el plan decía «solo leyenda»: en el móvil la leyenda está oculta. Gotas quietas.
- **Bloqueos:** ninguno. `out/families/` sigue con páginas viejas: el 3D solo se ve en la portada hasta `run --all`.
- **Para Raúl:** en `stage_page.html` solo cambia una línea (`mount` recibe `onFail` y `onPick`).
- **Siguiente:** iPhone; PR 3: la cámara (scroll y `turnHome`).

## 2026-11-15 23:17 — feat/stage-house-3d-switch — Claude Code
- **Hecho:** primer paso de la casa 3D, solo con `?house=3d` (la página por defecto no cambia). `web/house3d.js`: casa
  quieta con las 5 partes, hecha con formas simples. `web/vendor/three.module.min.js`: three.js 0.170.0 dentro del repo
  (692 KB, MIT). `stage_page.html`: `tryHouse3d()` y una llamada al final de `paint()`. Un test en `test_stage.py`.
- **Estado:** `bash check.sh` pasa (165). Navegador, 375×812 y 1280×800: se ve la casa 3D; `?house=2d` vuelve al dibujo;
  si se pierde el contexto gráfico vuelve sola al dibujo. Consola sin errores de la página. **iPhone real sin probar.**
- **Decisiones:** nunca 3D en «Simply» ni con «reducir movimiento». Se dibuja solo cuando algo cambia (batería).
- **Bloqueos:** ninguno. Las páginas de `out/families/` son de antes: para ver ahí el 3D, `finagent.run --all`.
- **Para Raúl:** he tocado `stage_page.html` (`paint()`, arranque y un `<div id="house3d">` junto al SVG).
- **Para Samuel:** una línea en `server.py`: `app.mount("/web", …)` para servir `src/finagent/web/`.
- **Siguiente:** que David la vea en su iPhone; PR 2: estados, brillo, jardín y foco en 3D.

## 2026-11-15 23:00 — docs/stage-house-3d-plan — Claude Code
- **Hecho:** solo un plan, sin código: `02-DOCS/ftd/stage-casa-3d.md`. La casa pasa a 3D con la opción intermedia:
  casa 3D (three.js) + cámara que se desliza de parte en parte con el scroll y con `turnHome`. El resto de la
  página no cambia.
- **Estado:** `bash check.sh` pasa (164). No se ha tocado `stage_page.html`.
- **Decisiones:** la casa 2D se queda de respaldo (sin WebGL, a tirones, y siempre en «Simply»); three.js dentro del
  repo; todo detrás de `?house=3d`; **decisión el 17 nov a las 14:00** tras probar en iPhone; si no va, seguimos en 2D.
- **Bloqueos:** ninguno.
- **Para Raúl y Samuel:** leed la ficha antes de tocar la casa. Si ya estáis con ella o con `stage_page.html`,
  decidlo en vuestro `visitas/` antes del 16 por la mañana, que empiezo con el primer PR (`feat/stage-house-3d-*`).
- **Siguiente:** PR 1: three.js en el repo, interruptor y casa 3D quieta; primera prueba en el iPhone.

## 2026-11-15 22:30 — feat/stage-mobile-chat-sheet — Claude Code
- **Hecho:** en el móvil (≤860 px) el chat es una hoja en la mitad de abajo, bajo la casa (que ya es fija arriba),
  así se ve la casa girar al preguntar. Sugerencias en una fila que se desliza. `turnHome` salta a la casa sin
  animación: el desplazamiento suave se cancelaba con el del chat y la página se quedaba en la portada.
- **Estado:** `bash check.sh` pasa (164). Móvil (375×812): pregunta → la casa arriba con el jardín marcado y la
  respuesta abajo. Escritorio (1280×800): el panel lateral no cambia. iPhone real sin probar.
- **Decisiones:** solo CSS en el bloque `max-width: 860px` más una línea en `turnHome`.
- **Bloqueos:** ninguno. El cuelgue de `check.sh` de antes era la red (edge-tts), confirmado por David.
- **Para Raúl:** he tocado el CSS móvil del chat y `turnHome` en `stage_page.html`.
- **Siguiente:** que David lo vea en su iPhone; audio de ElevenLabs cuando los textos tengan el visto bueno.

## 2026-11-15 21:00 — feat/stage-after-the-choice — Claude Code
- **Hecho:** después de elegir un paso. (A) «Your first move, tomorrow»: una o dos acciones por paso, sin cifras ni
  marcas (`house.FIRST_MOVES`, `visual.data.first_moves`). (B) «Not yet» pregunta qué lo frenó (no sé por dónde
  empezar / cuesta más / no nos hemos puesto de acuerdo, o «no he tenido tiempo» si vive solo, o texto libre),
  responde a ese freno y lo guarda en `/follow-up` (`note`). (C) Aviso del día 3 con el nombre sencillo
  (`decision.plain_title`). (D) La ficha del asesor dice qué lo frenó y el título de Sherpas entre paréntesis.
- **Estado:** `bash check.sh` pasa (164). Recorrido en el navegador con Michael y los Weah: elegir, volver, «Not yet»,
  freno y ficha. Consola limpia. Móvil: sin desbordamiento; el bloque nuevo no lo he visto a ojo en móvil.
- **Decisiones:** las acciones son consejo práctico escrito por nosotros: genéricas, sin productos y con el asesor.
- **Bloqueos:** ninguno. Ojo: la página ya tenía `let chosenStep`; volver a declararla rompía todo el script y los
  tests no lo ven (no ejecutan JS). Mirad la consola tras tocar `stage_page.html`.
- **Para Samuel:** he tocado `sessions.decide` (guarda `plain_title`), `server.decision`, `brain` y `house`.
- **Para Raúl:** he tocado el final de `stage_page.html` (elección, vuelta a los 3 días y ficha).
- **Siguiente:** audio de ElevenLabs cuando los textos tengan el visto bueno.

## 2026-11-15 20:10 — feat/brain-ask-family-question — Claude Code
- **Hecho:** `/ask` contesta la pregunta de cada familia. `brain`: hecho `plan_goals` en `timeline` (los objetivos
  tal como los escribe Sherpas; la proyección ya los incluye: la deuda salta el año de la compra). `ask.py`:
  `off_plan` solo para lo ajeno al plan (tiempo, una acción, una moneda); «¿qué va primero?» → `intro`; «¿está
  pagada la universidad?» → ahorro; nunca «yes, you can afford it». Un test en `test_house.py`.
- **Estado:** `bash check.sh` pasa (159). Real (deepseek-flash, ~21 preguntas en total): «Can I afford the second
  home in 2030?» → «The plan already includes … $500,000 in 2030. On today's projection, your savings run out at 73»;
  Johnson «What comes first…?» → «Sherpas does not rank them…»; Bitcoin y el tiempo siguen `off_plan`.
- **Decisiones:** un objetivo en el plan no es un objetivo pagado: la respuesta dice lo que muestra el plan con él.
- **Bloqueos:** ninguno. Ojo: tras parar un `serve.sh` en segundo plano, uvicorn sigue vivo y ocupa el puerto.
- **Para Samuel:** he tocado el `SYSTEM_PROMPT` de `ask.py` (paso 1) y `_timeline` en `brain.py`. Contrato igual.
- **Siguiente:** audio de ElevenLabs de la narración cuando los textos tengan el visto bueno.

## 2026-11-15 19:20 — feat/brain-narration-plain-couples — Claude Code
- **Hecho:** igual que con Samantha y Michael, narración completa de los Weah y los Johnson reescrita a mano (13
  escenas cada una). Intro con su pregunta: Weah, a dónde va el efectivo que sobra; Johnson, universidad y retiro
  tiran de los mismos $15,032 y Sherpas no los ordena.
- **Estado:** `bash check.sh` pasa (158). Las 26 escenas aceptadas por `guard`. Palabras: 664 → 463 y 608 → 449;
  voz Edge: 182 s y 179 s.
- **Decisiones:** las dos frases dudosas de los Johnson, resueltas: fuera «largest single jump»; la condición del
  `timeline` ahora es la de Sherpas («leans on your savings for about half»). Cimientos de los Johnson: «marked
  solid, yet the cushion itself is thin» ($19,000 frente a 8-9 meses), antes decía «real protection».
- **Bloqueos:** ninguno.
- **Para Samuel:** 26 textos tuyos más; léelos. Modo sencillo sin tocar en las cuatro familias.
- **Siguiente:** audio de ElevenLabs de las cuatro familias cuando deis el visto bueno a los textos.

## 2026-11-15 18:40 — feat/brain-narration-plain — Claude Code
- **Hecho:** narración completa de Samantha y Michael (las del pitch) reescrita a mano: frases cortas, una idea por
  parte, sin «X out of Y points» (ya está en pantalla), sin decimales ni cifras que no aportan. La intro abre con su
  pregunta (Samantha: 82 «strong» pero sin ahorros a los 73; Michael: casa en 2027 y retiro a los 58).
- **Estado:** `bash check.sh` pasa (158). Las 20 escenas aceptadas por `guard`. Palabras: 509 → 364 y 411 → 364;
  voz Edge: 134 s y 143 s. Cada frase comparada con las observaciones de Sherpas de esa escena.
- **Decisiones:** modo sencillo, Weah y Johnson sin tocar. `model` sigue diciendo `deepseek-flash`.
- **Bloqueos:** ninguno.
- **Para Samuel:** he cambiado 20 textos tuyos; léelos y cambia lo que no te guste. El paso 2 de Michael ya no cita
  $10,300 (no está claro si «cutting withdrawals to $10,300/year» es el nuevo retiro o la rebaja).
- **Siguiente:** lo mismo con Weah y Johnson; audio de ElevenLabs cuando los textos estén aprobados.

## 2026-11-15 18:00 — feat/stage-plain-steps — Claude Code
- **Hecho:** los pasos se ven en palabras de la familia: `house.plain_title` («Raise mortality coverage» → «Add more life
  insurance»), `brain` lo pasa en `visual.data.plain_title` (y `plain_moves` en `all_moves`), la página lo usa en la
  tarjeta, en «Which one do you start with?» y en «Chosen: …». «high effort» → «More work». El `action` de Sherpas
  queda plegado en «What your plan says, word for word». Dos tests en `test_house.py`.
- **Estado:** `bash check.sh` pasa (158 tests). Visto en el navegador (Michael y Samantha, `run --all` con Edge).
- **Decisiones:** sin cifras en los títulos llanos; `scene.title` sigue siendo el de Sherpas (decisión y ficha del asesor).
- **Bloqueos:** ninguno. Venía de una auditoría hecha sobre el servidor viejo del 8000; la web nueva está en el 8001.
- **Para Samuel:** he tocado `brain.py` (dos claves nuevas en `visual.data`) y `house.py`. El contrato no cambia.
- **Para Raúl:** he tocado `stage_page.html` (tarjeta de paso, botones del final y nota de elección).
- **Siguiente:** frases de la narración más cortas y sin cifras que no aportan, si Samuel está de acuerdo.

## 2026-11-15 16:45 — fix/ask-iphone-voice — Claude Code
- **Hecho:** `/ask/stream` empieza con un comentario de 2 KB (`STREAM_PADDING` en `server.py`) para que Safari entregue
  el evento `thinking` al momento. En `stage_page.html` y `chat_page.html`: el `click` que sigue a un toque ya no cuenta
  como segundo toque, y «mantener pulsado» pasa de 0,6 s a 1 s. `tests/test_family_experience.py` ignora el comentario.
- **Estado:** `bash check.sh` pasa (150 tests). Chromium por el enlace público: toque/toque envía una sola grabación y
  el texto de la pregunta sale en 1,0 s. **Sin confirmar en iPhone**: son hipótesis a partir de los tiempos de David.
- **Decisiones:** medido con el iPhone de David: el servidor responde en 0,5-0,8 s, pero él veía «…» varios segundos, y
  5 de 7 grabaciones llegaron de menos de 1 s y sin palabras (422).
- **Bloqueos:** ninguno.
- **Para Samuel:** he tocado `server.py` (4 líneas) y un test tuyo. El relleno es un comentario SSE: la página lo ignora.
- **Para Raúl:** otra vez el bloque del micrófono de la escena.
- **Siguiente:** que David repita la prueba en el iPhone.

## 2026-11-15 16:20 — fix/stage-tap-to-talk — Claude Code
- **Hecho:** el micrófono pasa de «mantener pulsado» a «tocar para hablar» en `stage_page.html` y `chat_page.html`: un
  toque empieza, otro envía; mantener pulsado (≥0,6 s) y soltar sigue valiendo. Se envía solo a los 30 s. El archivo
  lleva la extensión real de la grabación (`.webm`, `.mp4` en iPhone, `.ogg`).
- **Estado:** `bash check.sh` pasa (150 tests). En Chromium con un micrófono simulado: toque/toque y mantener/soltar
  envían la grabación. **Sin probar en un móvil real.**
- **Decisiones:** David lo probó: en el móvil no funcionaba de ninguna forma y en el ordenador solo manteniendo. Las
  grabaciones llegaban al servidor sin voz (422): se cortaban al soltar, al salirse el dedo o al salir el permiso.
- **Bloqueos:** ninguno.
- **Para Raúl y Samuel:** he tocado la escena (solo el bloque del micrófono y su etiqueta). Si preferís otro gesto, cambiadlo.
- **Siguiente:** que David lo pruebe en el móvil por el enlace público.

## 2026-11-15 15:50 — feat/voice-daily-cap — Claude Code
- **Hecho:** tope diario de caracteres enviados a ElevenLabs: `ELEVEN_MAX_CHARS_PER_DAY` (por defecto 20000) en
  `voice_eleven.py`. Suma pipeline y respuestas en directo; la cuenta va en `out/voice_cache/usage.json` y empieza de
  cero cada día. Dos tests nuevos, `VOICE.md` y `.env.example` al día.
- **Estado:** `bash check.sh` pasa (150 tests). Real: una respuesta por el enlace público sumó 237 caracteres; con el
  tope a 1, la siguiente salió por edge-tts sin enviar nada.
- **Decisiones:** por encima del tope la voz cae a edge-tts (lo ya en caché sigue sonando con ElevenLabs).
- **Bloqueos:** micrófono real sin probar.
- **Para Samuel:** regenerar las cuatro familias en los dos modos puede pasar de 20000: súbelo en `.env` ese día.
- **Siguiente:** probar el micrófono por el enlace; regenerar el audio cuando los textos tengan el visto bueno.

## 2026-11-15 15:27 — fix/serve-share-windows — Claude Code
- **Hecho:** `scripts/serve.sh` arranca en Windows (`PYTHONPATH` con `;`, igual que `check.sh`). `scripts/share.sh` usa
  `cloudflared` si está instalado y, si no, `localhost.run` (ahora contra `127.0.0.1`). `BACKEND.md`: una línea.
- **Estado:** `bash check.sh` pasa (148 tests). Real, por el enlace de `share.sh`: pregunta en 4,3 s y su mp3 en 0,9 s.
- **Decisiones:** el enlace público sale del ordenador de David con su clave de ElevenLabs (`VOICE_ENGINE=eleven` solo en
  ese proceso), así todos oyen a Matilda sin tener la clave. `localhost.run` daba ~5 KB/s: la voz se cortaba.
- **Bloqueos:** micrófono real sin probar. El audio de las respuestas no tiene tope global de caracteres.
- **Para Samuel:** he tocado tus dos scripts y una línea de `BACKEND.md`; en Windows `serve.sh` daba «No module named
  'finagent'» y el túnel de `share.sh` respondía «no tunnel». Sin probar en Linux/Mac ni la rama de `localhost.run`.
- **Siguiente:** pasar el enlace al equipo para probar el micrófono; tope diario de caracteres en `voice.py`.

## 2026-11-15 — docs/voice-readme — Claude Code
- **Hecho:** `VOICE.md` (en inglés, para jurado y mentores): qué hace la voz, cómo ejecutarla con y sin clave, motores y
  respaldos, protecciones de gasto, variables de `.env`, cómo se leen las cifras y cómo usarla desde `/ask`.
  `README.md`: una línea que enlaza a `VOICE.md`. `.env.example`: `ELEVEN_STT_MODEL` y `VOICE_CACHE_DIR`.
- **Estado:** `bash check.sh` pasa. Comandos del documento probados (PowerShell, mock, eleven) y ejemplos de la tabla verificados.
- **Decisiones:** la voz se documenta aparte para no chocar con el README final, que reescribiremos entre los tres.
- **Bloqueos:** ninguno.
- **Para Samuel y Raúl:** al rehacer el README de la entrega, enlazad `VOICE.md` en vez de copiarlo.
- **Siguiente:** probar el recorrido entero cuando existan `/ask` y el micrófono.

## 2026-11-15 — feat/voice-stt — Claude Code
- **Hecho:** `voice.transcribe_async(audio, filename)` → `Transcript(text, engine)`: la pregunta hablada a texto con
  ElevenLabs Scribe (mismas claves que la voz). Acepta webm/ogg/mp3/wav/m4a. Tests y ficha `voz-stt.md`.
- **Estado:** `bash check.sh` pasa. Real: mp3 y webm/Opus transcritos bien en 0,6–0,8 s.
- **Decisiones:** nunca lanza error: si falla o hay silencio, `text=None` y la página pide escribir la pregunta.
- **Bloqueos:** falta probarlo con una grabación real del micrófono en la página.
- **Para Samuel:** en `/ask` (FastAPI, `UploadFile`): `heard = await voice.transcribe_async(await file.read(), file.filename)`;
  si `heard.text` es `None`, devuelve un error amable. Luego LLM → guard → `voice.speak_async(answer)`.
- **Para Raúl:** graba con `MediaRecorder` (webm por defecto) y manda el archivo tal cual a `/ask` como formulario
  (`multipart/form-data`, campo `file`). No hace falta convertir nada.
- **Siguiente:** probar el recorrido entero cuando existan `/ask` y el micrófono de la página.

## 2026-11-15 — feat/voice-speak — Claude Code
- **Hecho:** `voice.speak_async(text)` / `voice.speak(text)` → `SpokenAudio(audio, duration_s, engine)`: un texto a MP3
  para las respuestas de `/ask`. Mismos motores, respaldos, `to_speech` y caché. Tests y ficha `voz-respuestas.md`.
- **Estado:** `bash check.sh` pasa. Real: 196 caracteres con ElevenLabs en 0,78 s; repetida, 0,005 s (caché).
- **Decisiones:** nunca lanza error: sin motor, `audio=None` y se muestra el texto.
- **Bloqueos:** ninguno.
- **Para Samuel:** en tu ruta `/ask`: `spoken = await voice.speak_async(answer)` y devuelve
  `Response(spoken.audio, media_type="audio/mpeg")` (si `spoken.audio` es `None`, solo texto). No uses `voice.speak` ahí.
- **Para Raúl:** el audio de la respuesta llega como MP3 en la respuesta de `/ask`; hablemos de cómo grabas el micrófono.
- **Siguiente:** STT (voz de la familia → texto) cuando sepamos cómo graba Raúl.

## 2026-11-15 — feat/voice-elevenlabs — Claude Code
- **Hecho:** `voice_eleven.py` + `VOICE_ENGINE=eleven` en `voice.py` (respaldo eleven → edge → mock). Caché en
  `out/voice_cache/` (mismo texto y voz = no se paga dos veces) y tope `ELEVEN_MAX_CHARS`. Voz: **Matilda**. Ficha `voz-elevenlabs.md`.
- **Estado:** `bash check.sh` pasa (75 tests). Probado de verdad: Samantha entera, 10 escenas, 70 s.
- **Decisiones:** ElevenLabs va con mi cuenta de estudiante (`ELEVENLABS_API_KEY`, gratis, 130 k caracteres/mes), no
  con los $1,40 del equipo (quedan de reserva por el proxy). Sin dependencias: `urllib`. Edge sigue por defecto.
- **Bloqueos:** ninguno.
- **Para Samuel:** ya no necesito `openai` para la voz; añádelo tú con el primer LLM. Backend: me encaja FastAPI con `/ask`.
- **Para Samuel y Raúl:** la clave es personal: el audio ElevenLabs de la demo lo genero yo; vosotros seguid con edge.
- **Siguiente:** las cuatro familias con ElevenLabs para la demo; voz de las respuestas de `/ask`.

## 2026-11-14 — feat/voice-normalization — Claude Code
- **Hecho:** `speech_text.py` (`to_speech`): reescribe el texto como se dice en voz alta (markdown fuera, `/yr` → «a
  year», `-$8,336` → «minus», `$1M`, rangos, `22/30`, fechas ISO, `401(k)`, `529`, siglas y tickers). `voice.py` lo
  aplica antes del TTS. Tests y `scripts/voice_listen_test.py` (antes/después en `out/listen/`). Ficha `voz-normalizacion.md`.
- **Estado:** `bash check.sh` pasa (37 tests). Ninguna cifra cambia en los 312 textos de los cuatro casos.
- **Decisiones:** `narration` no se toca (`guard` y subtítulos usan el original); sin LLM; nunca se redondea.
- **Bloqueos:** ninguno.
- **Para Samuel:** la narración puede traer markdown y formatos de `narrative` tal cual: la voz los adapta. Confirmo
  que `openai` no está en `requirements.txt` (nunca lo estuvo); habrá que añadirlo con el primer LLM.
- **Siguiente:** motor ElevenLabs (fase 3). Siglas comprobadas transcribiendo el audio con Whisper (ver ficha).

## 2026-11-13 — docs/under-one-roof — Claude Code
- **Hecho:** `nota-idea.md` con la versión final de la nota (más humana, descartadas resumidas, apartado nuevo
  «Why a phone, and what else we said no to»). `ideas.md`: nombre nuevo de la idea.
- **Estado:** `./check.sh` pasa. Solo documentación.
- **Decisiones:** la idea se llama **Under One Roof** (*One plan. One home. Everyone in it.*), antes «The House That
  Listens». Al empezar, cada persona elige su modo: sencillo (botones grandes, voz guía, mantener pulsado para
  hablar) o completo (explorar todas las cifras).
- **Bloqueos:** ninguno.
- **Para Samuel y Raúl:** la nota se envía hoy antes de las 22:00 pegando el texto de debajo de la línea con `/idea`.
- **Siguiente:** enviar la nota y repartir el MVP.

## 2026-11-13 — docs/idea-note — Claude Code
- **Hecho:** `nota-idea.md`, la nota de `/idea` en inglés con la idea elegida, «The House That Listens»
  (qué construimos, por qué según la rúbrica, 7 ideas descartadas con su motivo, riesgos). En `ideas.md`,
  la tabla de votos pasa a «Idea elegida».
- **Estado:** `./check.sh` pasa. Solo documentación.
- **Decisiones:** **idea elegida por los tres: The House That Listens** (fusión de S1 + R1, con modo sencillo por
  defecto). Sin votación: estamos de acuerdo.
- **Bloqueos:** ninguno.
- **Para Samuel y Raúl:** si queréis retocar el texto, editad `nota-idea.md`; quien la envíe pega el texto de
  debajo de la línea en Discord con `/idea` antes de hoy a las 22:00.
- **Siguiente:** enviar la nota y repartir el trabajo del MVP.

## 2026-11-13 — docs/david-fusion-vote — Claude Code
- **Hecho:** `idea-david.md` (sección «Actualización 13 nov») e `ideas.md` (sección D1 y mi columna de votos):
  propongo fusionar S1 + R1 como «the house that listens».
- **Estado:** `./check.sh` pasa. Solo documentación.
- **Decisiones:** mi voto: fusión S1 + R1 > S1 > R1. Tres añadidos: la interrupción de R1 en el centro (sin ella es
  un tour), **modo sencillo por defecto** para gente poco digital (2D, botón Next, micrófono tipo audio de WhatsApp)
  con S1 como modo explorar, y **personal de verdad** (una casa distinta por familia; cada persona ve su parte).
- **Bloqueos:** ninguno.
- **Para Samuel y Raúl:** ¿os vale como idea común? Si sí, redactamos hoy la nota de `/idea` (22:00). Todas las
  cifras de la propuesta salen de `persona.md` y de los JSON de `cases/`.
- **Siguiente:** acordar la idea y escribir la nota.

## 2026-11-12 18:00 — docs/idea-david — Claude Code
- **Hecho:** `idea-david.md`, mi propuesta de idea: **Your Financial Home** (el plan como la casa de la familia;
  cada parte de la casa es un pilar de la nota). Incluye las ideas que descarté y por qué, para la nota del viernes.
  PR #5 (`visitas/`) fusionado por mí, como pidió Samuel.
- **Estado:** `./check.sh` pasa (4 tests). Solo documentación.
- **Decisiones:** la fase 2 de la voz (normalización en inglés) queda aparcada hasta elegir la idea entre los tres.
- **Bloqueos:** ninguno.
- **Para Samuel y Raúl:** leed `idea-david.md`; cada uno trae la suya y elegimos la mejor antes del vie 13, 22:00.
  Datos comprobados en `cases/`: en los Weah las acciones sueltas casi no mueven la nota (60→62); solo combinadas
  llegan a 73 y 78.
- **Siguiente:** votar la idea en equipo y redactar la nota de `/idea`.

## 2026-11-12 (tarde) · David (`daviid-sc`) · Ya no hace falta permiso de Samuel para subir

- **PR #3 (`check.sh` en Windows) fusionado en `main`.** `./check.sh` funciona en Windows tal cual.
- `CLAUDE.md` (rama `docs/equal-team-push`): se quita "No hacer push sin permiso de Samuel".
  Acordado por los tres: **trabajamos de igual a igual**. Cada uno sube sus ramas y fusiona sus
  PRs cuando `./check.sh` pasa. Sigue prohibido el push directo o force-push a `main`, y los
  cambios en archivos de otro o en el contrato se avisan antes y se anotan aquí.
- `02-DOCS/ftd/voz-edge-tts.md`: actualizada (ya no espera el OK de Samuel; `check.sh` OK en Windows).

## 2026-11-12 (tarde) · David (`daviid-sc`) · Arreglo de `check.sh` en Windows

- **PR #1 (voz) y PR #2 (este archivo) ya están fusionados en `main`.** Tras `git pull`:
  `pip install -r requirements.txt` (añade `edge-tts` y `python-dotenv`).
- Rama `fix/windows-check` (PR #3). Toca dos archivos compartidos (no son de voz), con el OK de
  David; **en Linux/macOS no cambia nada**:
  - `check.sh`: en Windows (Git Bash) usa `;` como separador de `PYTHONPATH`, porque el Python
    de Windows no entiende `:`. Antes fallaba con `No module named 'finagent'`.
  - `tests/test_pipeline.py`: las 4 lecturas con `read_text()` ahora llevan `encoding="utf-8"`.
    En Windows la codificación por defecto es cp1252 y rompía textos con tildes ("Pérez").
- Resultado: **`./check.sh` funciona tal cual en Windows** (Git Bash), sin `PYTHONUTF8=1`.
  Comprobado: 4 tests pasan y `OK -> out/index.html`.
- Consejo para todos: al leer o escribir archivos de texto en Python, poner siempre
  `encoding="utf-8"`; si no, funciona en Linux y falla en Windows (Raúl y David).

## 2026-11-12 · David (`daviid-sc`) · Voz

### PR #1 — `feat/voice-edge-tts`: voz real con edge-tts
https://github.com/Inmortal112/finagent-sherpas/pull/1

- `src/finagent/voice.py`: sustituye el mock por TTS real con **edge-tts** (voces neuronales de
  Microsoft, gratis, sin clave). Genera un MP3 por escena en `out/audio/` y rellena `audio_path`
  (relativo a `out_dir`) y `duration_s` (medida del archivo). **No toca `narration`** y la firma
  `synthesize(presentation, out_dir) -> Presentation` no cambia.
- Si la síntesis falla (sin internet, etc.), usa duraciones estimadas: `main` nunca se rompe.
- Voz según `Presentation.language`: `en` → `en-US-EmmaMultilingualNeural`, `es` →
  `es-ES-ElviraNeural`. Como el producto va en inglés, **brain debe generar `language="en"`**.
- **Afecta a todos:**
  - `requirements.txt`: añade `edge-tts` y `python-dotenv`. Tras fusionar:
    `pip install -r requirements.txt`.
  - `.env.example`: se mantiene el bloque de Samuel (`MCP_URL`, `MCP_TOKEN`, `LLM_PROXY_URL`,
    `TEAM_KEY`) y se añaden `VOICE_ENGINE` y `VOICE_NAME` (opcionales). Hubo conflicto con
    `main` y ya está resuelto (merge de `main` en la rama).
- Comprobado: 4 tests pasan y `python -m finagent.run` genera `out/index.html`.

### Plan de la voz (próximos pasos)
1. **Normalización en inglés**: preparar el texto para que cifras y monedas se lean bien
   (p. ej. `$550,000` → "five hundred fifty thousand dollars"). Sin cambiar ninguna cifra.
2. **ElevenLabs para la demo** vía el proxy (`eleven-flash-v2.5`, $0.04/1000 caracteres).
   **Tope de ElevenLabs: $1,40 para todo el equipo** → en desarrollo se usa edge-tts (gratis) y
   ElevenLabs solo para generar el audio final. Por favor, que nadie lo gaste en pruebas.
3. Pausas, ritmo y elección final de voz.

### Avisos para el equipo
- **El repo es privado**, pero el brief de Sherpas pide que sea **público** para que mentores y
  jurado puedan abrirlo. Hay que decidirlo los tres antes de la entrega (18/11, 23:59).
  Los casos ya son públicos en el repo de Sherpas, así que no hay datos secretos en `cases/`.
- `fixtures/diagnostic_sample.json` sigue siendo el inventado; ya están los casos reales en `cases/`.
- ~~`check.sh` no funciona en Windows~~ → arreglado en PR #3 (ver entrada de arriba).
- ~~`CLAUDE.md` del repo dice "No hacer push sin permiso de Samuel"~~ → cambiado (ver entrada de arriba).
- Propuesta: añadir a `AGENTS.md` una línea tipo "Leer `comunicacion.md` al empezar" para que
  todas las IA lo carguen solas. No la he añadido: `AGENTS.md` es compartido.
