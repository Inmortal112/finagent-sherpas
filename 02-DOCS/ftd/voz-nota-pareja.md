---
created: 2026-11-16
status: done
branch: feat/voice-partner-note
---
# FTD — Voz: nota de voz para la pareja

- Dueño: David (`daviid-sc`)

## Intención
En una pareja, muchas veces solo uno recorre el plan y nada se lo lleva al otro (las parejas son uno de los atascos
del README de Sherpas). Al elegir un paso, quien lo ha visto manda a su pareja una nota de voz de unos 15 s, como un
audio de WhatsApp: qué le preocupa y qué paso eligió, con la nota antes y después.

## Alcance
- Entra: `src/finagent/partner_note.py`, dos rutas en `server.py` (`GET /partner-note`, `GET /partner-note/{id}.mp3`),
  `tests/test_partner_note.py`, sección en `VOICE.md`.
- NO entra: el botón «Send to …» de la página (`stage_page.html`, de Raúl, que tiene cambios sin subir). Cuando
  suba: pedir la nota tras `/decision` y pasar el MP3 a `navigator.share({files})` en el iPhone.

## Decisiones
- **Frases fijas, sin modelo**, como los recordatorios del día 3: gratis, al instante y sin inventar nada.
- Solo dos cifras: la nota del paso antes y después (hechos del plan). La preocupación son palabras de la familia:
  se quitan sus números con `sessions.FIGURE`, y si trae uno escrito con letras («fifty thousand») se omite.
- Sin pronombres: siempre el nombre («Daniel's biggest worry»), para no suponer el género de nadie.
- Solo parejas (dos adultos en el caso). Samantha y Michael: `available: false` con el motivo, sin error.
- Quién la manda: la persona de la sesión o `?person=` (la página siempre lo sabe; `/decision` no lo guarda).
- El MP3 se guarda por texto (hash): un paso nuevo o «ya lo empecé» genera otro.

## Checklist
- [x] 10 tests sin red: texto exacto, solo cifras del plan, preocupación con números, cada adulto a su pareja,
  «ya lo empezó», familias de una persona, sin paso, sin remitente, rutas y caché del audio.
- [x] Prueba real con el servidor y edge-tts: nota de los Johnson, transcrita con Whisper palabra por palabra (15,5 s).
- [x] `bash check.sh` pasa.
