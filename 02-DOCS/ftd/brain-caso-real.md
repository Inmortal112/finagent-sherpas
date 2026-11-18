---
created: 2026-11-14
status: done
branch: feat/brain-real-cases
---
# `brain` lee un caso real de `cases/`

## Intención
Paso 1 de la parte de Samuel en Under One Roof: `brain.build` deja de leer el diagnóstico inventado
(`fixtures/diagnostic_sample.json`) y lee el `financial-health.json` de una familia real de `cases/`.
Sin LLM todavía: frases de plantilla en inglés, para que la tubería completa funcione ya con datos reales.

## Alcance
- Entra: `src/finagent/brain.py` (hechos y escenas a partir de `score` y `case.household`), `run.py` (caso por
  defecto), `tests/test_pipeline.py` (los cuatro casos), borrar `fixtures/`, línea de `CLAUDE.md` sobre el fixture.
- NO entra: el contrato (`contracts/schemas.py` no cambia); LLM; partes de la casa, personas y años (paso 2 y 3);
  `investment-analysis.json` y `persona.md`.

## Checklist
- [x] `brain.build` produce una `Presentation` válida para los cuatro casos → test parametrizado.
- [x] La nota de cada caso coincide con `score.published_score` del JSON → test.
- [x] `guard` no encuentra números sin respaldo en ningún caso → test.
- [x] Nada referencia ya el fixture inventado → `grep`.
- [x] `./check.sh` pasa.

## Decisiones
- La firma no cambia de parámetros, pero `language` pasa a valer `"en"` por defecto: las bases exigen el producto en
  inglés (regla 9) y la voz elige la voz según `Presentation.language`.
- Cada pilar se cita con los puntos que la familia ve en la app (`points_shown_in_app`, p. ej. 22/30), no con la
  nota interna 0-100.
- Los pasos (`top_moves`) citan solo la nota antes y después, no los importes del texto `action`.

## Añadido después (pedido por Samuel)
- [x] `guard` usa formato inglés: el punto es el decimal y la coma solo agrupa millares («6,800» = 6800) →
  `test_guard_reads_point_as_decimal_and_comma_as_thousands`; `./check.sh` → `10 passed`.

## Evidencia
- `./check.sh` → `9 passed` (antes 4) y `OK -> out/index.html`, con el caso de Samantha por defecto.
- `test_brain_reads_every_real_case` pasa para las cuatro familias: nota igual a `published_score`, cinco pilares,
  ids de escena únicos y `guard.unsupported_numbers(...) == []`.
- `python -m finagent.run cases/<familia>/financial-health.json` (con `VOICE_ENGINE=mock`) → `OK` para Weah, Carter
  y Johnson.
- Narración observada (Weah): «Hello, Timothy and Melanie. Your financial health score is 60 out of 100. Sherpas
  calls that stable.» / «Insurance and protection: 7 out of 20 points.» / «Pay down revolving card. It takes your
  score from 60 to 62.»
- `grep -rn diagnostic_sample src tests check.sh CLAUDE.md AGENTS.md README.md` → sin resultados.
- **verify (14 nov, sobre `b17f188` + cambios sin commit):** `./check.sh` → `10 passed`, `OK -> out/index.html`;
  `compileall src contracts tests` → sin errores. `ruff` y `mypy`: HERRAMIENTA-AUSENTE (no instalados). Veredicto: PASA.

## Siguiente
Paso 2: hechos por familia y por persona (p. ej. el hueco de seguro de vida de Timothy y el de Melanie).
