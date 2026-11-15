---
created: 2026-11-15
status: done
branch: feat/voice-stt
---
# FTD — Voz: pregunta hablada → texto (STT)

- Dueño: David (`daviid-sc`)

## Intención
En la casa, la familia mantiene pulsado el micrófono y pregunta. `/ask` (FastAPI, Samuel) necesita el texto de esa
pregunta antes del LLM. Raúl aún no ha decidido cómo graba en la página, así que la función acepta cualquier formato.

## Alcance
- Entra: `voice.transcribe_async(audio, filename, language="en") -> Transcript` (y `voice.transcribe`),
  `voice_eleven.transcribe` (Scribe, subida multipart hecha a mano), `tests/test_voice_stt.py`.
- NO entra: grabar en el navegador (Raúl), la ruta `/ask` (Samuel).

## Decisiones
- **ElevenLabs Scribe** (`scribe_v2`), mismas claves que la voz: `ELEVENLABS_API_KEY` (la clave de David necesita
  «De voz a texto → Acceso», activado el 15 nov) o, sin ella, `scribe-v2` por el proxy con `TEAM_KEY` ($0,22/hora).
- Acepta cualquier grabación del navegador (`webm`, `ogg`, `mp3`, `wav`, `m4a`): Scribe detecta el formato.
- Idioma fijado en inglés. Sin etiquetas de sonidos («(laughs)»). Tope de 10 MB por grabación.
- **Nunca lanza error**: si falla, no hay clave o no se dijo nada, `text=None` → la página pide escribir la pregunta.
- Sin dependencias nuevas (`urllib`).

## Checklist
- [x] 9 tests sin gastar: camino directo y proxy, nombre de archivo saneado, audio vacío o enorme, error, silencio, async.
- [x] Prueba real: mp3 de Matilda, mp3 de edge y un `webm` con Opus (el formato de Chrome).
- [x] `bash check.sh` pasa.

## Evidencia (2026-11-15, Windows 11)
- Las tres transcripciones coinciden con el texto original; 0,6–0,8 s cada una.
- El `webm` se hizo convirtiendo el mp3 de edge con PyAV (fuera del repo): no se ha probado aún con una grabación
  real de micrófono en el navegador.
