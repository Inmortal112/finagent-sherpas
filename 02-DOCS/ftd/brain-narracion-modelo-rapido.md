---
created: 2026-11-15
status: done
branch: feat/brain-narration-fast-model
---
# Narración: de `gpt-5-mini` a `deepseek-flash`

- Dueño: Samuel (`Inmortal112`)

## Intención
Samuel pide que la narración de las familias deje de usar `gpt-5-mini` y use uno de los dos modelos rápidos de
`/ask` (`deepseek-flash` o `gemini-3.5-flash-lite`). Así el producto usa un solo modelo de texto en todas partes.

## Alcance
- Entra: `narrator.py` (`DEFAULT_MODEL`), `.env.example` (`BRAIN_MODEL`), `narrations/<familia>.json` (las cuatro,
  **regeneradas** con el modelo nuevo), esta ficha y `visitas/samuel.md`.
- NO entra: `ask.py` (ya usa `deepseek-flash`), el contrato, `voice`, `stage`. `BRIEF.md` y `02-DOCS/reto.md`
  citan `gpt-5-mini` en ejemplos y en la tabla de precios de Sherpas: no son configuración nuestra y no se tocan.
  Las fichas y entradas antiguas que nombran `gpt-5-mini` son historia y se quedan como están.

## Decisiones
- **`deepseek-flash`**, no `gemini-3.5-flash-lite`: es el que ya responde en `/ask` y su salida es la más barata
  ($1,20 por millón de tokens, frente a $2,50).
- **Se regenera, no se cambia la etiqueta.** El campo `model` de cada JSON dice qué modelo escribió ese texto.
  Cambiar solo la palabra dejaría un registro falso: el texto seguiría siendo de `gpt-5-mini`.
- **Aviso:** la narración se genera una vez y se guarda, así que la velocidad del modelo no se nota en la demo.
  Lo que cambia con este paso son los textos que oye el jurado.

## Checklist
- [x] Las cuatro familias regeneradas con `deepseek-flash`, con el número de escenas aceptadas por `guard`.
- [x] `./check.sh` pasa.
- [x] Gasto anotado.
- [ ] Una persona ha leído o escuchado los textos nuevos.

## Evidencia (2026-11-15)
- `python -m finagent.narrator --all` con `deepseek-flash` → Johnson 11 escenas, Carter 10, Lewis 10, Weah 11;
  `template kept for []` en las cuatro (ninguna rechazada por `guard`). Máximo 60 palabras por escena.
- **Tiempo: 8 min 27 s las cuatro** (unos 2 min por familia). No es más rápido que `gpt-5-mini` (2-3 min por
  familia): `deepseek-flash` es rápido en respuestas cortas, pero aquí escribe entre 8.000 y 11.500 tokens de salida.
- **Gasto** (`/key/info`): de `0.199` a `0.307` → **$0,108** esta tanda. Tokens: unos 4.500 de entrada y entre
  8.277 y 11.560 de salida por familia (con `gpt-5-mini`, unos 7.000 de salida).
- Texto observado (Samantha, intro): «Hello Samantha. Your financial health score is 82 out of 100, a strong
  result. Over the next few scenes you will see your plan as a home…». Línea del tiempo: «…you plan to retire at 65,
  and on the current plan your savings and investments run out at age 73.»
- **verify (15 nov, sobre `c8581fa` + cambios sin commit):** `./check.sh` → `110 passed`, `OK -> out/index.html`
  (Samantha, con los textos nuevos y sus mp3 de edge-tts); `compileall src contracts tests` → sin errores.
  `ruff` y `mypy`: HERRAMIENTA-AUSENTE. Veredicto: PASA.
- Sin comprobar: nadie ha leído con calma ni escuchado los 42 textos nuevos. Las versiones anteriores
  (`gpt-5-mini`) están en el historial de git (`c8581fa`).

## Siguiente
Samuel lee la narración nueva de Samantha y Michael (las del pitch). Si no convence, se vuelve atrás con
`git revert` de este commit: no cuesta créditos.
