---
created: 2026-11-15
status: done
branch: feat/brain-ask
---
# Backend: preguntas en vivo (`/ask`), historial y ficha del asesor

- Dueño: Samuel (`Inmortal112`)

## Intención
La familia puede parar la narración y preguntar. Hace falta un servidor: la `TEAM_KEY` no puede estar en la página
y hasta hoy solo generábamos un HTML fijo. El servidor responde con los hechos del plan, guarda cada pregunta para
que la familia pueda volver a verla y da al asesor una ficha con lo que preguntaron y decidieron.

## Alcance
- Entra: `src/finagent/ask.py` (pregunta → escena y respuesta, con `guard`), `sessions.py` (historial en archivos),
  `server.py` (FastAPI), `tests/test_ask.py`, dependencias (`fastapi`, `uvicorn`, `python-multipart`, `httpx`),
  `.env.example`, `data/` en `.gitignore`.
- NO entra: la página (Raúl), el micrófono, cuentas de usuario, base de datos, despliegue en internet, avisos del
  día 3, el contrato `Presentation` (no cambia).

## Rutas
| Ruta | Qué hace |
|---|---|
| `GET /families` | Las cuatro familias con nombre, nota y banda |
| `GET /presentation/{family}` | Hechos y escenas (`Presentation`) |
| `POST /ask` | Formulario: `family`, `question` (texto) o `file` (grabación), `session_id` opcional → respuesta |
| `GET /history?session_id=` | Todas las preguntas y respuestas de la sesión, en orden |
| `POST /decision` | JSON `{family, scene_id, session_id}`: el paso que eligen (`move_N`) |
| `GET /advisor-note?session_id=` | Preguntas, partes más preguntadas, lo que el plan no cubre y el paso elegido |
| `GET /answers/{session}/{turn}.mp3` | La respuesta hablada (se genera en la primera petición y se guarda) |
| `GET /try` | Página sencilla para el equipo: preguntar, ver el historial y la ficha del asesor |

Respuesta de `/ask`: `session_id`, `turn_id`, `asked_at`, `question`, `text`, `scene_id`, `house_part`, `fact_ids`,
`source` (`model` / `approved_narration` / `off_plan` / `unavailable`), `heard_from`, `audio_url`.

## Decisiones
- **Una sola llamada al modelo** (elige escena y responde), no dos: la mitad de espera. `guard` revisa la respuesta
  contra los hechos de la escena elegida; si falla, un reintento y después la narración ya aprobada de esa escena.
- **Modelos rápidos**: `deepseek-flash`, con `gemini-3.5-flash-lite` de respaldo si tarda más de 8 s. `gpt-5-mini`
  tardó 11-28 s por respuesta: no sirve en vivo.
- **El texto no espera a la voz**: `/ask` devuelve el texto y `audio_url`; el mp3 se genera cuando la página lo pide.
  Con la voz dentro de `/ask`, una respuesta tardaba 13-32 s (edge-tts).
- **Fuera del plan** (cripto, predicciones): frase fija, sin cifras, y la pregunta queda apuntada para el asesor.
- **Historial en archivos JSON**, uno por sesión (`data/sessions/`, fuera de git). La sesión es una persona en un
  dispositivo; la página guarda el `session_id` y lo manda en cada pregunta.
- `/ask` no lanza errores por culpa del modelo: sin clave o sin red responde «ask me again in a moment».

## Checklist
- [x] Respuesta con hechos de la escena → aceptada; número inventado → reintento y narración aprobada → tests.
- [x] Una cifra de otra parte de la casa se rechaza → test.
- [x] Fuera del plan → frase fija → test.
- [x] Historial: dos preguntas en la misma sesión se leen después en orden, con su audio → test.
- [x] Ficha del asesor con partes, preguntas no cubiertas y decisión → test.
- [x] Pregunta hablada: se transcribe antes; silencio → 422 con mensaje → test.
- [x] Rutas con ids raros (`../etc`) → 404 → test.
- [x] Servidor real con preguntas reales → medido.
- [x] `./check.sh` pasa sin llamar al modelo.

## Evidencia (2026-11-15)
- `./check.sh` → `109 passed` (antes 98) y `OK -> out/index.html`.
- Servidor real (`uvicorn`, puerto 8765), Michael: «Why does my garden dry up?» 4,0 s; «How much do I owe?» 2,8 s;
  «Is my roof ok?» 2,6 s. Samantha: «Why does my garden dry up?» → `timeline`, `garden`: «Your savings and investments
  run out at age 73, after you retire at 65…»; «Should I put my money in crypto?» → `off_plan`; «What should I do
  first?» → `move_1`, `roof`. `/history` devolvió los tres turnos en orden; `/advisor-note`, `asked_most_about:
  ["garden", "roof"]` y la decisión `move_1`; el mp3 de `t1` se sirvió (127 584 bytes, `audio/mpeg`).
- **verify (15 nov, sobre `656e78b` + cambios sin commit):** `./check.sh` → `109 passed`, `OK`; `compileall src
  contracts tests` → sin errores. `ruff` y `mypy`: HERRAMIENTA-AUSENTE. Veredicto: PASA.
- Añadido después: página `/try` (`try_page.html`) → `GET /try` 200, `text/html`; `./check.sh` → `110 passed`.
  Su JavaScript no se ha probado en un navegador desde aquí.
- Sin comprobar: pregunta hablada con una grabación real del micrófono (solo con un doble en el test); la página de
  Raúl llamando a estas rutas; varias personas a la vez.

## Siguiente
Raúl conecta la página a `/ask` y `/history`. Samuel: hechos por persona (pareja) y modo sencillo / completo.
