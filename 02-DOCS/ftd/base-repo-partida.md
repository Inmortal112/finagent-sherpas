---
created: 2026-11-12
status: done
branch: main
---
# Basar el repo en el repo de partida de Sherpas

## Intención

Que nuestro repo parta de `SherpasEngineering/hackathon-upv-2026`: tener dentro los cuatro casos (`cases/`), el
ejemplo de voz (`examples/voice/`) y el brief oficial, y poder traer sus actualizaciones (p. ej. el PDF de
Samantha, que aún no está) con un `git pull upstream main`.

## Alcance

- Dentro: remoto `upstream`, merge de su historial en `main`, resolver `README.md` y `.gitignore`, comprobar `./check.sh`.
- Fuera: cambiar `brain.py` para leer los casos reales, tocar el contrato o la arquitectura (depende de la idea),
  hacer público el repo, push.

## Checklist

- [x] Remoto `upstream` por SSH y su `main` descargado.
- [x] Merge con historiales no relacionados (no copia de archivos: así los pulls futuros de `upstream` funcionan).
- [x] `README.md`: se conserva el nuestro; el de Sherpas pasa a `BRIEF.md` en la raíz (sus enlaces relativos a `cases/` y `assets/` siguen funcionando).
- [x] `.gitignore`: unión de los dos.
- [x] `./check.sh` pasa con el árbol fusionado.
- [x] Ningún secreto entra con el merge.
- [x] Commit del merge en `main` y push (aprobado por Samuel el 12 nov).

## Evidencia (2026-11-12, merge preparado en `main`, sin commit)

- `git fetch upstream` → `upstream/main` en `056a8f9` (3 commits).
- `git merge upstream/main --allow-unrelated-histories --no-commit` → conflictos add/add solo en `README.md` y `.gitignore`; resueltos como dice el checklist.
- Entran 26 archivos nuevos: `assets/` (3), `cases/` (15, 5,0 MB), `examples/voice/` (7) y `BRIEF.md`.
- `./check.sh` con el árbol fusionado → `4 passed` y `OK -> out/index.html`.
- Los 8 JSON de `cases/` cargan con `json.load`.
- Búsqueda de patrones de clave (`sk-…` largo, `Bearer …`, JWT) en lo preparado → sin coincidencias. `examples/voice/.env.example` trae solo el marcador `TEAM_KEY=sk-...`.
- No verificado: ejecutar `examples/voice` (necesita Node 22 y la clave del equipo, que aún no está en `.env`).
- Límite conocido: como su `README.md` vive aquí como `BRIEF.md`, un cambio futuro de su README dará conflicto en `README.md` al hacer pull; se resuelve quedándonos con el nuestro y copiando el suyo a `BRIEF.md`.

### verify (2026-11-12, sobre `7f90cf5` + merge preparado, árbol sucio) — PASA

- `./check.sh` → `4 passed`, `OK -> out/index.html`.
- `python -m compileall -q src contracts tests` → sin errores.
- HERRAMIENTA-AUSENTE: `ruff` y `mypy` no están instalados; no se ejecutó lint ni tipos.
- `origin/main` sin commits nuevos respecto a local antes del push.

## Siguiente

David y Raúl hacen `git pull`. Después, elegir la idea y enviar `/idea` antes del vie 13 nov a las 22:00.
