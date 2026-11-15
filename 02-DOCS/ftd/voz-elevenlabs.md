---
created: 2026-11-15
status: done
branch: feat/voice-elevenlabs
---
# FTD — Voz, fase 3: motor ElevenLabs para la demo

- Dueño: David (`daviid-sc`)

## Intención
edge-tts es gratis pero suena a lector; para la demo queremos la voz de ElevenLabs, sin poner en riesgo
el saldo del equipo ni el pipeline.

## Alcance
- Entra: `src/finagent/voice_eleven.py` (motor, caché, límite, duración del MP3), `voice.py` con
  `VOICE_ENGINE=eleven` y respaldo eleven → edge → mock, `.env.example`, `tests/test_voice_eleven.py`.
- NO entra: preguntas en directo (`/ask`, depende del backend), STT, elegir modelo `eleven_v3`.

## Decisiones
- **Dos caminos**: `ELEVENLABS_API_KEY` (cuenta de estudiante de David, plan Creator, 129.943 caracteres/mes)
  va directo a ElevenLabs; sin ella, `TEAM_KEY` + `LLM_PROXY_URL` por el proxy de Sherpas (los $1,40 del equipo).
- **Sin dependencias nuevas**: `urllib` de la biblioteca estándar. `requirements.txt` no cambia (no hace falta `openai`).
- **Gasto**: caché por huella de (camino, modelo, voz, texto) en `out/voice_cache/`; `ELEVEN_MAX_CHARS` (6000 por
  ejecución, solo lo no cacheado); edge sigue siendo el motor por defecto.
- **Duración**: ElevenLabs devuelve MP3 de 128 kbit/s constantes; se lee el bitrate de la cabecera del primer frame.
- Modelo por defecto `eleven_flash_v2_5` (el más barato y rápido). Voz por defecto: Matilda (premade).

## Checklist
- [x] 8 tests con la llamada HTTP simulada (camino directo, proxy, caché, límite, sin clave, error del servicio, duración).
- [x] Prueba real: la bienvenida de Samantha con Matilda, Sarah y Eric (`out/voices/`).
- [x] Duración calculada frente a la decodificada con PyAV: 5,72/5,67 · 5,28/5,20 · 4,65/4,60 s (≤ 0,08 s).
- [x] David elige la voz: **Matilda** (comparada con Sarah, Eric, Bella, Chris y Bill).
- [x] Familia entera de Samantha con Matilda: 10 escenas, 70,2 s, 870 caracteres enviados; `intro` salió de la caché.

## Evidencia (2026-11-15, Windows 11)
- `pytest -q tests/test_voice_eleven.py` → 8 passed; `bash check.sh` → 75 passed.
- Contador de la cuenta: 120 caracteres tras ~1.400 enviados; se actualiza con retraso. Volver a mirarlo.

## Siguiente
Generar las cuatro familias con `VOICE_ENGINE=eleven` para la demo; voz de las respuestas de `/ask` cuando exista el backend.
