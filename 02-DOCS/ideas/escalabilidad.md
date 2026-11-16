# Escalabilidad: cómo dar más contexto al modelo

> Propuesta de Samuel (15 nov). Describe cómo puede crecer el producto y qué forma elegimos primero.
> **Construido: el nivel A del resumen del historial** (ver «Estado» más abajo). El resto son ideas.
> Documento interno, en español; si entra en la entrega se traduce al inglés (regla 9).

## La idea

El modelo no tiene memoria: cada llamada empieza de cero y solo sabe lo que nuestro código le escribe en el
mensaje. Por eso el producto no crece cambiando de modelo, sino **eligiendo qué más le damos y cómo**. Cada fuente
nueva de contexto mejora las respuestas sin rehacer nada.

El límite es que el contexto no es gratis: cada token de entrada se paga en cada pregunta, la respuesta tarda más
y, con demasiado texto, el modelo atiende peor a lo importante.

## Qué recibe hoy el modelo

| Momento | Archivo | Qué se le envía | ¿Recuerda algo? |
|---|---|---|---|
| Narración (una vez por familia) | `narrator.py` | las escenas en orden, cada una con sus hechos | no hace falta |
| Pregunta en vivo | `ask.py` | la pregunta, los hechos del plan y, desde la segunda pregunta, el resumen de la conversación | lo que le pasa el resumen |

Hasta el 15 nov el historial se guardaba (`sessions.py`, un JSON por sesión en `data/sessions/`) pero solo lo leían
`/history` y `/advisor-note`: nunca volvía al modelo. Si la familia preguntaba «Why does my garden dry up?» y
después «and what can I do about it?», el modelo no sabía qué era «it».

## Las formas de añadir contexto

| # | Forma | Qué es | Coste |
|---|---|---|---|
| 1 | Más datos en el mensaje | enviar `investment-analysis.json` y `persona.md`, que hoy no se usan | más tokens en cada pregunta |
| 2 | Historial completo | reenviar todas las preguntas y respuestas anteriores | crece con cada turno |
| 3 | **Resumen del historial** | un resumen corto de la sesión, que se actualiza tras cada pregunta | tamaño fijo |
| 4 | Memoria guardada | lo que la persona dijo o decidió en otras visitas | una lectura de archivo |
| 5 | Selección | enviar solo la parte de la casa relevante | una decisión previa |
| 6 | Herramientas (MCP) | el modelo pide él mismo el dato que le falta | más llamadas, menos control |

## Forma elegida: resumen del historial

**Qué es.** En vez de reenviar toda la conversación, el servidor guarda un resumen de pocas líneas de la sesión
y lo añade a cada pregunta. Tras cada respuesta, el resumen se actualiza.

**Por qué esta.**

- **Tamaño fijo.** Con el historial completo, la pregunta número 20 lleva las 19 anteriores: cada pregunta cuesta
  y tarda más que la anterior. Con el resumen, la pregunta 20 cuesta lo mismo que la 2.
- **Sirve entre visitas.** El resumen se queda en el archivo de la sesión. Cuando la familia vuelve el día 3, el
  modelo sabe de qué hablaron sin releer nada.
- **Ya tenemos casi todos los datos.** `sessions.advisor_note` calcula hoy las partes más preguntadas, lo que el
  plan no cubre y el paso elegido.

**Cómo funciona** (nivel A, construido):

1. `sessions.context_for(session)` monta el resumen a partir del archivo de la sesión, en el momento de preguntar.
   No se guarda aparte: así no puede quedarse viejo.
2. `server.py` se lo pasa a `ask.answer` en `/ask`, `/ask/stream` y `/worry`.
3. `ask.py` lo añade al mensaje del modelo en el campo `conversation`, y a las instrucciones una regla: es
   contexto para entender la pregunta, nunca fuente de cifras, y una pregunta de seguimiento se queda en la misma
   parte de la casa.

```json
"conversation": {
  "worries": ["We owe an amount on a card, is that bad?"],
  "asked_most_about": ["garden", "walls"],
  "chosen_step": "Close a coverage gap",
  "previous": {"question": "Why does my garden dry up?",
               "answer": "Your savings and investments run out at age 73…",
               "scene": "timeline", "house_part": "garden"}
}
```

