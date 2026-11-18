---
created: 2026-11-18
status: done
branch: chore/final-cleanup
---
# Limpieza final antes de la entrega

## Intención
Repasar todo el repo y quitar lo que sobra: código y estilos sin uso, líneas en blanco de más, espacios al
final de línea y restos locales, sin cambiar lo que ve el jurado.

## Alcance
- Dentro: todos los archivos de texto versionados, el CSS de la escena, las worktrees y ramas locales ya fusionadas.
- Fuera: los JSON de Sherpas (`cases/*/*.json`; en `persona.md` de Samantha solo se quitan líneas en blanco dobles), fichas FTD antiguas (historial), contrato,
  `scripts/voice_listen_test.py` (herramienta documentada en `VOICE.md`, no un ejemplo).

## Checklist
- [x] Python sin código muerto → vulture en `src scripts contracts tests`: solo falsos positivos (rutas FastAPI,
  atributos de Blender, firmas de mocks).
- [x] JS sin funciones sin uso → `countTo` (definida y nunca llamada) borrada de `stage_page.html`.
- [x] CSS sin reglas huérfanas → `.ring` (el anillo antiguo, sustituido por `.hero-score-dial`) y `.year-num`,
  22 líneas entre `stage_page.html` y `web/architectural.css`.
- [x] Formato → script sobre todos los archivos versionados: 0 espacios al final, 0 bloques de líneas en blanco
  repetidas, todos acaban en un solo salto de línea.
- [x] Restos locales → 5 worktrees y 27 ramas locales fusionadas borradas; `.claude/` en `.git/info/exclude`.
- [x] `./check.sh` pasa y la página se ve igual.

## Evidencia
- `./check.sh` → 241 passed.
- Chromium headless contra el backend real (`?welcome=0`, 1280×800 y 375×800): sin errores de JS, el marcador
  de puntuación y el héroe idénticos.
- Duplicados que se quedan a propósito: `tests/test_ask.py:105` y `tests/test_voice_speak.py:43` repiten la
  llamada para probar la caché.

## Siguiente
Grabar el vídeo de 2 min y poner su enlace en `SUBMISSION.md` (único `TODO` que queda).
