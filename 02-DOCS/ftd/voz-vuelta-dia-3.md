---
created: 2026-11-16
status: done
branch: feat/voice-welcome-back
---
# FTD — Voz: la vuelta del día 3 habla

- Dueño: David (`daviid-sc`)

## Intención
Cuando la familia vuelve, la casa saluda en voz alta y pregunta por su paso, en vez de esperar a que lean un texto
(*Mueve a actuar*): «Welcome back, Emily. A few days ago you chose a first step: … Have you been able to start it?»

## Alcance
- Entra: `src/finagent/welcome_back.py` (nuevo), `GET /reminders` devuelve además `spoken` y `audio_url`, ruta nueva
  `GET /reminders/{session}.mp3`, 2 líneas en `stage_page.html` (`comeBack`). Tests `test_welcome_back.py`.
- NO entra: cambiar los textos de `sessions.reminders` (son de Samuel): solo se les pone el saludo delante.

## Decisiones
- Frases fijas, sin modelo y sin cifras nuevas: saludo + pregunta por su paso + como mucho una fecha del plan.
- La ruta de audio solo dice los avisos de esa sesión (no hay ruta que lea texto libre: nadie puede gastar voz con ella).
- Audio guardado por texto (`data/sessions/audio/<sesión>-back-<hash>.mp3`), como la nota para la pareja.
- `person` opcional en la petición: `/decision` no guarda quién usa la página, y la página sí lo sabe.

## Checklist
- [x] Tests sin red (5).
- [x] En el navegador (Johnson): al pulsar «Come back three days from now» suena la voz y sale el texto.
- [ ] Oírlo en el iPhone de David.
- [x] `bash check.sh` pasa.

## Para Samuel y Raúl
`/reminders` solo añade dos campos; lo que ya devolvía no cambia. En la página, busca `audio_url` dentro de `comeBack`.
