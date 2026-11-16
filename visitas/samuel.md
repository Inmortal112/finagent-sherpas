# Visitas — Samuel (cerebro: `brain.py`, `guard.py`)

## 2026-11-17 — chore/repo-cleanup — Claude Code
- **Hecho:** limpieza para la entrega. Borrado `examples/voice/` (ejemplo Node de Sherpas, sin uso) y 3 capturas
  duplicadas. Movidos a `02-DOCS/ideas/`: `ideas.md`, `idea-david.md`, `idea-raul.md`, `nota-idea.md` y
  `escalabilidad.md`. `BRIEF.md` → `02-DOCS/brief.md` (imágenes en `02-DOCS/brief-assets/`). Enlaces corregidos.
- **Render:** https://finagent-sherpas.onrender.com funciona: 8 páginas, audio edge real, `/ask` responde con voz.
  Enlace ya en `SUBMISSION.md` (falta el del vídeo).
- **Estado:** `./check.sh` pasa (219). 0 enlaces rotos en los `.md`. Ficha `limpieza-repo.md`.
- **Para David y Raúl:** vuestros `idea-*.md` están ahora en `02-DOCS/ideas/`; el contenido no ha cambiado.
- **Siguiente:** grabar el vídeo de 2 min y poner su enlace en `SUBMISSION.md`.

## 2026-11-17 — feat/deploy-dockerfile — Claude Code
- **Hecho:** el `Dockerfile` genera las 8 páginas con voz edge (`VOICE_ENGINE=edge … run --all`), no una sola con
  mock. Línea en `BACKEND.md`. Ficha `despliegue-dockerfile.md`.
- **Estado:** `./check.sh` pasa (218). Simulado sin `.env` y con caché vacía: 8 páginas, 204 mp3 reales, 1 min 15 s.
  `docker build` sin probar (no hay Docker aquí): lo comprobará Render.
- **Decisiones:** edge y no Matilda en la imagen: gratis, sin claves en el build y sin tocar el tope de ElevenLabs.
- **Para David:** si quieres Matilda en el enlace público, habría que subir su audio o generarlo en Render (gasta).
- **Siguiente:** crear el Web Service en Render (runtime Docker) y poner el enlace en `SUBMISSION.md`.

