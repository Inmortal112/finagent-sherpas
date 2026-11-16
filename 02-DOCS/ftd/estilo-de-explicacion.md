---
created: 2026-11-16
status: done
branch: feat/brain-explanation-style, feat/voice-explanation-style, feat/stage-opening-screen, feat/brain-ask-style
---
# FTD — Cada persona elige cómo se lo explican

## Hecho (17 nov) — Samuel y Raúl dijeron sí; las cuatro fases, por David
- **Decisiones tomadas** (las recomendadas abajo): dos métodos, **As a story** (la narración de hoy) y **Numbers
  first**; solo en «In full», así que el orden es **persona → detalle → método**; `/ask` sigue el método.
- **Fase 1:** `narrator --style numbers`, clave `numbers` en las cuatro `narrations/*.json` (46 escenas, 10.602
  caracteres). Las 46 leídas contra sus hechos; **seis retocadas a mano** (Johnson `all_moves` y `timeline`; Samantha
  `pillar_insurance_and_protection`, `move_1` y `timeline`; Weah `pillar_insurance_and_protection`).
- **Fase 2:** `styles.py` + `web/styles.js`: `styles/numbers/audio/` y `styles.json` junto a cada página completa. El
  texto, el audio y los subtítulos cambian sin recargar. Se guarda por persona. `captions.js` no hizo falta tocarlo.
- **Fase 3:** `web/welcome.js`: pantalla de inicio (una vez por familia y navegador), botón «Change» en la barra, y al
  cambiar de modo se vuelve al mismo capítulo (`#ch-<id>`). `?welcome=1` la fuerza, `?welcome=0` la quita.
- **Fase 4:** `/ask`, `/ask/stream` y `/worry` aceptan `style`; la sesión lo recuerda y sale en la nota del asesor.
- **No hecho:** el método en español (con «Español» suena la historia y el interruptor dice «English only»), el audio
  con Matilda (hoy solo voz gratuita) y la prueba en iPhone real.

Lo que sigue es el plan original, tal como se aprobó.

- Propone: David (`daviid-sc`). **Lo deciden los tres.** Toca las tres etapas, así que nada se programa hasta el sí.
- Este PR solo trae este plan. El código iría en ramas `feat/*-explanation-style-*`.

## Intención
Al abrir, cada persona dice tres cosas: **quién es**, **cómo prefiere que se lo expliquen** y **cuánto detalle quiere**
(Simply / In full). Lo nuevo es lo segundo: la misma casa y las mismas cifras, contadas de otra manera.
- *Personal* (15): hoy elegir persona casi no cambia nada (ver abajo). Con esto, Timothy y Melanie oyen cada uno su versión.
- *Se entiende* (20): las bases piden que sirva «para novatos y expertos».
- `persona.md` deja vacío «Subjective concerns» en los cuatro casos y marca el estilo de decisión (D5) con confianza
  baja: nadie les ha preguntado. Por eso se pregunta, no se adivina.
- La nota de idea enviada al jurado dice que cada persona elige al abrir (`modo-se-elige-al-abrir.md`). Hoy no hay esa
  pantalla.

## Lo que hay hoy (leído en `main`, `f96ca22`)
- **No hay pantalla de inicio.** La elección es una fila de botones en la portada (`stage_page.html`, `#opts`): «I am»
  (solo parejas), «Guide me: Simply | In full», «Listen in: English | Español». La familia va en un desplegable.
- **Se puede cambiar siempre, pero hay que volver arriba.** Cambiar de modo carga otra página (`switchTo`) y te deja al
  principio. La persona y los pasos hechos se guardan en el navegador (`localStorage`).
- **La persona cambia poco:** las respuestas de `/ask`, la nota a la pareja y el saludo de vuelta. La narración es la misma.
- **El español ya es una «segunda pista» dentro de la misma página:** `spanish.py` escribe `audio/es/*.mp3` y `es.json`,
  y `web/spanish.js` cambia de pista sin recargar.

## Propuesta

### 1. El método es una segunda pista, no más páginas
Igual que el español: cada página lleva dentro el texto y el audio del otro método (`audio/<método>/*.mp3`,
`<método>.json`) y un interruptor los cambia al momento.
- Siguen siendo **8 páginas**, no 16 ni 24. `brain.MODES`, `switchTo` y el **contrato no cambian**.
- Cambiar de método **no recarga**: la persona sigue en el mismo capítulo. Es lo que hace que «poder cambiarlo
  después» no moleste.
- El texto nuevo pasa por el mismo control que el actual (`narrator.check`): solo cifras de los hechos de su escena.

### 2. Se guarda por persona
Clave `uor-style-<familia>-<persona>` en el navegador. Al tocar «I am Melanie» vuelve su método.

### 3. Pantalla de inicio corta y siempre cambiable
- Tres preguntas, **un toque cada una**, con una opción ya marcada y un «Start» visible desde la primera. Las bases
  hablan de 10 segundos para captar la atención: nada de formularios.
- Se salta lo que no aplica (un solo adulto → no se pregunta quién es) y no vuelve a salir a quien ya eligió.
- Un botón pequeño y fijo («Change») la reabre desde cualquier capítulo. La fila de la portada se queda como está.
- Al cambiar Simply / In full, la dirección lleva el capítulo (`#<id>`) para volver al mismo sitio.

