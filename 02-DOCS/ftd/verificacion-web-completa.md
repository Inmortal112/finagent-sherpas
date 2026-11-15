---
created: 2026-11-15
status: done
branch: feat/stage-full-integration
---
# Comprobación de la web completa (toda la visita en la página)

- Dueño: Samuel (`Inmortal112`)

## Intención
La otra sesión terminó `feat/stage-full-experience` (`0259cfa`): modos, persona, preocupación, vuelta a los 3 días,
ficha del asesor e historial del chat, todo en la página. Esta rama la une con `main` (`f4adb96`) y comprueba la
visita entera en un navegador real, antes de subirla.

## Alcance
- Entra: la fusión; conflicto de `visitas/samuel.md`; un texto de plantilla en la narración sencilla de los Weah;
  una regla en las instrucciones de `/ask`; la comprobación.
- NO entra: cambiar la página; enlace público; micrófono real; iPhone.

## Checklist
- [x] `./check.sh` pasa con todo junto.
- [x] `finagent.run --all` genera las cuatro familias en los dos modos, con voz.
- [x] Visita entera en navegador: familia, persona, modo, preocupación, chat con seguimiento, recarga, paso,
  vuelta a los 3 días y ficha del asesor.
- [ ] Una persona la ha recorrido.

## Evidencia (2026-11-15, sobre `2218c98` + cambios sin commit)
- `./check.sh` → `153 passed`, `OK -> out/index.html`.
- `VOICE_ENGINE=edge python -m finagent.run --all` → 8 páginas en `out/families/<familia>/<modo>/`, 92 mp3,
  ninguno vacío, en 52 s.
- **Playwright, Chromium sin ventana, 390×844, servidor real en :8766. Trece pasos, todos bien, cero errores de
  consola:**
  1. `/` → nota 82.
  2. Cambiar a los Weah → `/families/timothy-melanie-weah/complete/`, nota 60.
  3. Opciones: «I am Timothy / Melanie / Guide me», «Simply / In full».
  4. Elegir Melanie y «Simply» → `/families/timothy-melanie-weah/simple/`.
  5. Preocupación «Our debts» → «Melanie, you have $93,000 in total debt, including an $18,000 credit card at 18%.»
  6. Chat: «How bad is the credit card?» → «It's at 18%, your costliest debt, but your debt overall is manageable.»
     (paredes).
  7. Seguimiento «and what should we do about it?» → el paso de la tarjeta, por su nombre («…, Melanie»).
  8. Recargar → el chat sigue ahí (historial recuperado).
  9. Elegir paso → «Chosen: Pay down revolving card. Your advisor will see it, and we check in with you in three days.»
  10. «Come back three days from now» → aviso del paso («Have you been able to start it?») y la fecha de enero de 2027.
  11. Ficha del asesor → persona y modo, preocupación, las dos preguntas, «the walls», paso elegido.
- **Visto y corregido:** la narración sencilla de `pillar_debt` de los Weah era la frase de plantilla tal cual
  (la escribió así el modelo; `guard` la aceptaba). Sustituida a mano por una frase sin cifras nuevas.
- **Visto y mejorado a medias:** una respuesta decía «That clears your costliest debt» (pagar $6,800 de $18,000 no
  la salda). Añadida una regla a las instrucciones de `/ask` («A step does only what its facts say…»). En cuatro
  preguntas reales después, tres respuestas correctas («that only pays part of it, so the debt isn't cleared») y
  una todavía dice «clears the costly revolving balance». La causa es el texto del propio paso («…to remove high
  revolving exposure and clear the gate»). `guard` no puede verlo: no es una cifra.
- `ruff` y `mypy`: HERRAMIENTA-AUSENTE. Veredicto: PASA, con lo de abajo.
- Sin comprobar: micrófono real, Safari / iPhone, cómo suena la voz, tamaño de escritorio en este recorrido (solo
  móvil), y el puerto 8000 (ver aviso).
- **Aviso:** en el puerto 8000 sigue un servidor antiguo (pid 398275, de las 12:08) con el mock viejo. Ninguna de
  las dos sesiones lo ha parado. La web buena está en `http://localhost:8001` (la dejó la otra sesión).

## Siguiente
Samuel para el servidor viejo del 8000 y recorre la web; decide si el paso de la tarjeta necesita un hecho nuevo
(«queda $11,200 por pagar») para que el modelo no diga que la salda.
