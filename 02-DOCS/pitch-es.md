# Pitch en español: guion de 2 minutos y preguntas del jurado

> Para el Demo Day (19 nov, 12:45). Se proyecta `pitch/index.html`, que ya sale **en español por defecto**
> (`?lang=en` o el botón EN la pasa a inglés). Servirla: `python -m http.server -d pitch` y abrir `localhost:8000`.
> Controles: **espacio** pausa, **← →** cambian de capítulo, **R** reinicia.
> Ritmo hablando tranquilo: unas 2,5 palabras por segundo. Cada bloque cabe en el tiempo de su capítulo.

## 1. Guion

### 0:00 · Problema (13 s)
*Pantalla: «Sherpas ya calcula el plan correcto» → 82 sólida → «se agotan a los 73».*

> «Sherpas ya calcula el plan correcto. Samantha tiene un 82: "sólida". Y aun así, sus ahorros se acaban a los 73.
> Un plan correcto que no se siente es un consejo que nadie sigue.»

- Di «a los 73» justo cuando aparece en rosa. Es el gancho: una buena nota puede esconder el problema.

### 0:13 · Abrir (15 s)
*Pantalla: el cursor elige Michael, Completo y Como una historia.*

> «La familia abre un enlace en el móvil. Sin app y sin cuenta. Tres toques: quién es, cuánto detalle quiere y
> cómo prefiere que se lo expliquen. Las personas no entienden un plan todas igual.»

### 0:28 · Recorrer (20 s)
*Pantalla: la casa de Michael, 26 sobre 100, con techo, cimientos y tuberías rotos.*

> «Este es Michael: 26 sobre 100. Cada pilar de su diagnóstico es una parte de su casa. Los cimientos son su
> fondo de emergencia: rotos. El techo, sus seguros: roto. Una grieta en la pared no necesita explicación.
> Una voz lo acompaña, y cada cifra que dice sale de su plan.»

- Señala la parte de la casa cuando la nombres.

### 0:48 · Preguntar (8 s)
*Pantalla: Michael escribe «¿Todavía puedo comprar la casa en 2027?» y aparecen los puntos.*

> «En cualquier momento, Michael para la voz y pregunta. ¿Todavía puedo comprar la casa en 2027? Sigámosla.»

- «Sigámosla» justo cuando aparecen los puntos: enlaza con el fondo oscuro.

### 0:56 · El cable (23 s)
*Pantalla: los paquetes viajan, el reloj sube hasta 3.050 ms y el precio hasta $0,001465.*

> «La pregunta sale del móvil y llega a nuestro servidor. La envolvemos con **su propio plan**: unos cuatro mil
> tokens de hechos, y nada más. Pasa por **el proxy de Sherpas**, así que la clave nunca sale de nuestro
> servidor, y llega al modelo. *(pausa mientras gira el círculo)* Vuelve la respuesta, y antes de que Michael lea
> una sola palabra, **el guard comprueba cada cifra contra su plan**. Tres segundos de punta a punta. ¿Y el
> precio? **Una décima de céntimo**. Unas setecientas preguntas por un dólar.»

- El momento fuerte es el badge verde del guard: ahí dices «comprueba cada cifra».
- Di «tres segundos de punta a punta», no «3.050 ms»: el total está medido (2,6 a 4,4 s) y el reparto entre
  saltos es ilustrativo (lo dice la nota al pie).

### 1:19 · Actuar (20 s)
*Pantalla: la respuesta con sus cifras subrayadas → «Ya lo he hecho» → la tubería se repara y la puntuación
pasa de 26 a 62.*

> «La respuesta solo usa cifras de su plan, y termina en un paso que Sherpas ya calculó: gastar menos de sus
> ahorros al jubilarse. Lo marca como hecho, su casa se repara, y su puntuación sube de 26 a **62**. Esa cifra no
> es nuestra: es la de Sherpas. Va a su calendario, y su asesor recibe una nota con lo que le preocupaba, lo que
> preguntó y lo que decidió.»

### 1:39 · Por qué (21 s)
*Pantalla: titular, «Hoy / Con Under One Roof», las cuatro cifras de una en una y el lema.*

> «Sherpas ya tiene el producto: el plan. **Nosotros hacemos que las familias lo usen.** Hoy, una familia recibe
> una puntuación y un informe, y cierra la pestaña. Con Under One Roof, lo ve, pregunta, elige un paso, y su
> asesor empieza la siguiente llamada sabiendo qué decidió. El recorrido cuesta cero, una pregunta una décima de
> céntimo, y ni una cifra inventada. *(pausa)* **Un plan. Una casa. Todos dentro.**»

- Esta es la parte que crea la necesidad: Sherpas ya ha hecho el trabajo caro (el plan); lo que pierde es que la
  familia actúe y vuelva al asesor.
- El lema mirando al jurado, y a callar. El botón «Abrir el MVP en vivo» queda de fondo para las preguntas.

**Ojo con una cosa:** en la web, la pregunta y la respuesta salen en español. En el producto, el recorrido con voz
sí existe en español (traducido una vez y con las mismas cifras comprobadas), pero **el chat en vivo responde en
inglés**. No digáis que el chat en directo es bilingüe; si preguntan, ver la pregunta 9.

## 2. Preguntas probables del jurado (backend y escalabilidad)

Respuesta corta primero (la que se dice), detalle debajo por si repreguntan.

**1. ¿Cómo evitáis que el modelo se invente cifras?**
Ninguna cifra llega a la familia sin pasar por el `guard`. Compara cada número de la respuesta, también los
escritos en palabras, con los hechos de la escena que el modelo eligió. Si hay uno que no está, se rechaza.
- El modelo tiene dos intentos. Si falla los dos, la familia oye la narración ya aprobada de esa parte de la casa
  (`source: approved_narration`).
