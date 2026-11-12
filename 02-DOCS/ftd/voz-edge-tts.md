# FTD — Voz real con edge-tts

- Fecha: 2026-11-12 · Rama: `feat/voice-edge-tts` · Dueño: David (`daviid-sc`)

## Intención

Sustituir el mock de `voice.synthesize` por audio real: un MP3 por escena y su duración medida, para que la escena pueda sincronizar diapositivas con la voz.

## Alcance

- Dentro: motor `edge` (voces neuronales de Microsoft, gratis, sin clave), elección por `.env` (`VOICE_ENGINE`, `VOICE_NAME`), respaldo automático al mock si falla la red.
- Fuera: normalizar números para la lectura (fase 2), motor de OpenRouter (fase 3), pausas y elección final de voz (fase 4).

## Decisiones

- `audio_path` es relativo a `out_dir` (`audio/<scene_id>.mp3`), para que `index.html` lo cargue a su lado.
- `duration_s` se calcula a partir del tamaño del archivo: edge-tts devuelve MP3 de 48 kbit/s constantes. No hace falta ninguna dependencia extra.
- Si el motor falla, aparece un aviso y se usan duraciones estimadas con `audio_path = None`: `main` sigue funcionando sin internet.
- `narration` no se modifica nunca (`test_voice_does_not_change_what_is_said`).
- Cambio en un archivo compartido: `requirements.txt` (+ `edge-tts`, `python-dotenv`). Necesita el visto bueno de Samuel.

## Checklist

- [x] Los 4 tests pasan con la voz real.
- [x] `finagent.run` genera `out/audio/*.mp3` y rellena `audio_path` y `duration_s`.
- [x] La duración por tamaño coincide con el final del habla que reporta edge-tts (diferencia de 0,1 s o menos en las 4 escenas).
- [x] Sin red: aviso, `audio_path = None`, duraciones estimadas, y el pipeline no se rompe.
- [ ] Escuchado por una persona: pronunciación de cifras como "14.0 %" (pasa a la fase 2).
- [ ] La escena (Raúl) reproduce `audio_path`. Hoy el mock de `stage.py` no lo usa.

## Evidencia (2026-11-12, Windows 11, Python 3.14.6)

- `pytest -q tests` (con `PYTHONPATH=src;.` y `PYTHONUTF8=1`): 4 passed en 2,98 s.
- Duraciones (tamaño / fin del habla): intro 6,1/6,01 · savings_rate 3,7/3,73 · emergency_fund_months 3,9/3,94 · debt_to_income 4,3/4,26.
- Prueba sin red (proxy roto): `ConnectionTimeoutError` → respaldo correcto.
- No verificado: `./check.sh` en Linux o Mac. En Windows falla por motivos previos a esta rama (separador de `PYTHONPATH` y lectura sin UTF-8 en los tests), ya avisado a Samuel.
