---
created: 2026-11-13
status: done
branch: docs/idea-final-samuel
---
# Idea final de Samuel: S5 · Home Story

## Intención
Dejar en `ideas.md` la idea final de Samuel para el voto: la casa de David en una web interactiva que la familia
recorre deslizando, viendo el plan en cada momento. Llega como enlace del asesor, enseña la casa de hoy y la
casa si siguen el plan, y tiene botones de resumen escrito y de audio con idioma y acento.

## Alcance
- Entra: sección de Samuel en `ideas.md` (S5 sustituye a S4, que pasa a descartadas) y entrada en `visitas/samuel.md`.
- NO entra: `idea-david.md`, `idea-raul.md`, la tabla de votos, la nota de `/idea`, código o contrato.

## Checklist
- [x] Las cifras citadas salen de `cases/` → script sobre `score.pillars`, `goals.chartGoals` y `projections.yearly`.
- [x] `./check.sh` pasa.

## Evidencia
- Weah: objetivos 2028-07 (coche), 2030-01 (casa), 2038-08 (Liam), 2048 (jubilación); `total_debts` = 0 en 2059.
- Samantha: `BANKRUPTCY_ZEROCASH` 2053-02, primer `investable_assets` negativo en 2053. Michael: 2075-01.
- Johnson: protección `0/20`. `projections.yearly` solo trae patrimonio, deuda y activos invertibles.
- `./check.sh` → `4 passed`, `OK -> out/index.html`.

## Siguiente
Fusionar el PR, votar entre los tres y redactar la nota de `/idea`.
