---
created: 2026-11-12
status: done
branch: docs/visit-log
---
# Libro de visitas y subida libre para los tres

## Intención

Que David y Raúl (y sus IA) suban a GitHub sin depender del permiso de Samuel, y que las tres IA compartan un
registro corto de lo hecho para no releer el repo en cada sesión.

## Alcance

- Dentro: sección «Quién puede subir» en `AGENTS.md` (el permiso ya lo quitó David de `CLAUDE.md` en el PR #4);
  carpeta `visitas/` con instrucciones, plantilla y un archivo por persona; mover las entradas de
  `comunicacion.md` (de David) a `visitas/david.md` y borrar ese archivo, **vía PR para que David lo apruebe**.
- Fuera: cambiar el flujo de ramas/PR, la protección de ramas en GitHub o el contrato.

## Checklist

- [x] Los tres tienen permiso de escritura y `main` no está protegida → `gh api .../collaborators` (admin, write, write) y `branches/main/protection` → 404 «Branch not protected».
- [x] Ningún archivo del repo exige el permiso de Samuel para subir → `grep -rni "permiso de samuel"` sin resultados.
- [x] `visitas/` con un archivo por persona (decisión: evita conflictos de merge cuando los tres escriben a la vez).
- [x] `./check.sh` pasa.

## Evidencia (2026-11-12, rama `docs/visit-log` sobre `ee54445`)

- `./check.sh` → `4 passed`, `OK -> out/index.html`.
- HERRAMIENTA-AUSENTE: `ruff` y `mypy` no instalados.
- No verificado: que Astra (Raúl) cargue `AGENTS.md` sola; si no, hay que pegárselo al empezar.

## Siguiente

David revisa y fusiona el PR (toca su `comunicacion.md`); después cada uno deja su entrada en `visitas/`.
