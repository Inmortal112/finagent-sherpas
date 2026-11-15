---
created: 2026-11-15
status: done
branch: feat/voice-speak
---
# FTD — Voz para las respuestas en directo (`/ask`)

- Dueño: David (`daviid-sc`)

## Intención
Acordado con Samuel (15 nov): el backend es FastAPI con una ruta `/ask`. Cuando la familia pregunta, la respuesta
(LLM → `guard`) tiene que volver hablada. `synthesize` trabaja con una `Presentation` entera; hace falta una función
de un solo texto que la ruta pueda llamar.

## Alcance
- Entra: `voice.speak_async(text, language="en") -> SpokenAudio` (y `voice.speak` para código no async),
  `_edge_bytes` (la llamada a edge-tts, compartida con `synthesize`), `tests/test_voice_speak.py`.
- NO entra: la ruta `/ask` ni FastAPI (Samuel), grabar el micrófono (Raúl), STT.

## Decisiones
- `SpokenAudio(audio, duration_s, engine)`: MP3 en bytes, duración y el motor que habló.
- **Nunca lanza error**: si ningún motor puede hablar, `audio=None` y `engine="mock"`; la página muestra el texto.
- Mismos motores y respaldos que la presentación (eleven → edge → mock), mismo `to_speech`, misma caché y tope.
- En FastAPI: `spoken = await voice.speak_async(answer)` y `Response(spoken.audio, media_type="audio/mpeg")`.
  `voice.speak` usa `asyncio.run` y no vale dentro de una ruta async.

## Checklist
- [x] 5 tests sin gastar: ElevenLabs con la copia hablada, caché, respaldo a edge, sin motor, dentro de un bucle async.
- [x] Prueba real con frases del caso de Samantha.
- [x] `bash check.sh` pasa.

## Evidencia (2026-11-15, Windows 11)
- Frase nueva (196 caracteres, con markdown) con ElevenLabs: 12,8 s de audio en **0,78 s**.
- Misma frase ya generada: 0,005 s desde la caché. edge-tts, 67 caracteres: 1,49 s.
