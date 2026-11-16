---
created: 2026-11-16
status: done
branch: feat/voice-captions
---
# FTD — Voz: subtítulos que siguen a la voz

- Dueño: David (`daviid-sc`)

## Intención
Que cada palabra de la narración se ilumine en la página mientras la voz la dice (*Se entiende*, modo sencillo,
gente que oye mal o está en un sitio con ruido). Queda muy bien en el vídeo.

## Alcance
- Entra: `src/finagent/captions.py` (nuevo), tiempos por palabra en `voice.py` (edge) y `voice_eleven.py`
  (ruta `with-timestamps`), `web/captions.js` (nuevo) y 2 líneas en `stage_page.html`. Tests `test_captions.py`.
- NO entra: el contrato (`schemas.py`): el archivo de tiempos va junto al MP3 (`audio/<escena>.words.json`) y la
  página lo deduce de `audio_path`. Subtítulos en las respuestas de `/ask`.

## Decisiones
- **Se ilumina el texto escrito, sin cambiarlo.** La voz lee la copia hablada (`to_speech`); `captions.align` empareja
  palabras dichas y escritas (`difflib`): «$15,032/yr» se ilumina mientras se dice «…dollars a year».
- ElevenLabs: misma petición y mismo precio, pero devuelve audio + tiempos por carácter; se guardan en la caché
  junto al MP3. Por el proxy de Sherpas no hay tiempos: se estiman por longitud de palabra.
- En la página, un temporizador (25 veces por segundo) en vez de `requestAnimationFrame`: sobra para palabras.
- Sin archivo de tiempos (voz mock, audios viejos) no hay subtítulos y todo lo demás funciona igual.

## Checklist
- [x] Tests sin red (8): alineación, cifras, estimación, edge y ElevenLabs falsos.
- [x] En el navegador (Michael, edge): «Hello,» → «Michael.» → «want» → … al ritmo de la voz; se apaga al parar.
- [ ] Verlo en el iPhone de David.
- [ ] Probar la ruta `with-timestamps` real de ElevenLabs (al regenerar con Matilda).
- [x] `bash check.sh` pasa.

## Para Raúl
2 líneas en `stage_page.html` (busca `captions.js`). El color del resaltado está en `web/captions.js` (`STYLE`).
