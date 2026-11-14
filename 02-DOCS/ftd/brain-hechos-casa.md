---
created: 2026-11-15
status: done
branch: feat/brain-house-facts
---
# `brain` entrega los hechos de la casa por familia

- Dueño: Samuel (`Inmortal112`)

## Intención
Paso 2 de la parte de Samuel en Under One Roof. Hoy `brain` solo da la nota, los cinco pilares y los `top_moves`.
Raúl no puede dibujar la casa con eso: le falta saber qué parte es cada pilar, en qué estado está, qué parte arregla
cada paso y qué pasa con los años. Este cambio lo añade, todavía con frases de plantilla (sin LLM).

## Alcance
- Entra: `src/finagent/house.py` (nuevo: partes, estados, paso → parte, línea del tiempo), `brain.py` (hechos y
  `visual.data` nuevos, escenas `all_moves` y `timeline`), `tests/test_house.py`.
- NO entra: el contrato (`contracts/schemas.py` no cambia: todo va en `Fact` y en `visual.data`, que es un `dict`
  libre); LLM; `/ask`; registro de conversaciones; hechos por persona más allá de nombre, papel y edad (seguros y
  cuentas de cada uno: paso siguiente); `investment-analysis.json`; `stage.py` y `voice.py`.

## Decisiones
- **Parte de cada pilar** (tabla acordada en `idea-david.md`, nombres en inglés de `nota-idea.md`): Liquidity →
  `foundations`, Insurance → `roof`, Debt → `walls`, Savings and cash flow → `plumbing`, Investments → `garden`.
- **Tres estados** (`solid` / `cracked` / `broken`) según `score.pillars[].score` (0-100, de Sherpas): ≥ 70 sólido,
  ≥ 40 con grietas, menos roto. Los umbrales son nuestros (Sherpas no publica bandas por pilar): constantes en
  `house.py`, elegidas para que salgan los ejemplos de la idea (Johnson sin tejado, Weah con paredes agrietadas,
  Michael con tuberías rotas). El estado es un `Fact` con `source` que lo dice.
- **Paso → parte** por palabras del título (`cover` → tejado, `card` → paredes…). Si un título nuevo no encaja,
  la parte es `None` y el test de los cuatro casos lo detecta.
- **Línea del tiempo** solo con lo que hay: `projections.yearly` (patrimonio, deuda, activos invertibles), edades de
  jubilación y `key_metrics.facts.retirement` (`savingsRunOut` o `savingsLeftAtPlanEnd`). No hay proyección «si
  reparas»; el final reparado es la nota de `combined_moves`.
- **Nunca saldo negativo**: la nota de `savingsRunOut` lo prohíbe, así que los activos invertibles de la serie se
  cortan en 0 y la narración dice a qué edad se acaban.
- **Casa reparada** (`all_moves`): la combinación de `combined_moves` con más nota; si empatan, la más corta
  (Johnson: dos pasos dan 60 y el tercero no suma). Samantha y Michael no tienen combinaciones: sin escena.
- Los ids de escena existentes no cambian (son los nombres de los mp3 de David).

## Checklist
- [x] Las cinco partes con estado, para las cuatro familias → test parametrizado.
- [x] Los estados coinciden con los ejemplos de la idea (Johnson, Weah, Michael, Samantha) → test.
- [x] Cada `top_move` de los cuatro casos tiene parte → test.
- [x] Línea del tiempo: Samantha se queda sin ahorros a los 73 y Michael a los 85; Weah y Johnson no → test.
- [x] `guard` no encuentra números sin respaldo en ninguna escena nueva → test.
- [x] `./check.sh` pasa.

## Evidencia (2026-11-15)
- `./check.sh` → `67 passed` (antes 37) y `OK -> out/index.html` (Samantha, con edge-tts).
- `VOICE_ENGINE=mock python -m finagent.run cases/<familia>/financial-health.json` → `OK` para Carter, Weah y Johnson.
- Casas: Johnson `roof: broken`; Weah `walls: cracked`, `roof: broken`; Michael `plumbing`, `foundations` y `roof`
  `broken`, `walls: solid`; Samantha todo `solid` salvo `garden: cracked`.
- Línea del tiempo: Samantha se jubila a los 65 (2044) y se queda sin ahorros a los 73 (2052); Michael, 58 (2047) y
  85 (2074); Weah y Johnson llegan al final del plan. Sin deuda desde 2059 (Samantha, Weah), 2057 (Michael), 2047 (Johnson).
- Narración observada (Samantha): «Your garden is cracked. Investments: 10 out of 15 points.» / «Now look ahead. You
  plan to retire at 65. On the current plan, your savings and investments run out at age 73. The plan has your debts
  paid off by 2059.» Weah: «Done together, Pay down revolving card, Add life cover and Add umbrella cover take your
  score from 60 to 78.»
- `guard.unsupported_numbers(...) == []` en las cuatro familias (test).
- Sin comprobar: cómo suenan las frases nuevas (no he escuchado los mp3) y la lectura que haga `stage` real de
  `visual.data` (el mock solo usa `fact_id`).
- **verify (15 nov, sobre `444a3e2` + cambios sin commit):** `./check.sh` → `67 passed`, `OK -> out/index.html`;
  `compileall src contracts tests` → sin errores. `ruff` y `mypy`: HERRAMIENTA-AUSENTE (no instalados). Veredicto: PASA.

## Siguiente
Narración con LLM por el proxy (necesita `.env` con `TEAM_KEY` y `openai` en `requirements.txt`), pasada por `guard`.
