---
created: 2026-11-15
status: done
branch: feat/brain-llm-narration
---
# `brain`: narración escrita por un LLM, revisada por `guard`

- Dueño: Samuel (`Inmortal112`)

## Intención
Paso 3 de la parte de Samuel. La voz dice hoy frases de plantilla («Your roof is broken. Insurance and protection:
0 out of 20 points.»). Un modelo de texto, por el proxy de Sherpas, las reescribe para que suenen a una persona que
explica la casa, **con los mismos hechos**. `guard` revisa cada escena y la que cite un número que no esté en sus
hechos vuelve a la frase de plantilla.

## Alcance
- Entra: `src/finagent/narrator.py` (generar, validar, guardar y aplicar), `brain.py` (`build` aplica la narración
  guardada; `build_template` es lo de antes), `guard.py` (`spelled_numbers`), `narrations/<familia>.json` (las cuatro),
  `requirements.txt` (`openai`), `.env.example` (`BRAIN_MODEL`), tests.
- NO entra: el contrato; `/ask` y preguntas en vivo; registro de conversaciones; narración por persona o por modo
  (sencillo / completo); español; `voice.py` y `stage.py`.

## Decisiones
- **Se genera una vez por familia y se guarda en el repo** (`narrations/`): `./check.sh` y la demo no llaman al LLM,
  no gastan créditos y dan siempre el mismo texto. Se regenera a mano: `python -m finagent.narrator <familia>`.
- **`guard` vuelve a revisar al cargar**: si los hechos cambian y un texto guardado ya no cuadra, esa escena usa la
  plantilla. Nunca se rompe la tubería por la narración.
- **Una llamada por familia** con todas las escenas (el modelo ve el recorrido entero y no se repite); un reintento
  solo con las escenas rechazadas, diciéndole qué número sobraba.
- **Números escritos con letras** («seventy-three»): `guard` solo ve cifras, así que el narrador rechaza decenas,
  «hundred» y «thousand» escritos con letras.
- **Los importes del paso** (`top_moves[].action`, p. ej. «Pay $6,800 on the 18% card») pasan a ser un hecho de la
  escena del paso: así la narración puede decir qué hay que hacer, no solo cuánto sube la nota.
- **La explicación de Sherpas es un hecho de la escena** (`context_<parte>`, texto de `narrative.*` de esa área):
  la narración puede citar sus cifras («your $80,000 of cash covers 7.9 months») y `guard` las acepta solo en la
  escena de esa parte. Límite conocido: `guard` comprueba que el número existe, no que se use con su significado.
- Los dos importes con céntimos de la línea del tiempo se guardan en dólares enteros (Sherpas también los escribe así).
- Modelo: `gpt-5-mini` (`BRAIN_MODEL` en `.env`), barato para desarrollar (regla 8).

## Checklist
- [x] Narración guardada para las cuatro familias, todas las escenas aceptadas por `guard` → informe del generador.
- [x] `brain.build` usa la guardada y `guard.unsupported_numbers == []` en las cuatro → test.
- [x] Un texto guardado con un número inventado se sustituye por la plantilla → test.
- [x] Sin `narrations/` o sin clave, la tubería funciona igual con plantillas → test.
- [x] `./check.sh` pasa sin red hacia el LLM.
- [x] Gasto anotado (`/key/info`).

## Evidencia (2026-11-15)
- `python -m finagent.narrator <familia>` para las cuatro → 10, 10, 11 y 11 escenas escritas, `template kept for []`
  (ninguna rechazada tras el reintento). Unos 4.500 tokens de entrada y 7.000 de salida por familia, 2-3 min.
- `./check.sh` → `76 passed` (antes 67) y `OK -> out/index.html`; los tests no llaman al modelo.
- Texto observado (Samantha, cimientos): «These are your foundations, cash and emergency fund, and their state is
  solid. Foundations score 15 out of 15 and your $80,000 of cash covers 7.9 months of essential expenses…».
- Gasto (`/key/info`): `spend 0.134532` de `max_budget 50.0`, con tres tandas de generación (antes 0.0).
- **verify (15 nov, sobre `1d36866` + cambios sin commit):** `./check.sh` → `76 passed`, `OK`; `compileall src
  contracts tests` → sin errores. `ruff` y `mypy`: HERRAMIENTA-AUSENTE. Veredicto: PASA.
- Sin comprobar: nadie ha leído con calma ni escuchado los 42 textos. Vistos al pasar: frases algo largas, alguna
  afirmación discutible (Weah, tuberías: «the spare surplus is low confidence») y los cimientos de los Johnson salen
  `solid` (13/15) aunque su efectivo cubre 1,4 meses: el dato de Sherpas es así y la narración dice las dos cosas.
- edge-tts falló una vez de dos (`NoAudioReceived`) y la voz cayó a duraciones estimadas; al repetir funcionó.

## Siguiente
Samuel lee la narración de Samantha y Michael (las del pitch) y marca lo que no le convenza; después, backend `/ask`.