## 2026-11-16 11:40 — feat/stage-house-3d-default — Claude Code
- **Hecho:** la casa 3D nueva (PR #59: casa moderna, cielo según la puntuación, reparación animada) sale **por defecto**
  en el modo completo. `?house=2d` la apaga. Fichas `stage-casa-que-mejora.md` y `stage-casa-3d.md` actualizadas.
- **Estado:** `./check.sh` pasa (167). Navegador sin interfaz: completo → 3D; `?house=2d` y «Simply» → 2D; sin errores.
- **Decisiones:** se adelanta la decisión del 17 a las 14:00 para que todos veáis la casa nueva sin tocar la dirección.
  Respaldo 2D intacto: «Simply», sin WebGL, «reducir movimiento» o móvil lento.
- **Bloqueos:** falta el iPhone de verdad.
- **Para David y Raúl:** para verla: `git pull`, regenerar `out/` (`PYTHONPATH=src:. .venv/bin/python -m finagent.run --all`;
  sin voz nueva si los textos no cambian) y reiniciar `scripts/serve.sh`. **David:** pruébala en tu iPhone; si va
  lenta o falla, decidlo y volvemos al 2D por defecto (una línea: `wanted = wanted || "3d"` en `tryHouse3d`).
- **Siguiente:** prueba en iPhone antes del 17 a las 14:00.

## 2026-11-16 11:30 — feat/stage-house-heals — Claude Code
- **Hecho:** la casa mejora cuando la familia hace los pasos. Cada paso tiene «I've done this»: repara su parte, la
  puntuación sube con animación (+N) y, en 3D, las grietas se cierran con chispas y el cielo pasa de gris con lluvia a
  atardecer dorado según la puntuación. 3D al estilo del vídeo: pantalla completa, intro desde las nubes con el scroll,
  colinas, árboles, sombras y ventanas encendidas. Ficha `stage-casa-que-mejora.md`.
- **Estado:** `./check.sh` pasa (167). Navegador sin interfaz: 3 familias, escritorio y móvil, sin errores en consola.
- **Decisiones:** avanzar es hacer: en el paso N cuentan como hechos los anteriores y el botón hace el actual, así
  que la puntuación sube al bajar por la página. Puntuación = la mayor cifra de Sherpas para lo hecho (un paso o
  `all_moves`), nunca una suma ni una bajada. Casa 3D nueva: moderna minimalista (volúmenes blancos, cubiertas planas,
  ventanales, piscina = fontanería, zócalo = cimientos), con mucho más movimiento. Sigue detrás de `?house=3d`.
- **Bloqueos:** falta probarlo en un iPhone real (rendimiento).
- **Para Raúl:** he tocado `stage_page.html` (botón por paso, `achieved()`, `frame3d()`, estilos `body.h3d`) y he
  reescrito `web/house3d.js` (misma entrada más `health`, `setFrame` y `setIntro`).
- **Para David:** ningún texto narrado cambia. El «Yes, I started» del día 3 ahora también sube la puntuación.
- **Siguiente:** probarlo en el iPhone de David antes de la decisión del 17 a las 14:00.

## 2026-11-16 01:40 — feat/stage-family-worries — Claude Code
- **Hecho:** los botones bajo «What worries you most?» son ahora tres por familia, sacados de las «Objective
  concerns» de su `persona.md` (`house.WORRIES` → `intro.visual.data.worries`). Ficha `stage-preocupaciones-familia.md`.
- **Estado:** `./check.sh` pasa (167). Navegador y modelo real: las 12 frases llevan a su parte de la casa.
- **Decisiones:** `persona.md` no recoge ninguna preocupación dicha por las familias, así que son sugerencias
  del plan, no «lo que dijeron». Descartado por ahora el campo para que el asesor la escriba.
- **Bloqueos:** ninguno.
- **Para Raúl:** toqué una línea de `stage_page.html` (los botones de `worryChips` leen `data.worries`; sin ese
  dato salen los cuatro de antes).
- **Para David:** ningún texto narrado cambia. `out/` regenerado en mi máquina (8 páginas, 105 mp3).
- **Siguiente:** Samuel monta Render el 16 (antes hay que cambiar el `Dockerfile` a `run --all` con voz).

## 2026-11-16 00:55 — fix/brain-ask-partial-paydown — Claude Code
- **Hecho:** `/ask` ya no dice que pagar $6,800 «salda» la tarjeta de los Weah. El paso lleva un hecho nuevo (el
  saldo de hoy, $18,000) y `guard.claims_debt_cleared` rechaza «clears / pays off…» en ese paso. Ficha
  `brain-ask-pago-parcial.md`.
- **Estado:** `./check.sh` pasa (166). Modelo real: 6 de 6 respuestas correctas.
- **Decisiones:** no se calcula «lo que queda» ($11,200): se dan las dos cifras de Sherpas y «the rest is still owed».
- **Bloqueos:** ninguno. Gasto del equipo: $0.63 de $50 (caduca el 21 nov).
- **Para David:** ningún texto guardado cambia; el audio sigue valiendo.
- **Para Raúl:** `visual.data.pays_part_of_debt` es nuevo en los pasos (true solo en `move_1` de los Weah), por si
  la página quiere dibujar la pared «reparada a medias».
- **Siguiente:** decidir dónde se aloja la web para la entrega.

## 2026-11-16 00:20 — docs/readme-project-overview — Claude Code — README del proyecto
- **Hecho:** `README.md` reescrito en inglés: qué es Under One Roof, en qué se basa (pilar → parte de la casa) y
  cómo funciona. Arreglado un test que fallaba de 00:00 a 01:00: `/reminders` usaba el día local y las fechas
  guardadas son UTC. Ficha `readme-proyecto.md`.
- **Estado:** `./check.sh` pasa (165). Antes del arreglo fallaba 1 test en `main` a esa hora.
- **Decisiones:** el README resume y enlaza a `STAGE.md`, `BACKEND.md` y `VOICE.md`; no los repite.
- **Bloqueos:** el repo sigue privado; lo cambia Samuel.
- **Para David:** el README en inglés ya está; queda el párrafo de entrega. Revísalo si quieres cambiar algo de la voz.
- **Para Raúl:** sigue pendiente tu decisión sobre la casa 3D (el 17 a las 14:00).
- **Siguiente:** hacer público el repo; párrafo de entrega; prueba en iPhone real.

## 2026-11-15 — feat/stage-full-integration — Claude Code — web completa comprobada
- **Hecho:** unida `feat/stage-full-experience` con `main`. Visita entera recorrida con Playwright (13 pasos, móvil):
  familia, persona, modo, preocupación, chat con seguimiento, recarga, paso, vuelta a los 3 días y ficha del
  asesor. Ficha `verificacion-web-completa.md`.
- **Estado:** `./check.sh` pasa (153 tests). `run --all`: 8 páginas y 92 mp3. Cero errores de consola.
- **Decisiones:** narración sencilla de `pillar_debt` de los Weah reescrita a mano (era la plantilla). Regla nueva
  en las instrucciones de `/ask`: un paso hace solo lo que dicen sus hechos.
- **Bloqueos:** el puerto 8000 lo ocupa un servidor viejo (pid 398275) con el mock antiguo; la web buena está en
  el 8001. Lo tiene que parar Samuel.
- **Para David:** cambia un texto más del modo sencillo (`timothy-melanie-weah` `pillar_debt`).
- **Siguiente:** que Samuel recorra la web. Pendiente: a veces `/ask` dice que pagar $6,800 «salda» la tarjeta.

## 2026-11-15 — fix/narration-part-score — Claude Code
- **Hecho:** leídos los textos del pitch (Samantha y Michael, dos modos) y los pasos, personas y línea del tiempo
  de Weah y Johnson. Corregidas dos frases a mano. `guard.part_scored_out_of_100` (nuevo): rechaza «roof score …
  out of 100». Ficha `narracion-revision-pitch.md`.
- **Estado:** `./check.sh` pasa (151 tests).
- **Decisiones:** solo la nota global es sobre 100; una parte de la casa con nota sobre 100 es siempre un error
  (Michael, modo sencillo: «lifts your roof score to 31 out of 100»). La regla vale también para `/ask`.
- **Bloqueos:** ninguno. Dos frases dudosas de los Johnson sin tocar (ver la ficha): decide Samuel.
- **Para David:** cambian dos textos del modo sencillo (`michael-carter` `move_1`, `samantha-lewis`
  `pillar_investments`): su audio guardado ya no vale.
- **Siguiente:** comprobar la página completa cuando la otra sesión termine `feat/stage-full-experience`.

## 2026-11-15 — feat/stage-full-experience — Claude Code — la experiencia entera en la página
- **Hecho:** `finagent.run --all` genera `out/families/<familia>/<modo>/` (página y voz) para las cuatro familias en
  los dos modos. La página (`stage_page.html`) añade: modo «Simply / In full», «I am …» en parejas, «What worries
  you most?» antes del recorrido, volver a los 3 días con el seguimiento (la parte queda reparada), la nota del
  asesor en un panel y el chat que recupera sus respuestas al recargar. Guía en inglés: `STAGE.md`.
- **Estado:** `./check.sh` pasa (152 tests). Recorrido entero probado en Chromium con el servidor real.
- **Decisiones:** cambiar de familia o de modo navega a su página generada (con voz); si no existe, se redibuja con
  `/presentation` (sin voz de narración). La sesión, la persona y el sonido se guardan en el navegador.
- **Bloqueos:** micrófono e iPhone real sin probar. `out/` no está en git: tras clonar, `finagent.run --all`.
- **Para Raúl:** todo sigue siendo un punto de partida para tu etapa; `STAGE.md` explica cómo está hecho.
- **Para David:** tus cambios del micrófono (tocar para hablar, iPhone) siguen intactos. La narración usa Edge.
- **Siguiente:** que Samuel la recorra entera y diga qué cambiar; ensayo con móvil real.

## 2026-11-15 — feat/stage-integration — Claude Code — primera web comprobada
- **Hecho:** unidas la casa interactiva (`feat/stage-house-journey`) y `main` (con el resumen del historial en
  `/ask`). Comprobación de extremo a extremo en `02-DOCS/ftd/verificacion-primera-web.md`. Sin cambios de código.
- **Estado:** `./check.sh` pasa (148 tests). Servidor real: página, chat, cuatro familias en dos modos, pregunta
  y seguimiento por `/ask/stream`, decisión, ficha del asesor, aviso del día 3 y audio: todo responde.
- **Decisiones:** la web se ve con `scripts/serve.sh` → http://localhost:8000 (la casa) y `/chat` (prueba).
- **Bloqueos:** ninguno. A mirar a ojo: en mis capturas el anillo de la nota marcaba 36, no 82 (parece la
  animación a medias). Sin probar: deslizar, chat dentro de la página, micrófono, iPhone.
- **Para Raúl:** la escena real ya está en `main`: ábrela y di qué cambiar.
- **Siguiente:** que Samuel la recorra en el navegador; después, modo sencillo y elegir persona en la página.

## 2026-11-15 — feat/brain-ask-summary — Claude Code
- **Hecho:** `/ask` recuerda la conversación. `sessions.context_for` monta un resumen de la sesión (preocupaciones,
  partes más preguntadas, paso elegido, **sin cifras**) más el último turno literal; `ask.answer(context=…)` lo
  envía al modelo. `tests/test_ask_context.py`. `escalabilidad.md` y `BACKEND.md` al día. Ficha
  `brain-ask-resumen-historial.md`.
- **Estado:** `./check.sh` pasa (141 tests). Real: «Why does my garden dry up?» → «and what can I do about it?»
  se queda en el jardín (`move_3`); antes iba al seguro de hogar. Respuestas en 1,0-6,2 s.
- **Decisiones:** el resumen se calcula al preguntar, no se guarda; tamaño fijo; `guard` sigue decidiendo.
  `ASK_HISTORY=off` lo desactiva. La primera pregunta de una sesión no cambia.
- **Bloqueos:** ninguno.
- **Para Raúl y David:** la forma de `/ask`, `/ask/stream` y sus eventos no cambia. Mandad siempre el `session_id`.
- **Siguiente:** comprobar la casa interactiva de extremo a extremo.


## 2026-11-15 — feat/stage-house-journey — Claude Code — la escena real
- **Hecho:** `stage.py` deja de ser un mock: genera `out/index.html` desde `stage_page.html` (nuevo). Nota primero,
  luego la casa de la familia; al deslizar cambia (cinco partes, los años del plan, cada paso reparando su parte,
  la casa con todo hecho y «¿por cuál empiezas?»). Botón «?» → chat lateral con `/ask/stream`, voz y micrófono;
  el altavoz calla la voz. Estilo de sherpaswealth.com. `brain`: `home` en `intro` y `dates` en `timeline`.
- **Estado:** `./check.sh` pasa (139 tests). Probado en Chromium (escritorio y móvil) con el servidor real.
- **Decisiones:** los años enseñan el plan actual (no hay proyección «con los pasos hechos»); una parte tocada por
  un paso se dibuja «reparada». Sin `combined_moves` no se enseña nota conjunta. El contrato no cambia.
- **Bloqueos:** micrófono y iPhone real sin probar. Sin push todavía: falta el visto bueno de Samuel.
- **Para Raúl:** he tocado tu etapa (`stage.py` entero y la plantilla nueva) porque Samuel me lo pidió. Es un punto
  de partida: cámbialo o tíralo si tu versión va por otro lado. Ficha: `02-DOCS/ftd/stage-casa-interactiva.md`.
- **Para David:** la página pone `audio_path` de cada escena al llegar a su tarjeta y `audio_url` de cada respuesta.
- **Siguiente:** revisarla entre los tres en el punto de las 21:00.
## 2026-11-15 — feat/brain-narration-fast-model — Claude Code
- **Hecho:** la narración pasa de `gpt-5-mini` a `deepseek-flash` (`narrator.py`, `.env.example`) y las cuatro
  `narrations/<familia>.json` están **regeneradas** con él, en modo completo y sencillo, con las escenas por
  persona. Ficha `brain-narracion-modelo-rapido.md`.
- **Estado:** `./check.sh` pasa (132 tests). Las 92 escenas aceptadas por `guard`, ninguna en plantilla.
- **Decisiones:** un solo modelo de texto en todo el producto (el mismo que `/ask`). Generar no fue más rápido
  (7-8 min por tanda) y costó $0,21 entre las dos tandas; gasto total del equipo: $0,41 de $50. Una regeneración
  completa apunta ahora en el JSON el modelo que la escribió.
- **Bloqueos:** ninguno. Nadie ha leído ni escuchado aún los textos nuevos.
- **Para David:** los textos de las cuatro familias han cambiado: los mp3 guardados en caché ya no valen y
  ElevenLabs volverá a cobrar esos caracteres. Espera a que Samuel dé el visto bueno a los textos antes de generar.
- **Para Raúl:** los ids de escena no cambian; solo el texto de `narration`.
- **Siguiente:** Samuel revisa los textos de Samantha y Michael.

## 2026-11-15 — feat/brain-narration-fast-model — Claude Code — documento de escalabilidad
- **Hecho:** `escalabilidad.md` (raíz): cómo crece el producto dando más contexto al modelo. Forma elegida por
  Samuel: **resumen del historial**. Ficha `02-DOCS/ftd/escalabilidad.md`. Solo documentación; no hay código nuevo.
- **Estado:** `./check.sh` pasa (110 tests).
- **Decisiones:** hoy `/ask` guarda el historial pero no se lo envía al modelo (cada pregunta es independiente).
  La propuesta añade a cada pregunta un resumen corto de la sesión, **sin cifras** (para no tocar `guard`), y el
  último turno literal. Primero un resumen hecho con código (`advisor_note`); con el modelo solo si se queda corto.
- **Bloqueos:** ninguno. Falta decidir si se construye antes de la congelación (18 nov, 18:00).
- **Para David y Raúl:** leedlo y decid si lo veis útil para la demo. No cambia la forma de `/ask` para la página.
- **Siguiente:** si se aprueba, issue y rama `feat/brain-ask-summary`.

## 2026-11-15 — feat/voice-stt-fallback — Claude Code
- **Hecho:** `voice_stt_model.py` (nuevo) y `voice.transcribe_async`: si Scribe falla, la grabación la transcribe
  `gemini-3.5-flash-lite` por el proxy. Tests en `tests/test_voice_stt.py`.
- **Estado:** `./check.sh` pasa (132 tests). Real: pregunta hablada en webm → respuesta en 4,9 s; silencio → 422.
- **Decisiones:** Scribe sigue siendo el primero; el respaldo solo entra si Scribe da error y hay `TEAM_KEY`.
- **Bloqueos:** el proxy sigue dando 401 en ElevenLabs (hablar y transcribir). Enlace público sin abrir.
- **Para David:** he tocado tu etapa (`voice.py`, 12 líneas, y `Transcript.engine` puede valer `"model"`). El motivo:
  sin tu clave personal nadie más podía preguntar por voz. Si prefieres otra forma, cámbialo.
- **Siguiente:** probar `/chat` con micrófono real en el móvil (necesita el enlace https de `scripts/share.sh`).

## 2026-11-15 — feat/brain-family-experience — Claude Code
- **Hecho:** por persona (escena `person_<nombre>` en Weah y Johnson; `/ask` con `person`), modo `simple` /
  `complete` (narración y respuestas), `POST /worry`, `GET /reminders` + `POST /follow-up`, `POST /ask/stream`
  (la respuesta llega palabra a palabra), topes de uso, página `/chat`, `scripts/serve.sh`, `scripts/share.sh`,
  `Dockerfile`. Guía en inglés: `BACKEND.md`. Ficha: `brain-experiencia-familia.md`.
- **Estado:** `./check.sh` pasa (126 tests). Probado con el servidor real; `/chat` sin probar en navegador.
- **Decisiones:** lo que se escribe poco a poco es el texto ya aprobado por `guard`, nunca el del modelo según sale.
  `brain.build` acepta `mode` (opcional; el contrato no cambia). Los avisos son frases fijas, sin modelo.
- **Bloqueos:** el proxy de Sherpas da 401 «Invalid API key» en ElevenLabs (hablar y transcribir): sin la clave
  personal de David no hay pregunta por voz ni voz ElevenLabs. Enlace público sin abrir (hay que lanzar `share.sh`).
- **Para David:** ¿puedes probar `/ask` con un webm real y tu clave? Y avisar a un mentor de lo del proxy. Hay
  escenas nuevas (`person_*`) y narración `simple`: `brain.build(diagnostic, mode="simple")`.
- **Para Raúl:** todas las rutas y la forma de los eventos de `/ask/stream` están en `BACKEND.md`; `/chat` es un
  ejemplo que ya las usa todas (preocupación, chat, pasos, aviso del día 3). Manda `mode` y `person` en cada pregunta.
- **Siguiente:** abrir el enlace público y probar en el móvil; resumen del historial como contexto (`escalabilidad.md`).

## 2026-11-15 — feat/brain-ask — Claude Code
- **Hecho:** backend FastAPI (`server.py`): `/ask`, `/history`, `/decision`, `/advisor-note`, `/families`,
  `/presentation/{family}`. `ask.py` (pregunta → escena + respuesta, con `guard`) y `sessions.py` (historial en
  `data/sessions/`, fuera de git). Ficha con todas las rutas: `02-DOCS/ftd/brain-ask.md`.
- **Estado:** `./check.sh` pasa (109 tests, sin llamar al modelo). Real: respuesta en 2,6-4,0 s.
- **Decisiones:** `/ask` devuelve el texto ya y un `audio_url`; el mp3 se genera al pedirlo (con la voz dentro
  tardaba 13-32 s). Modelos: `deepseek-flash`, respaldo `gemini-3.5-flash-lite`. Fuera del plan → frase fija.
- **Bloqueos:** ninguno. Arrancar: `PYTHONPATH=src:. .venv/bin/uvicorn finagent.server:app --port 8000`.
- **Para Raúl:** `POST /ask` como formulario (`family`, `question` o `file`, `session_id`). Devuelve `scene_id` y
  `house_part` (a dónde gira la casa), `text` (subtítulo), `audio_url` (ponlo en un `<audio>`; si da 503, solo
  texto) y `session_id` (guárdalo y mándalo siempre). `GET /history?session_id=` da la lista para «tus preguntas».
  ¿Te vale esta forma? Es un contrato nuevo entre los dos; dime si quieres otro campo.
- **Para David:** uso `voice.transcribe_async` en `/ask` y `voice.speak_async` en `/answers/…mp3`, tal cual. Hoy
  edge-tts tarda 9-30 s por respuesta y falla a ratos; con tu ElevenLabs debería ir en menos de 1 s.
- **Siguiente:** hechos por persona (pareja) y modo sencillo / completo.

## 2026-11-15 — feat/brain-llm-narration — Claude Code
- **Hecho:** `narrator.py` (nuevo): `gpt-5-mini` por el proxy escribe la narración de cada familia, `guard` la revisa
  escena a escena y se guarda en `narrations/<familia>.json` (las cuatro, en el repo). `brain.build` la aplica;
  `brain.build_template` es la versión de plantilla. `openai` en `requirements.txt`. Ficha `brain-narracion-llm.md`.
- **Estado:** `./check.sh` pasa (76 tests) sin llamar al modelo. Gasto total del equipo: $0,13 de $50.
- **Decisiones:** se genera una vez y se guarda (la demo no gasta ni cambia de texto); escena rechazada por `guard` →
  frase de plantilla. La explicación de Sherpas de cada área es un hecho de su escena (`context_*`), así que la
  narración puede citar sus cifras. Regenerar: `python -m finagent.narrator <familia>` (2-3 min, unos céntimos).
- **Bloqueos:** sin respuesta a la pregunta del backend `/ask` (FastAPI o el Node de `examples/voice/`).
- **Para David:** las narraciones son ahora de 40-60 palabras por escena (mp3 de unos 20 s) y traen `$1M`, `%`,
  `VTI` y fechas («January 2027»). Tras `git pull`: `pip install -r requirements.txt`.
- **Para Raúl:** `facts` trae hechos `context_*` con texto largo: no son para pintar. Los subtítulos son `narration`.
- **Siguiente:** Samuel revisa los textos de Samantha y Michael; después, backend `/ask`.

## 2026-11-15 — feat/brain-house-facts — Claude Code
- **Hecho:** `house.py` (nuevo) y `brain.py`: cada pilar es una parte de la casa (`foundations`, `roof`, `walls`,
  `plumbing`, `garden`) con estado `solid` / `cracked` / `broken`; cada paso dice qué parte repara; escenas nuevas
  `all_moves` (casa reparada, solo Weah y Johnson) y `timeline` (el plan año a año). Ficha `brain-hechos-casa.md`.
- **Estado:** `./check.sh` pasa (67 tests). Sin LLM todavía: frases de plantilla. El contrato no cambia.
- **Decisiones:** umbrales nuestros sobre la nota 0-100 del pilar (≥ 70 sólido, ≥ 40 con grietas), en `house.py`.
  Los activos invertibles nunca salen negativos (lo prohíbe el caso): se cortan en 0 y se dice la edad.
- **Bloqueos:** sigo sin `.env` (`TEAM_KEY`); sin respuesta a la pregunta del backend `/ask` (FastAPI o Node).
- **Para Raúl:** todo va en `visual.data`: `intro` trae `house` (parte → estado) y `people`; `pillar_*` trae
  `house_part` y `state`; `move_*` trae `house_part`, `action`, `effort` y nota antes/después; `timeline` trae
  `points` (un punto por año) y `events` (`retirement`, `debt_free`, `savings_run_out` o `savings_last`).
- **Para David:** dos mp3 nuevos (`all_moves`, `timeline`) y las frases de pilar y de paso son más largas.
- **Siguiente:** narración con LLM por el proxy, pasada por `guard`.

## 2026-11-14 — feat/brain-real-cases — Claude Code — resumen del día y propuesta de arquitectura
- **Hecho:** tres cosas, detalladas en las dos entradas de abajo y en `02-DOCS/ftd/`: (1) documentos de idea
  unificados en «cada persona elige su modo al abrir»; (2) `brain` lee los cuatro casos reales; (3) `guard` usa
  formato inglés (punto decimal, coma de millares).
- **Estado:** `./check.sh` pasa (10 tests). Dos PR abiertos: documentos del modo y `brain` + `guard`.
- **Decisiones (propuesta mía, a confirmar entre los tres):** workflow, no agente. La narración se genera una vez
  por familia (LLM de texto por el proxy → `guard` → voz). En las preguntas en vivo el LLM elige la parte de la casa
  de una lista cerrada y responde solo con los hechos de esa parte; `guard` revisa antes de hablar.
- **Bloqueos:** no hay `.env` con `TEAM_KEY` en mi máquina ni `openai` en `requirements.txt`; hoy no hay ningún LLM.
- **Para David y Raúl:** las preguntas en vivo necesitan un **backend** (hoy solo generamos un HTML fijo). Propongo
  un FastAPI pequeño con una ruta `/ask`; la clave se queda ahí. ¿Os encaja, o partimos del Node de `examples/voice/`?
- **Siguiente:** subir esto en dos PR y seguir con los hechos por familia y por persona (paso 2).

## 2026-11-14 — feat/brain-real-cases — Claude Code — `brain` con casos reales
- **Hecho:** `brain.py` lee `cases/<familia>/financial-health.json`: nota, banda, los cinco pilares (puntos como en
  la app, p. ej. 22/30) y los `top_moves` con nota antes y después. `run.py` usa a Samantha por defecto. Borrado
  `fixtures/` (el diagnóstico inventado). Tests: los cuatro casos.
- **Estado:** `./check.sh` pasa (10 tests). Sin LLM todavía: frases de plantilla en inglés.
- **Decisiones:** `brain.build` devuelve `language="en"` por defecto (regla 9). El contrato no cambia.
- **Bloqueos:** ninguno. `guard` usa ya formato inglés: punto decimal, coma de millares («6,800» = 6800).
- **Para David:** la narración sale ya en inglés, así que `voice` usa `en-US-EmmaMultilingualNeural`. Ids de
  escena nuevos (`intro`, `pillar_debt`, `move_1`…): son los nombres de tus mp3.
- **Para Raúl:** `presentation.json` trae 9 escenas reales por familia; `visual.data.fact_id` sigue igual.
- **Siguiente:** hechos por familia y por persona (paso 2).

## 2026-11-14 — docs/mode-choice-on-open — Claude Code
- **Hecho:** `ideas.md` e `idea-david.md`: se quita «modo sencillo por defecto». Queda una sola versión, la de
  `nota-idea.md`: **cada persona elige su modo al abrir** (pantalla inicial con dos botones, sencillo o completo).
- **Estado:** `./check.sh` pasa (4 tests). Solo documentación.
- **Decisiones:** no hay modo por defecto; nada empieza hasta elegir, y se puede cambiar de modo después.
- **Bloqueos:** ninguno.
- **Para David:** he editado `idea-david.md` (sección 2 y «Para todos los públicos») para que coincida con la nota.
  Tus entradas del 13 nov en `visitas/david.md` siguen diciendo «por defecto»; no las toco, son registro.
- **Para Raúl:** la primera pantalla de `stage` es el selector de modo, no la casa.
- **Siguiente:** repartir el MVP y abrir las issues.

## 2026-11-13 — docs/idea-final-samuel — Claude Code
- **Hecho:** `ideas.md`: mi idea final es **S1 · Casa interactiva en el tiempo**: la casa de David vista en
  una web que se recorre deslizando; el scroll es la línea del tiempo del plan. Es un enlace que el asesor da a la
  familia, con casa de hoy / casa si siguen el plan y dos botones: resumen escrito y audio con idioma y acento.
  Es mi única idea: he quitado de `ideas.md` todas las anteriores (árbol incluido); siguen en el historial de git.
- **Estado:** `./check.sh` pasa (4 tests). Solo documentación.
- **Decisiones:** ninguna de equipo; es mi propuesta para el voto. Límite comprobado en `cases/`: los pilares son de
  hoy; año a año solo hay patrimonio, deuda y activos invertibles, así que tejado y cimientos no cambian a futuro.
- **Para David:** mi idea usa tu casa tal cual (partes, reparar, estilo de plano); solo cambia cómo se recorre. El
  selector de idioma y acento caería en la voz: ¿qué voces de `edge-tts` ves viables? (la demo va en inglés).
- **Para Raúl:** tu «Wait…» está dentro de mi idea. Cambio grande para ti: Samuel quiere la casa en **3D** (`three.js`,
  hecha de cajas, escenas que avanzan y retroceden con el dedo, como la referencia enlazada en `ideas.md`) y una vista del
  asesor que cambia la casa. ¿Lo ves factible en cinco días, o partimos del SVG?
- **Siguiente:** votar y redactar la nota de `/idea` (hoy, 22:00).

## 2026-11-13 — docs/shared-ownership — Claude Code
- **Hecho:** `AGENTS.md`, regla 1: de «un dueño por archivo» a **«todos pueden modificar todo»**. La columna
  «Dueño» de la tabla pasa a «Responsable» (referente de la etapa, no candado). Explícito para las IA: si ves algo incorrecto en cualquier archivo, lo arreglas tú. `CLAUDE.md` y `README.md` alineados.
- **Estado:** `./check.sh` pasa (4 tests). Solo documentación.
- **Decisiones:** siguen igual la regla 2 (el contrato se cambia en PR aparte con el visto bueno de los tres) y
  `visitas/` (cada uno escribe solo en su archivo, para evitar conflictos de merge).
- **Para David y Raúl:** ya podéis editar `brain.py`, `guard.py` o cualquier otro archivo sin pedirlo; yo haré lo
  mismo con `voice.py` y `stage.py`. Si tocáis una etapa ajena: rebase antes, PR pequeño y una línea «Para …» aquí.
  Si no estáis de acuerdo con el cambio, decidlo en vuestro archivo y lo revertimos.
- **Siguiente:** votar la idea y redactar la nota de `/idea` (hoy, 22:00).

## 2026-11-12 23:17 — docs/ideas-s4-only — Claude Code
- **Hecho:** `ideas.md`: mi sección queda con una sola idea, **S4 · The Family Tree**, que ahora empieza con la
  configuración por persona (formato, nivel de detalle, qué le preocupa). Borradas S1, S2 y S3; quedan en una lista
  corta de descartadas con su porqué, para la nota del viernes.
- **Estado:** `./check.sh` pasa (4 tests). Solo documentación.
- **Bloqueos:** ninguno.
- **Para David y Raúl:** siguen en pie las preguntas de la entrada anterior (¿fusionar casa y árbol?, ¿qué es
  factible en SVG?).
- **Siguiente:** votar entre los tres y redactar la nota de `/idea` (vie 13 nov, 22:00).

## 2026-11-12 23:13 — docs/ideas-family-tree — Claude Code
- **Hecho:** `ideas.md`: nueva idea **S4 · The Family Tree** (el plan como árbol vivo; una rama por persona; cada
  paso del plan es un cuidado), ahora mi idea principal. S1 pasó a ser «Your Plan, Your Way» (agente configurable
  por persona) en el PR #7 y queda como capa encima de S4.
- **Estado:** `./check.sh` pasa (4 tests). Solo documentación.
- **Decisiones:** ninguna de equipo todavía; falta votar.
- **Bloqueos:** ninguno.
- **Para David:** S4 es del mismo tipo que tu casa (un objeto cuyas partes son los pilares). La diferencia es que el
  árbol está vivo y da motivo para volver. ¿Competimos o las fusionamos?
- **Para Raúl:** faltan tus ideas y tu opinión sobre qué es factible dibujar en SVG en seis días (casa o árbol).
- **Siguiente:** votar entre los tres y redactar la nota de `/idea` (vie 13 nov, 22:00).

## 2026-11-12 14:50 — main — Claude Code
- **Hecho:** el repo parte ahora del repo de partida de Sherpas (remoto `upstream`): entran `cases/` (las cuatro
  familias), `examples/voice/`, `BRIEF.md`. `AGENTS.md` y `02-DOCS/reto.md` actualizados con las bases reales.
  Creado este libro de visitas (`visitas/`), que sustituye a `comunicacion.md`.
- **Estado:** `./check.sh` pasa (4 tests) sobre el `main` con la voz de David (PR #1 a #4).
- **Decisiones:** el producto va en inglés; créditos por el proxy de Sherpas con una sola `TEAM_KEY` ($50, tope de
  $1,40 en ElevenLabs); el MCP ya no es obligatorio, los datos están en `cases/`.
- **Bloqueos:** la idea no está elegida; el contrato `Presentation` (escenas narradas) puede no encajar con ella.
- **Para David:** tus entradas de `comunicacion.md` están tal cual en `visitas/david.md`; tu propuesta de que
  `AGENTS.md` mande leer el registro al empezar ya está hecha.
- **Para David y Raúl:** leed `02-DOCS/reto.md`. Propuesta de idea: «First Move» (experiencia de 2 min por persona
  en el móvil que acaba en un primer paso acordado, con seguimiento día 3 y 30); os la cuento hoy. Hay que acordar la idea antes del vie 13 nov a las 22:00 (`/idea`, 10 puntos).
- **Siguiente:** acordar la idea entre los tres y redactar la nota de `/idea`.
