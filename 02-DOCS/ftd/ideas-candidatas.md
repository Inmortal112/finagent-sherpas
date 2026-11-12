---
created: 2026-11-12
status: done
branch: docs/ideas
---
# Archivo de ideas candidatas

## Intención

Que los tres (y sus IA) vean en el repo tres ideas de cada uno y elijan una antes de la nota de `/idea` (vie 13 nov, 22:00).

## Alcance

- Dentro: `ideas.md` en la raíz con las tres ideas de Samuel, secciones vacías para David y Raúl, tabla de votos y plantilla.
- Fuera: elegir la idea, redactar la nota de `/idea`, tocar código o contrato.

## Checklist

- [x] Las cifras citadas salen de `cases/` → leídas con un script de `score.top_moves`, `score.combined_moves`, `assetDepletion` y las cuatro `persona.md`.
- [x] Cada persona escribe en su propia sección (evita conflictos de merge).
- [x] `./check.sh` pasa.

## Evidencia (2026-11-12, rama `docs/ideas` sobre `ee54445`)

- `./check.sh` → `4 passed`, `OK -> out/index.html`.
- HERRAMIENTA-AUSENTE: `ruff` y `mypy` no instalados (el cambio es solo documentación).

## Siguiente

David y Raúl añaden sus tres ideas y los tres votan en la tabla.
