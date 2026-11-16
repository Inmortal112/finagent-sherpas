---
created: 2026-11-17
status: done
branch: chore/repo-cleanup
---
# Limpieza del repo antes de la entrega

## Intención
Quitar lo que no forma parte del producto (ejemplos de los organizadores, duplicados, código sin uso) y sacar de
la raíz los documentos de trabajo, para que el jurado vea un repo limpio. Rellenar el enlace del MVP.

## Alcance
- Dentro: `examples/voice/` (ejemplo Node de Sherpas, sin uso), 3 capturas duplicadas, imports y constantes sin
  uso, mover a `02-DOCS/` las ideas, la nota de `/idea`, la propuesta de escalabilidad y el brief oficial con sus
  imágenes, arreglar enlaces, enlace de Render en `SUBMISSION.md`.
- Fuera: cambios de comportamiento, `stage_page.html` (sin código muerto detectable sin riesgo), fichas FTD
  antiguas (son el historial), `visitas/`, contrato.

## Checklist
- [x] Borrar `examples/voice/` y su mención en README → `git grep examples/voice` vacío fuera del historial.
- [x] Mover ideas y brief a `02-DOCS/` → ningún enlace roto (script de enlaces).
- [x] Borrar duplicados de `review-assets` → la ficha apunta a las copias `-v2`.
- [x] Imports sin uso de `export_coast.py` (`random`, `array`) → vulture ya no los señala. `house.PARTS` se queda:
  lo usa `tests/test_stage.py` (vulture solo miraba `src/`).
- [x] `SUBMISSION.md` con el enlace de Render → leído.
- [x] `./check.sh` pasa.

## Evidencia
- Raíz: de 25 entradas a 18. Borrados 8 archivos de `examples/voice/` y 3 capturas idénticas (mismo md5 que sus `-v2`).
- Script de enlaces relativos en todos los `.md`: 10 rotos tras mover el brief → corregidos → 0.
- `./check.sh` → 219 passed.
- Debug: al quitar `house.PARTS` fallaron 12 tests (`AttributeError` en `test_stage.py:29`). Causa: vulture no
  analizó `tests/`. Arreglo: restaurar la constante. Sin test nuevo: la suite ya lo detecta.

## Siguiente
Fusionar en `main` y comprobar que Render se reconstruye bien.
