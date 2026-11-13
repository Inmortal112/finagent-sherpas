---
created: 2026-11-13
status: done
branch: docs/shared-ownership
---
# Todos pueden modificar todo (regla 1 de AGENTS.md)

## Intención
Samuel pide quitar «un dueño por archivo»: cualquiera de los tres (y su IA) puede editar cualquier archivo.
Con seis días y una idea que aún no está elegida, esperar al responsable de cada archivo frena más de lo que protege.

## Alcance
- Entra: regla 1 y sección «Quién puede subir» de `AGENTS.md`; la misma frase en `CLAUDE.md`; una línea de
  `README.md`; entrada en `visitas/samuel.md`.
- NO entra: regla 2 (el contrato sigue necesitando el visto bueno de los tres); `visitas/` (un archivo por
  persona, por conflictos de merge); docstrings `owner:` de `voice.py`, `stage.py`, `guard.py` (siguen indicando
  el responsable); protección de ramas en GitHub (no hay `CODEOWNERS` ni nada que cambiar).

## Checklist
- [x] Regla 1 reescrita y sin restos de «edita solo lo tuyo» → `grep`.
- [x] `CLAUDE.md` y `README.md` no contradicen la regla nueva → `grep`.
- [x] `./check.sh` pasa.

## Evidencia
- `grep -rn "solo lo tuyo\|archivos de otro" AGENTS.md CLAUDE.md README.md` → sin resultados.
- `./check.sh` → ver entrada de `visitas/samuel.md` (4 tests, pipeline completo).

## Siguiente
Fusionar el PR y avisar a David y Raúl para que hagan `git pull`.
