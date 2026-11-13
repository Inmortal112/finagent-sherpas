# Visitas — Samuel (cerebro: `brain.py`, `guard.py`)

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
