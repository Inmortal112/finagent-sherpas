---
created: 2026-11-16
status: done
branch: feat/voice-house-sound
---
# FTD — Voz: la casa suena

- Dueño: David (`daviid-sc`)

## Intención
Que la casa se sienta, no solo se vea: lluvia suave cuando la nota es baja, pájaros cuando está sana y un «ding» al
marcar un paso hecho. Pedido por David: **fondo bajito, que la voz se oiga siempre bien.**

## Alcance
- Entra: `src/finagent/web/house_sound.js` (nuevo) y 6 líneas en `stage_page.html` (cargarlo, `setWeather` en
  `paint()`, `repaired()` en `markDone()`, `setEnabled()` en el botón de sonido). Sección en `VOICE.md`.
- NO entra: tocar `house3d.js`. Sonidos grabados (si los generados no convencen, se cambian sin tocar la página).

## Decisiones
- **Generados con Web Audio API**: sin archivos, sin licencias, gratis y con el volumen exacto.
- Misma escala que el cielo 3D (`healthOf(score)`): lluvia hasta 0,6 (~61 puntos), pájaros desde 0,55.
- **Niveles medidos** contra una narración real (render offline en el navegador): lluvia máxima −30 dB respecto a la
  voz; **ducking** (bajar el fondo mientras habla la voz) −9 dB más; «ding» −19 dB bajo los picos de la voz.
  Primera versión a −21 dB: se notaba demasiado y se bajó.
- Arranca con el primer toque (iPhone lo exige), se para con la pestaña oculta, el botón de sonido lo apaga todo.

## Checklist
- [x] Medición de niveles con la peor nota, media y alta (con nota alta no llueve).
- [x] En la página: «I've done this» suena y la lluvia baja (Michael 26 → 31); el botón de sonido lo apaga; sin errores.
- [ ] Escucharlo en el iPhone de David.
- [x] `bash check.sh` pasa.

## Para Raúl
Tus cambios sin subir tocan la misma página. Si chocan, solo son estas 6 líneas: búscalas por `houseSound`.
