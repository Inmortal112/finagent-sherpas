---
created: 2026-11-16
status: done
branch: feat/voice-calendar
---
# FTD — El primer paso en su calendario

- Dueño: David (`daviid-sc`)

## Intención
Que el paso elegido no se quede en la página: botón «Add to my calendar» que mete dos eventos en el calendario real
de la familia (*Mueve a actuar*). Mañana a las 10:00 «First step: …» con lo que hay que hacer, y el día 3 a las 10:00
«Look at your home again» con el enlace de vuelta a su página, donde espera la pregunta del día 3.

## Alcance
- Entra: `src/finagent/calendar_invite.py` (nuevo), ruta `GET /calendar/{sesión}.ics?day=&mode=` en `server.py`,
  función `addToCalendar()` y una llamada en `chooseStep` de `stage_page.html`. Tests `test_calendar_invite.py`.
- NO entra: tocar sesiones ni el contrato.

## Decisiones
- Archivo `.ics` (iCalendar, el estándar de calendarios) servido por el servidor, no creado en la página: así el iPhone
  abre su ventana «Añadir al calendario» con un simple enlace.
- Hora «flotante» (sin zona horaria): las 10:00 allí donde esté la familia. La página manda su fecha de mañana.
- Sin cifras ni modelo: el título del paso y sus «first moves» de `house.py`. Aviso 15 min antes.
- La página manda su modo (`simple`/`complete`) para que el enlace de vuelta abra el mismo.

## Checklist
- [x] Tests sin red (5): fechas, formato estándar (líneas ≤ 75 bytes, CRLF, comas escapadas), sin cifras, rutas.
- [x] En el navegador (Michael, sencillo): botón visible, archivo con los dos eventos y enlace al modo sencillo.
- [ ] Abrirlo en el iPhone de David («Añadir al calendario»).
- [x] `bash check.sh` pasa.

## Para Raúl
`addToCalendar()` en `stage_page.html` añade un enlace con tu clase `pill dark` dentro de `#firstMove`.
