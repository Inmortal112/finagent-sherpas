---
created: 2026-11-16
status: done
branch: docs/readme-project-overview
---
# README del proyecto y test de avisos que fallaba de madrugada

## Intención
El `README.md` decía «esqueleto con mocks» y no explicaba el proyecto. Sherpas pide el repo público para mentores
y jurado: el README debe contar qué es Under One Roof, en qué se basa y cómo funciona. De paso, `./check.sh`
fallaba en `main` entre las 00:00 y la 01:00 (hora de España) y eso se arregla primero (regla 3).

## Alcance
- Entra: `README.md` reescrito en inglés (regla 9); día de hoy en UTC en `/reminders` y en sus tests.
- No entra: `STAGE.md`, `BACKEND.md`, `VOICE.md` (el README enlaza a ellos); párrafo de entrega; hacer público el repo.

## Checklist
- [x] `/reminders` usa el día UTC, igual que las fechas guardadas (`sessions._now`). Antes usaba `date.today()`
      (hora local): de 00:00 a 01:00 el aviso del día 3 salía un día antes. → `./check.sh`
- [x] README: qué es, tabla pilar → parte de la casa, qué hace la familia, cómo funciona, cómo ejecutarlo. Cifras
      (notas de las cuatro familias, umbrales 70/40) leídas de `cases/` y `house.py`.
- [ ] Ver el README renderizado en GitHub tras el merge.

## Evidencia
- Antes (16 nov, 00:11 CET): `./check.sh` → `1 failed, 164 passed`
  (`test_reminders_check_in_on_day_3_and_announce_the_plan_dates`: `['check_in'] == []`).
- Después (misma hora): `./check.sh` → `165 passed`, `OK -> out/index.html`.

## Siguiente
Hacer público el repo (Samuel) y escribir el párrafo de entrega.
