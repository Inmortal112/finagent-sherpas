---
created: 2026-11-15
status: done
branch: feat/stage-integration
---
# Comprobación de extremo a extremo de la primera web

- Dueño: Samuel (`Inmortal112`)

## Intención
Samuel pide comprobar que todo va bien cuando la otra sesión termine la casa interactiva, y tener una primera web
donde verlo. Esta rama une `feat/stage-house-journey` (la casa, commit `352d827`) con `main` (`ef5548d`, que ya trae
el resumen del historial en `/ask`) y lo comprueba junto.

## Alcance
- Entra: la fusión de las dos ramas, el conflicto de `visitas/samuel.md` y la comprobación. Ningún cambio de código.
- NO entra: cambiar la página; enlace público (`scripts/share.sh`); micrófono real; despliegue.

## Checklist
- [x] `./check.sh` pasa con todo junto.
- [x] El servidor arranca y sirve la página, el chat y las rutas.
- [x] Las cuatro familias en los dos modos.
- [x] Pregunta, pregunta de seguimiento, decisión, ficha del asesor, aviso del día 3 y audio.
- [x] La página se dibuja en escritorio y en móvil.
- [ ] Una persona la ha recorrido entera en un navegador.

## Evidencia (2026-11-15, sobre `619d197`)
- `./check.sh` → `148 passed`, `OK -> out/index.html`.
- Servidor (`uvicorn finagent.server:app --port 8766`): `/healthz` → `{"ok":true}`; `/` → 200, `text/html`, 87.525
  bytes (la casa); `/chat` y `/try` → 200; `/families` → 200. Cero `ERROR` o `Traceback` en el log.
- `/presentation/{familia}?mode=`: Lewis y Carter 10 escenas, Weah y Johnson 13, en `complete` y `simple`; todas
  traen `home` en `intro`. Máximo de palabras por escena: 61 en `complete`, 28 en `simple`.
- `/ask/stream` (Samantha): «Why does my garden dry up?» → eventos `thinking`, `turn`, 42 `delta` y `done`;
  `timeline`, `garden`. Con el mismo `session_id`: «and what can I do about it?» → `t2`, `move_3`, `garden`.
- `POST /decision` (`move_3`) → guardado; `/advisor-note` → dos preguntas, `asked_most_about: ["garden"]` y la
  decisión; `/reminders?today=2026-11-20` → aviso `check_in` del paso y la fecha del plan de enero de 2027.
- `/answers/<sesión>/t1.mp3` → 200, `audio/mpeg`, 139.824 bytes.
- Capturas con Chromium sin ventana, 1440×860 y 390×844: cabecera «Under One Roof», selector de familia
  («Samantha · 82»), altavoz, «Hello, Samantha.», el anillo de la nota, «Sherpas calls that strong», el botón
  «Step inside your home» y el botón «?» del chat. Sin solapes en móvil.
- **A mirar a ojo:** en las capturas el anillo marcaba 36 y 34, no 82. Parece la animación de la nota cogida a
  medias (el selector sí dice 82 y la otra sesión la vio llegar a 82 con Playwright), pero no lo he confirmado.
- Sin comprobar: el recorrido al deslizar y el chat dentro de la página (solo las rutas que usa); micrófono real;
  Safari / iPhone; cómo suena la narración.

## Siguiente
Samuel abre `scripts/serve.sh` → http://localhost:8000 y recorre la casa entera; mira que la nota llega a 82.
