---
created: 2026-11-16
status: done
branch: feat/voice-spanish
---
# FTD — Voz: escucharlo en español

- Dueño: David (`daviid-sc`)

## Intención
Muchas familias de EE. UU. hablan español en casa. El producto sigue en inglés (lo exigen las bases), pero el
recorrido tiene una segunda pista de audio: «Listen in: English | Español», con el texto en español debajo de cada
narración y los subtítulos iluminándolo (*Personal*, *Se entiende*).

## Alcance
- Entra: `src/finagent/spanish.py` (traducir, comprobar cifras, copia hablada, audio), `narrations/es/*.json`,
  1 línea en `run.py`, `web/spanish.js`, `web/captions.js` (pista `audio/es/`), 3 enganches en `stage_page.html`.
- NO entra: traducir la página, las respuestas de `/ask`, la nota de pareja ni la de los niños. El contrato no cambia.

## Decisiones
- **Traducción una sola vez y guardada** (`python -m finagent.spanish`, `deepseek-flash` por el proxy: céntimos).
  Cada entrada guarda la huella del inglés del que sale: si Samuel cambia una narración, esa escena se queda sin
  español hasta volver a ejecutar el comando (un test avisa: `test_the_saved_translations_match_today_s_narrations`).
- **Cifras:** la traducción solo vale si tiene exactamente los mismos números que el inglés (`same_figures`).
  Las 92 pasaron a la primera.
- **Copia hablada en español** (`to_speech_es`): importes y decimales en letras, porque están en formato de EE. UU.
  («$1,166,000») y en español la coma es el decimal.
- **Voz: edge `es-US-PalomaNeural` (gratis).** Comprobado con Scribe en las 7 escenas más difíciles: todo bien.
  Con Matilda (modelo rápido) en español se oyó «treinta y ocho» por «31» y un tartamudeo, así que ElevenLabs queda
  como opción (`SPANISH_VOICE_ENGINE=eleven`), no por defecto. Se gastaron ~16.000 caracteres en esa prueba.
- De paso: auditadas con Whisper las 92 escenas en inglés de Matilda → todas las cifras bien.

## Checklist
- [x] Tests sin red (9). `bash check.sh` pasa.
- [x] En el navegador (Johnson): el interruptor aparece, suena `audio/es/intro.mp3` y se ilumina el texto español.
- [ ] Oírlo en el iPhone de David.
- [ ] Decidir si se rehace la pista con Matilda (modelo multilingüe + todos los números en letras).

## Para Samuel y Raúl
- Samuel: `narrations/es/` es nuevo y no toca tus archivos. Si cambias narraciones: `python -m finagent.spanish`.
- Raúl: busca `spanish` en `stage_page.html` (carga del módulo, `play()` y `build()`).