- Si el plan no cubre la pregunta, recibe una frase fija y la pregunta se guarda para el asesor (`off_plan`).
- También vigila errores sin cifras: decir que una deuda «queda saldada» cuando el paso solo paga una parte.

**2. ¿Es un agente? ¿Qué decide el modelo?**
No: es un *workflow*. El modelo solo elige una escena de una lista cerrada y redacta la respuesta con los hechos
de esa escena. Qué datos recibe lo decide nuestro código. Lo preferimos así porque es más barato, más rápido y se
puede auditar.

**3. ¿Cuánto cuesta y cómo crece el coste?**
Unos **$0,0015 por pregunta** (4.300 a 5.200 tokens de entrada y ~140 de salida con `deepseek-flash` a $0,30 /
$1,20 por millón). El recorrido guiado cuesta **cero** por visita: la narración se escribe una vez por familia, se
guarda en `narrations/` y se reproduce sin llamar al modelo.
- El coste crece con las **preguntas**, no con las visitas ni con la longitud de la conversación: el historial
  se manda como un resumen de tamaño fijo (`sessions.context_for`), así que la pregunta 20 cuesta lo mismo que la 2.
- Topes: 40 preguntas por sesión (`ASK_MAX_TURNS`) y 30 por minuto en total (`ASK_MAX_PER_MINUTE`), con un 429 amable.

**4. ¿Cuánto tarda una respuesta? ¿Y si el modelo se cae?**
Medido: **2,6 a 4,4 s** por respuesta escrita; una pregunta hablada entera, 4,9 s. La respuesta llega palabra a
palabra (`/ask/stream`, server-sent events), así que la familia empieza a leer antes.
- Si `deepseek-flash` tarda más de 8 s o falla, se pregunta a `gemini-3.5-flash-lite` (fallback).
- Si fallan los dos, la familia recibe una frase fija, nunca un error.
- La voz no frena la respuesta: el mp3 se genera cuando el móvil lo pide y luego se guarda.

**5. ¿Por qué pasa por el proxy de Sherpas?**
Porque así Sherpas controla la clave, el gasto (`/key/info`) y qué modelos se usan. La clave nunca llega al móvil:
vive en nuestro servidor (`.env`). Cambiar de modelo es cambiar una variable (`ASK_MODEL`), no el código.

**6. ¿Cómo escala a miles de familias?**
La parte cara (narración y voz del recorrido) se hace **una vez por familia** y se sirve como archivos estáticos,
que escalan con cualquier CDN. Lo único en vivo son las preguntas, y cada una es una llamada corta e independiente.
Para producción cambiaríamos tres cosas:
1. **Sesiones:** hoy son archivos JSON en `data/sessions/`; pasarían a una base de datos (Postgres o Redis),
   porque un servidor sin disco las olvida al reiniciar.
2. **Límite de ritmo por familia**, no global, y más de una instancia del servidor detrás de un balanceador (el
   servidor no guarda estado en memoria salvo ese contador).
3. **Generar narración y voz** en una cola cuando Sherpas publica o actualiza un diagnóstico.
- El límite real hoy es el del proxy del hackathon: 60 peticiones por minuto y 4 a la vez.

**7. ¿Y si Sherpas actualiza el diagnóstico de una familia?**
Se vuelve a generar su narración (una llamada) y se vuelve a comprobar con el `guard`. Las traducciones al español
guardan una huella del texto inglés del que salen: si el inglés cambia, la traducción vieja deja de usarse sola.

**8. ¿Cómo lo integra Sherpas?**
Leemos el mismo `financial-health.json` que da su diagnóstico (el que sirve su MCP; hoy lo leemos de archivos
locales para no depender de un token que caduca, y conectarlo al MCP es cambiar de dónde se lee). El contrato entre etapas es
`contracts/schemas.py`: una `Presentation` con hechos (cada uno con su origen en el diagnóstico) y escenas. Se
despliega como un contenedor (`Dockerfile`, hoy en Render). Encaja como un enlace más en el informe que ya envían.

**9. ¿Funciona en español?**
El recorrido con voz, sí: se traduce una vez con un modelo y solo se usa si tiene exactamente las mismas cifras que
el inglés. El chat en vivo hoy responde en inglés, porque el `guard` lee las cifras en formato inglés. Hacerlo
bilingüe es adaptar ese formato (punto y coma) y las cifras escritas en palabras.

**10. ¿Y la privacidad?**
Las sesiones contienen qué preocupa a cada persona. Hoy están fuera de git y solo en nuestro servidor. En producción
harían falta consentimiento de la familia, poder borrarlas y alojarlas en la UE (RGPD). Al modelo solo le llegan los
hechos del plan y la pregunta, no datos de contacto.

**11. ¿Cómo sabéis que funciona?**
241 tests automáticos (`./check.sh`), con un modelo falso: sin red y sin gastar. Prueban el `guard`, las respuestas,
el historial y que una cifra fuera de su escena se rechaza. Además, `./check.sh` genera la página completa en cada
cambio, y nada entra en `main` si no pasa.

**12. ¿Qué no está probado todavía?**
Decidlo sin miedo: no lo hemos probado con familias reales (las pruebas de calidad son ~10 preguntas nuestras) y
no tenemos medido si sube la tasa de acción. Lo siguiente sería un piloto con unas pocas familias de Sherpas
midiendo cuántas marcan un primer paso y vuelven al asesor.
