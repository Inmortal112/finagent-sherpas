# Visitas — Samuel (cerebro: `brain.py`, `guard.py`)

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