### 4. Inglés primero (decidido por David)
El método nuevo se hace **solo en inglés**. Con «Español» puesto suena la pista española de hoy y el interruptor del
método avisa «English only». Traducirlo queda para el final, si sobra tiempo.

## Decisiones abiertas (para los tres)
1. **Qué métodos.** Propongo **dos**, no tres:
   - *The story of your home* → la narración de hoy (la casa como metáfora). Coste cero.
   - *Straight to the numbers* → la cifra primero y qué significa después; la casa solo como referencia de lo que se ve.
   - Descartado por ahora *What do I do?* (empezar por la acción): las escenas de cada parte no llevan los hechos del
     paso que la repara, y habría que tocar `brain`.
2. **¿También en «Simply»?** Recomiendo que no: quien elige Simply quiere menos opciones y ya son 28 palabras por escena.
   Eso cambia el orden a **persona → detalle → método** (el método solo se pregunta en «In full»). Si se quiere el
   orden persona → método → detalle, el método tiene que existir en los dos modos (el doble de escenas).
3. **¿El método cambia `/ask`?** Barato (un párrafo en el aviso al modelo, como `SIMPLE_MODE`), pero son tres archivos
   de Samuel. Lo dejaría para la fase 4.

## Coste (medido hoy sobre `narrations/`)
| | Escenas | Caracteres de audio |
|---|---|---|
| Un método, solo «In full», inglés (**recomendado**) | 46 | ~8.800 |
| Un método, los dos modos, inglés | 92 | ~13.700 |
| Lo mismo en español (más adelante) | 46–92 | ~9.500–16.100 |

- **Texto:** `deepseek-flash` por el proxy, céntimos.
- **Voz gratuita (edge):** gratis. Es la que usa el `Dockerfile`, así que el enlace público lo tendría sin más.
- **Matilda (cuenta de estudiante de David, 129.943 caracteres/mes):** 8.800 son el 6,8 %; 13.700, el 10,6 %.
  Familia a familia para no pasar de `ELEVEN_MAX_CHARS` (6.000 por ejecución). Saldo actual sin consultar.
- **Clave del equipo:** no. 13.700 caracteres serían $0,55 del tope de $1,40.

## Fases y línea de corte
Congelación: **18 nov, 18:00**. Tiempos a ojo.
| Fase | Qué | Referente | Tiempo |
|---|---|---|---|
| 1 | Texto: `narrator --style`, generar las 4 familias, leerlas | Samuel | ~2 h |
| 2 | Voz: pista de audio, subtítulos, `web/styles.js`, interruptor en `#opts` | David | ~3 h |
| 3 | Pantalla de inicio, botón «Change», volver al mismo capítulo | Raúl | ~3 h |
| 4 | Opcional: `/ask` sigue el método; español | Samuel / David | ~2 h |

**Corte:** si la fase 3 no está fusionada el 18 a las 12:00, se entrega con las fases 1 y 2 (interruptor en la portada,
como el del español) y sin pantalla de inicio.

## Archivos
- `narrator.py`: párrafo del método (como `SIMPLE_MODE`), opción `--style`, texto guardado en la misma
  `narrations/<familia>.json` bajo una clave nueva. `brain.build` no cambia.
- `src/finagent/styles.py` (nuevo, calcado de `spanish.py`): escribe la pista con el mismo motor de voz que la principal.
- `run.py`: una línea, como la del español.
- `web/styles.js` (nuevo, calcado de `web/spanish.js`): aquí el texto **sustituye** al párrafo, no se añade debajo.
- `web/captions.js`: reconocer `audio/<método>/` además de `audio/es/`.
- `stage_page.html`: tres enganches (cargar, `play()`, `build()`), pantalla de inicio y botón «Change».
- Tests sin red: cada familia tiene el método aceptado por `guard`; el interruptor cambia la pista; la pantalla no
  sale dos veces.
- Al fusionar código: `SUBMISSION.md`, `README.md`, `VOICE.md`, `STAGE.md`.

## NO entra
- Cambiar lo que se ve según el método (casa, cámaras, tarjetas). Solo cambia lo que se dice y se lee.
- El método en la nota de pareja, la de los niños, el calendario o el saludo de vuelta.
- Adivinar el método a partir de `persona.md`.

## Riesgos
- **Tiempo.** Quedan unas 42 h hasta la congelación y siguen pendientes el enlace de Render, el vídeo, el repo público
  y las pruebas en iPhone. Esto compite con eso.
- **Dos textos que mantener.** Si cambia una narración, el otro método puede quedar desfasado: un test avisa, como en
  el español.
- **Cifras en voz.** Las escenas nuevas de Matilda hay que auditarlas con Whisper, como las 92 de hoy.
- **Sin probar en iPhone:** la pantalla de inicio y el cambio de pista.

## Checklist
- [x] Los tres dicen sí o no, y contestan las tres decisiones abiertas.
- [x] Fase 1 · [x] Fase 2 · [x] Fase 3 · [x] Fase 4
- [x] `bash check.sh` pasa en cada PR.

## Para Samuel y Raúl
- **Samuel:** ¿te encaja el método como un párrafo más del aviso (`--style`)? ¿Y los dos métodos propuestos?
- **Raúl:** la pantalla de inicio y el botón «Change» son tu escena. ¿Caben antes del 18 a las 12:00, o vamos solo
  con el interruptor de la portada?
