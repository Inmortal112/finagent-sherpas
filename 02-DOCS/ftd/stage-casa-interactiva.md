---
created: 2026-11-15
status: done
branch: feat/stage-house-journey
---
# Stage real: la casa interactiva (scroll, chat «?» y altavoz, estilo Sherpas)

## Intención
Sustituir el mock de `stage.render` por la página que ve el jurado: primero la nota, después la casa de la
familia con sus datos, y al deslizar la casa cambia: el recorrido por sus cinco partes, los años del plan y
cada paso del asesor reparando su parte, hasta la casa con todos los pasos hechos. Un botón «?» abre un chat
lateral con el modelo (`/ask/stream`) y un altavoz calla la voz. Aspecto de la web de Sherpas.

## Alcance
- Entra: `stage.py` (misma firma), plantilla `stage_page.html`, dos datos nuevos en `visual.data` desde `brain`
  (`home` en `intro`, `dates` en `timeline`; el contrato no cambia), tests de la escena.
- NO entra: 3D, avatar, modo `simple` en la página, elegir persona en una pareja, avisos del día 3 en pantalla.
- Honestidad: los años muestran **el plan actual** (Sherpas no publica una proyección «con los pasos hechos»).
  Los pasos muestran la nota antes/después que Sherpas calculó; una parte tocada por un paso se dibuja
  «reparada», no «sólida». Sin combinación publicada (`combined_moves` vacío) no se enseña una nota conjunta.

## Checklist
- [x] `stage.render` genera `out/index.html` desde la plantilla, con la `Presentation` dentro → `./check.sh`.
- [x] La casa se dibuja con el estado de cada parte y las personas, para las cuatro familias → captura.
- [x] Al deslizar: recorrido, años (jardín según `investable_assets`), pasos y casa reparada → captura.
- [x] «?» abre el chat, la respuesta llega poco a poco y la casa marca la parte → prueba con el servidor.
- [x] El altavoz calla la voz en curso y las siguientes → prueba en navegador.
- [x] Sin servidor (abrir el archivo) la página funciona y el chat lo dice con claridad.

## Evidencia
- `./check.sh` → 139 passed y `OK -> out/index.html` (7 tests nuevos en `tests/test_stage.py`).
- Chromium sin ventana (Playwright) contra `uvicorn finagent.server:app --port 8010`, 1440×860 y 390×844, sin
  errores de consola: nota de Samantha (82), casa con Samantha 47 / Ethan 18 / Ava 16 / «Home you own»; en 2060 el
  jardín seco y «2059 · No debt left in the plan»; paso 1 con 82 → 84 y el tejado reparado; Michael (26) con tejado,
  cimientos y tuberías rotos; Weah en móvil 60 → 78.
- Chat: «Why is my roof broken?» → respuesta real del modelo con las cifras del plan, la casa marca el tejado y
  suena el mp3 (`paused: false`); altavoz → `paused: true`, sin `src`, página en `muted`.
- Elegir paso: `POST /decision` → «Your advisor will see it, and we check in with you in three days.»
- Abierta como archivo (`file://`): 12 capítulos dibujados; el chat avisa de que hace falta el servidor.
- Sin comprobar: micrófono real (mantener pulsado), Safari/iPhone real, y cómo suena la narración al deslizar.
- **verify** (commit `9b603a2`, limpio, ya sobre `origin/main`): `./check.sh` → 139 passed; `compileall src contracts` → ok;
  servidor en :8010 → `/healthz` `{"ok":true}`; recorrido sin ventana → 12 capítulos, sin errores de consola.
  HERRAMIENTA-AUSENTE: `ruff` y `mypy` no están en `.venv`. Veredicto: PASA (con lo «sin comprobar» de arriba).

## Siguiente
Que Samuel y Raúl la abran (`scripts/serve.sh` → http://localhost:8000) y digan qué cambiar; después PR.
