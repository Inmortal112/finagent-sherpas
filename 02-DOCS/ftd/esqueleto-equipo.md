# FTD — Esqueleto de equipo (contrato + tres etapas con mocks)

- Fecha: 2026-11-11 · Rama: `main`

## Intención

Que las tres personas (y sus IA) puedan trabajar en paralelo e integrar desde el primer día. En València Futura el trabajo de un compañero no llegó a fusionarse: sin permiso de escritura, un único `app.py` y sin contrato.

## Alcance

- Dentro: contrato `Presentation`, etapas `brain` / `guard` / `voice` / `stage` como mocks, `AGENTS.md`, `check.sh`, repo con acceso para los tres.
- Fuera: producto real (MCP, LLM, voz, avatar, reproductor). Empieza tras el kick-off del 12 nov.

## Checklist

- [x] El pipeline completo se ejecuta con un comando → `./check.sh`.
- [x] Un número que no está en el diagnóstico corta la ejecución → `test_guard_blocks_a_number_that_is_not_in_the_diagnostic`.
- [x] El JSON Schema publicado coincide con el código → `test_published_schema_matches_the_code`.
- [x] Los pasos del README funcionan en una copia limpia (venv nuevo).
- [ ] Repo remoto con permiso de escritura para los tres, y cada uno ha hecho un push de prueba.
- [ ] Sustituir `fixtures/diagnostic_sample.json` (inventado) por un diagnóstico real del MCP.

## Evidencia (2026-11-11, antes del commit inicial; árbol sin commits)

- `pytest -q tests`: 4 passed.
- `python -m compileall -q src contracts tests`: sin errores.
- `./check.sh` en el repo y en una copia limpia con venv nuevo (Linux, Python 3.13.7): 4 passed y `OK -> out/index.html`.
- HERRAMIENTA-AUSENTE: `ruff` y `mypy` no están instalados; no se ejecutó lint ni tipos.
- No verificado: Windows (el equipo de Raúl) ni la carga de `AGENTS.md` por Astra.

## Siguiente paso

Cada compañero clona, ejecuta `./check.sh` y hace un push de prueba a una rama antes del kick-off.