4. La primera pregunta de una sesión se envía exactamente igual que antes. `ASK_HISTORY=off` lo desactiva.

**Quién escribe el resumen.** Dos niveles, en este orden:

| Nivel | Cómo | Coste | Cuándo |
|---|---|---|---|
| A. Con código | se monta con lo que ya da `advisor_note` (partes, decisión, preguntas fuera del plan) | cero, sin llamadas | primero |
| B. Con el modelo | una llamada aparte, después de responder: «update this summary with the new turn, in 5 lines, no figures» | unos $0,0003 por pregunta con `deepseek-flash` | solo si el nivel A se queda corto |

El nivel B se lanza **después** de devolver la respuesta, para no añadir espera (hoy `/ask` tarda 2,6-4,0 s).

## Estado (15 nov)

- **Nivel A construido y probado** con el servidor real y tres familias. Ejemplo (Samantha): «Why does my garden
  dry up?» → `timeline`, jardín; «and what can I do about it?» → `move_3`, jardín («shift your invested mix from 85%
  in stocks to 80%…»); «how much does that raise my score?» → `move_3` («from 82 out of 100 to 83 out of 100»).
  Sin historial, la segunda pregunta acababa en `move_1` (seguro de hogar), que no tiene que ver con el jardín.
- **Respuestas en 1,0-6,2 s**, las diez aceptadas por `guard`. Es una muestra pequeña (10 preguntas): falta probarlo
  con personas.
- **Nivel B sin construir:** no ha hecho falta todavía.

## Reglas para no romper `guard`

1. **El resumen no lleva cifras.** `guard` acepta solo los números de los hechos de la escena elegida. Si el
   resumen trajera «$80,000», el modelo podría citarlo en una escena que no lo tiene y la respuesta se rechazaría.
   El resumen guarda temas, preocupaciones y decisiones; las cifras salen siempre de los hechos.
2. **El resumen es contexto, no fuente.** Las instrucciones dicen al modelo que lo use para entender la pregunta,
   no para responder con él.
3. **El último turno va literal**, junto al resumen. Un resumen pierde el detalle que hace falta para entender
   «that» o «it» en la pregunta siguiente.
4. **Tamaño máximo** (por ejemplo, 5 líneas). Si crece, deja de ser un resumen.
5. **`guard` sigue revisando la respuesta final**, igual que hoy.

## Riesgos

- **Un error del resumen se arrastra.** Si el modelo resume mal (nivel B), todas las preguntas siguientes parten
  de ese error. Por eso se empieza por el nivel A, que es determinista.
- **Es información personal** (qué preocupa a cada persona). Hoy `data/sessions/` está fuera de git; en un
  producto real necesitaría permiso de la familia y una forma de borrarlo.
- **No está medido.** No sabemos todavía si mejora las respuestas de seguimiento ni cuánto cambia el tiempo de
  respuesta.

## Cómo se comprueba

`tests/test_ask_context.py` (9 tests, sin llamar al modelo):

1. Dos preguntas en la misma sesión: la segunda llamada al modelo lleva el resumen y el turno anterior.
2. El resumen no lleva cifras: los números que escribió la familia pasan a «an amount».
3. Sin historia, el mensaje y las instrucciones son los de antes.
4. El resumen no crece con la sesión (30 turnos pesan lo mismo que 1).
5. Una cifra del turno anterior usada en otra escena se sigue rechazando.
6. `ASK_HISTORY=off` lo desactiva.

## Después (sin orden decidido)

- **Más datos (forma 1):** `persona.md` trae las tensiones de cada pareja e `investment-analysis.json` el detalle
  de las inversiones. Cada dato nuevo entra como hecho (`Fact`) de su escena, para que `guard` lo pueda comprobar.
- **Memoria entre visitas (forma 4):** el mismo resumen, leído al abrir el día 3.
- **Herramientas (forma 6):** descartado para la demo. Convierte el workflow en un agente: más caro y más difícil
  de vigilar.

## Para el pitch

Respuesta a «¿y esto cómo crece?»: el producto no depende de un modelo concreto. Lo que el modelo sabe de cada
familia lo decide nuestro código, y cada dato nuevo del plan o de la conversación mejora las respuestas. El coste
por pregunta no sube con la longitud de la conversación.
