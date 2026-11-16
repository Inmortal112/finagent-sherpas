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
- [x] Escucharlo en el iPhone de David (16 nov): va fluido, pero **la lluvia no sonaba a lluvia** (era ruido rosa
  filtrado: un «shhh» continuo).
- [x] Lluvia rehecha con gotas (rama `feat/voice-rain-drops`): bucle estéreo de 8 s con ~320 golpecitos/s por oído,
  ~5 «plics» por segundo (tono corto que sube, como una gota en agua) y un lavado de ruido brillante; filtrada
  500–7000 Hz. Mismo volumen medio que antes (−30 dB bajo la voz); se genera justo después del primer toque (~0,2 s
  en el portátil) para no congelarlo.
- [x] Volver a escucharla en el iPhone (fusionada, PR #67).
- [x] David no oía el «ding» (16 nov): solo sonaba con «I've completed this step», no con «Preview this change»
  (Raúl los separó en el PR #66), y mientras habla la voz quedaba tapado. Ahora (rama `feat/voice-preview-sound`):
  la vista previa tiene su propio brillo (4 notas rápidas y agudas, −23 dB bajo los picos de la voz) y ni el «ding»
  ni el brillo bajan con el ducking. 1 línea en `stage_page.html` (`houseSound.previewed()`).
- [ ] Oír el brillo y el «ding» en el iPhone.
- [x] `bash check.sh` pasa.

## Para Raúl
Tus cambios sin subir tocan la misma página. Si chocan, solo son estas 6 líneas: búscalas por `houseSound`.
