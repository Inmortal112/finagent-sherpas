---
created: 2026-11-16
status: done
branch: feat/voice-kids
---
# FTD — Voz: la casa explicada a los niños

- Dueño: David (`daviid-sc`)

## Intención
El reto pide que sea personal «para la familia y cada miembro», y nadie explica el plan a los hijos. La casa se lo
explica a ellos, por su nombre, en unos 30-40 segundos y con palabras de su edad (*Personal*, *Creatividad*).

## Alcance
- Entra: `src/finagent/kids_note.py` (nuevo), `GET /kids-note` y `GET /kids-note/{familia}.mp3` en `server.py`,
  `offerKidsNote()` y una llamada en `stage_page.html`. Tests `test_kids_note.py`.
- NO entra: el contrato ni lo de Samuel (los datos salen de la escena `intro`: personas y estado de cada parte).

## Decisiones
- Familias con hijos: Johnson (Oliver 11, Sophia 9), Weah (Liam 6, Josh 3), Samantha (Ethan 18, Ava 16). Michael, no.
- Dos tonos: niños, y adolescentes (todos con 13 o más; Samantha). Solo las 2 partes más dañadas (rotas primero).
- Sin cifras y **sin «mom»/«dad»**: los datos no dicen quién es quién; se habla de «your family».
- Frases fijas, sin modelo: el texto es siempre el mismo por familia → un solo audio por familia (seguro con enlace público).

## Checklist
- [x] Tests sin red (7): nombres, tonos, sin cifras ni pronombres de género, longitud, rutas y caché.
- [x] En el navegador: botón en Johnson y Samantha, no en Michael; suena 34,8 s y un segundo toque lo para.
- [ ] Oírlo en el iPhone de David.
- [x] `bash check.sh` pasa.

## Para Raúl
`offerKidsNote()` en `stage_page.html` añade una fila `.seg` «For the children» debajo de «Guide me».
