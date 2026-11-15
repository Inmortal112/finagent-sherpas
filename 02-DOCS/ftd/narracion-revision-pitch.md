---
created: 2026-11-15
status: done
branch: fix/narration-part-score
---
# Revisión de los textos del pitch y nota de una parte «sobre 100»

- Dueño: Samuel (`Inmortal112`)

## Intención
Nadie había leído las narraciones nuevas (`deepseek-flash`). `guard` comprueba que cada número existe en los hechos
de la escena, no que se use con su significado. Se leen los textos de Samantha y Michael (los del pitch) y las
escenas de pasos, personas y línea del tiempo de Weah y Johnson, comparando cada cifra con el texto de Sherpas.

## Alcance
- Entra: leer los textos; corregir a mano los errores claros; una comprobación nueva en `guard` para el error
  encontrado; test.
- NO entra: regenerar con el modelo; cambiar el estilo; los textos de Weah y Johnson que no son de pasos, personas,
  intro o línea del tiempo (sin leer).

## Hallazgos
- **Error (corregido):** Michael, modo sencillo, `move_1`: «It lifts your roof score to 31 out of 100». El 31 es la
  nota global, no la del tejado. Ahora: «It repairs your roof and lifts your score to 31 out of 100.»
- **Exageración (corregida):** Samantha, modo sencillo, `pillar_investments`: «…so it cannot pay for college or
  later years». Sherpas dice que una casa «is not money you can easily spend». Ahora: «…which is not easy to spend
  on college or later years.»
- **Dudosas, sin tocar (decide Samuel):** Johnson `all_moves`: «That is the largest single jump the plan holds»
  (comparación que hace el modelo; 60 es la nota más alta de `combined_moves`, pero el plan no lo dice así).
  Johnson `timeline`: «It holds, but only if the saving keeps up in the years before» (condición que no está en
  los hechos).
- **Comprobadas y correctas** contra `narrative` de Sherpas: Michael `$3,500` al 20 %, `$145,000` invertibles,
  `$16,530` de hueco en la reserva, `$720,000` de hueco en el seguro de vida; Samantha `$750`, `6.1 months`, `65%`,
  `$900,000`.

## Decisiones
- **Regla nueva en `guard`** (`part_scored_out_of_100`): solo la nota global es sobre 100 (una parte puntúa sobre
  10 a 30), así que «roof score … out of 100» es siempre un error. `narrator.check` lo rechaza, también en `/ask`.
- Las dos correcciones son a mano: el campo `model` sigue diciendo `deepseek-flash` porque escribió el resto.

## Checklist
- [x] Texto con «roof score to 31 out of 100» rechazado; el corregido, aceptado → test.
- [x] Los 92 textos guardados siguen aceptados (el test por familia no cambia) → `./check.sh`.
- [x] `./check.sh` pasa.

## Evidencia (2026-11-15, sobre `7a28f5e` + cambios sin commit)
- Búsqueda del patrón en los 92 textos → 1 caso (el de Michael); tras corregir, 0.
- `pytest -q tests/test_narrator.py` → `10 passed`. `./check.sh` → `151 passed`, `OK -> out/index.html`.
- `ruff` y `mypy`: HERRAMIENTA-AUSENTE. Veredicto: PASA.
- Sin comprobar: los pilares de Weah y Johnson; cómo suenan los textos en voz.

## Siguiente
Samuel decide sobre las dos frases dudosas de los Johnson.
