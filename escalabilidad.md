# Escalabilidad: cómo dar más contexto al modelo

> Propuesta de Samuel (15 nov). **No está construido**: describe cómo puede crecer el producto y qué forma
> elegimos primero. Documento interno, en español; si entra en la entrega se traduce al inglés (regla 9).

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
| Pregunta en vivo | `ask.py` | la pregunta y los hechos del plan de esa familia | **no**: cada pregunta es independiente |

El historial sí se guarda (`sessions.py`, un JSON por sesión en `data/sessions/`), pero solo lo leen `/history`
y `/advisor-note`. **Nunca vuelve al modelo.** Si Melanie pregunta «Can we buy the house in 2030?» y después
«and how much would that cost?», el modelo no sabe qué es «that».

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

**Cómo funcionaría** (propuesta, sobre el código que ya existe):

1. `sessions.py` guarda un campo nuevo `summary` en el JSON de la sesión.
2. `server.py` lee ese resumen y el último turno, y se los pasa a `ask.answer`.
3. `ask.py` los añade al mensaje `user`, debajo de la pregunta:

```
Question: and how much would that cost?

What this person has asked so far (no figures; background only):
- Asked mostly about: garden, roof.
- Worried about running out of savings after retiring.
- Chose step: move_1 (add life cover).

Previous question: Can we buy the house in 2030?
Previous answer: (texto de la respuesta anterior)
```

4. Tras responder, el resumen se actualiza y se guarda.

**Quién escribe el resumen.** Dos niveles, en este orden:

| Nivel | Cómo | Coste | Cuándo |
|---|---|---|---|
| A. Con código | se monta con lo que ya da `advisor_note` (partes, decisión, preguntas fuera del plan) | cero, sin llamadas | primero |
| B. Con el modelo | una llamada aparte, después de responder: «update this summary with the new turn, in 5 lines, no figures» | unos $0,0003 por pregunta con `deepseek-flash` | solo si el nivel A se queda corto |

El nivel B se lanza **después** de devolver la respuesta, para no añadir espera (hoy `/ask` tarda 2,6-4,0 s).

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

## Cómo se comprobaría

1. Test: dos preguntas en la misma sesión; la segunda llamada al modelo contiene el resumen y el turno anterior.
2. Test: un resumen con una cifra se rechaza antes de guardarse.
3. Test: sin sesión previa, el mensaje es el de hoy (nada cambia para la primera pregunta).
4. Prueba real en `/try`: «Can we buy the house in 2030?» y después «and how much would that cost?»; la segunda
   respuesta habla de la casa.
5. `./check.sh` sigue pasando sin llamar al modelo.

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
