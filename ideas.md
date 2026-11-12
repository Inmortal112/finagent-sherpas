# Ideas candidatas

Tres ideas por persona. Entre las nueve elegimos una y la enviamos con `/idea` antes del **vie 13 nov a las 22:00**
(10 puntos; hay que decir qué construimos y por qué, y qué descartamos y por qué: las ocho que no elijamos sirven
para esa segunda parte).

**Cómo añadir las tuyas:** escribe solo dentro de tu sección (abajo), con la misma plantilla. La idea de David está en
`idea-david.md` («Your Financial Home»). No edites las de otro;
si quieres opinar sobre una idea ajena, hazlo en la tabla de votos del final, en tu columna.

Criterios del jurado: Engancha 20 · Se entiende 20 · Mueve a actuar 20 · Personal 15 · Creatividad 15 · Nota de idea 10.
Aviso de las bases: Sherpas ya tiene tours guiados y un chat sobre el plan; una idea que sea solo eso puntúa bajo.

## Datos de los casos que condicionan cualquier idea

Comprobado en `cases/` el 12 nov:

- **El plan ya trae los pasos calculados.** `score.top_moves` da cada acción con la nota antes y después, y
  `score.combined_moves` da la nota al combinarlas. Ejemplo (Weah): pagar la tarjeta + ampliar el seguro de vida
  → de 60 a 73; añadiendo el seguro umbrella → 78. Se puede enseñar "qué pasa si…" sin inventar cifras.
  Michael Carter y Samantha Lewis no tienen `combined_moves`, solo pasos sueltos.
- **Nadie les ha preguntado qué les preocupa.** En las cuatro `persona.md`, «Subjective concerns» está vacío
  («None recorded / None detected»).
- **Las parejas tienen tensiones documentadas** (secciones T1, T2… de `persona.md`). Ejemplo (Weah): $18.000 en una
  tarjeta al 18 % (unos $3.240 al año de intereses) con $150.800 en efectivo que rinde unos $150 al año.
- **Hay proyección año a año** (`projections.yearly`) solo del plan actual. No hay proyección "si hago el paso X":
  lo único calculado para los escenarios alternativos es la nota.

---

## Ideas de Samuel

### S1 · Your Plan, Your Way (idea principal de Samuel)

- **Qué es:** un agente que se incrusta en la página del plan de Sherpas. Antes de explicar nada, cada persona lo
  configura en medio minuto (cómo quiere que se lo expliquen y con cuánto detalle). Después reorganiza el plan de
  esa familia en ese formato y en el orden que más le conviene, y termina en un primer paso.
- **Para quién:** familias con o sin asesor. Caso principal de la demo: los Weah, con dos configuraciones distintas
  sobre el mismo plan (Timothy: gráficos y todo el detalle; Melanie: voz, resumen y «dime qué hacer»).
  Segundo: Michael Carter (nota 26).
- **Cómo lo vive la familia:**
  1. **Configuración (30 s, por persona).** No es un formulario de ajustes: la app enseña una cifra real de su plan
     de varias maneras y la persona elige la que mejor entiende.
     - Formato (uno o varios): datos concretos en el tiempo, gráfico interactivo, voz, resumen escrito.
     - Nivel de detalle: «Just tell me what to do» / «Show me why» / «Give me everything».
     - Qué le preocupa más (cuatro tarjetas sacadas de su plan): decide por dónde se empieza.
  2. **Plan reorganizado.** El agente ordena los temas según los datos de la familia (primero lo que más frena su
     nota y lo que ha dicho que le preocupa) y presenta cada tema en el formato y nivel elegidos.
  3. **Preguntas.** Puede preguntar al agente, que responde en su formato (un gráfico o una frase de voz, no solo
     texto) y con cifras del plan.
  4. **Primer paso.** Acaba con la acción que más le conviene, con la nota antes y después (`top_moves`,
     `combined_moves`), cómo hacerla y una fecha.
  5. La configuración se guarda y se puede cambiar. Los días 3 y 30 vuelve en el mismo formato.
- **Por qué puntúa:** responde de frente a «Se entiende» (funciona para quien no sabe y para un experto: son los
  niveles de detalle) y a «Personal» (para esta familia y para cada persona de ella: dos configuraciones, un plan).
  Ataca los atascos de las cifras grandes que no dicen si algo va bien o mal (2), la pareja con necesidades
  distintas (8) y demasiadas opciones sin primer paso (11).
- **Argumento para el pitch:** lo que cada persona elige y dice que le preocupa rellena el «Subjective concerns»
  que hoy está vacío en las cuatro familias; el asesor llega a la reunión sabiendo cómo hablarle a cada uno.
- **Integración en Sherpas:** un widget (una etiqueta `<script>` o un `iframe`) sobre un backend propio que lee el
  mismo JSON que Sherpas ya produce (`financial-health.json`, `investment-analysis.json`, `persona.md`). En la
  demo se enseña incrustado en una página de plan de ejemplo. No conocemos su stack: «fácil de integrar» es una
  afirmación de diseño, no algo que podamos probar contra su web.
- **Reparto:** encaja con las tres etapas que ya tenemos. Samuel (cerebro): perfil de preferencias → selección,
  orden y redacción de los bloques por nivel de detalle, con `guard`. Raúl (escena): pantalla de configuración y un
  componente por formato (línea de tiempo, gráfico interactivo, resumen). David (voz): audio de cada bloque
  (`edge-tts` en desarrollo, ElevenLabs solo para la demo) y preguntas por voz si da tiempo.
  El contrato `Presentation` casi sirve: una escena pasa a ser un bloque; falta añadir el perfil de preferencias.
- **Riesgos:**
  - **Creatividad:** Sherpas ya tiene un chat sobre el plan y avisa de que una idea que sea solo eso puntúa bajo.
    Hay que presentarlo como un plan que se reorganiza para cada persona, no como un chatbot; el chat es una pieza.
  - **Engancha:** empezar por una configuración es fricción. Por eso son tres elecciones con vista previa sobre
    sus propios datos, no un formulario.
  - **Alcance:** 4 formatos × 3 niveles son 12 combinaciones por tema. Para el MVP: dos familias, tres o cuatro
    temas, textos pregenerados y guardados.
- **Coste:** bajo en texto. La voz, pregenerada.

### S2 · A Message from 2047

- **Qué es:** cada persona recibe un mensaje de voz de un minuto de su «yo futuro», que le cuenta cómo le fue según
  la proyección de su propio plan y qué habría hecho antes. Termina con una sola petición: el primer paso.
- **Para quién:** sobre todo familias que nunca verán a un asesor, y personas que apartan la mirada ante una mala
  noticia. Caso principal: Michael Carter (nota 26, sus activos líquidos se agotan a los 85 según el plan).
  Segundo: Samantha Lewis (nota 82, pero sus ahorros se agotan a los 73).
- **Cómo lo vive la familia:**
  1. Llega una notificación: «You have a voice message from Michael, age 58».
  2. Escucha el mensaje mientras ve su línea de vida avanzar año a año (`projections.yearly`).
  3. El mensaje cuenta el camino actual con las cifras del plan, en primera persona y en su tono.
  4. Acaba con el paso que el plan recomienda y un botón para comprometerse.
  5. Días después llega una «posdata» corta del yo futuro si no ha actuado.
- **Por qué puntúa:** engancha en segundos y es muy personal. Ataca la mala noticia que hace mirar a otro lado (6),
  no ver cómo una decisión de hoy cambia su vida dentro de años (1) y la nota buena que esconde un problema (3).
- **Reparto:** Samuel escribe el guion por persona a partir de la proyección y la persona. David es el centro de la
  idea: voz, ritmo y tono. Raúl hace la pantalla de mensaje con la línea de vida animada.
- **Riesgos:** es de un solo uso y flojo en «mueve a actuar» si el final no es muy concreto. Solo podemos contar el
  futuro del plan actual: para «si haces el paso» únicamente tenemos la nota, no una proyección, así que el
  «final bueno» no puede llevar cifras. Tono delicado (envejecer, quedarse sin dinero).
- **Coste:** medio. La voz es el producto y ElevenLabs tiene un tope de $1,40: hay que pregenerar y guardar.

### S3 · Sixty Seconds a Day

- **Qué es:** el plan llega repartido en una semana de mensajes de un minuto (Telegram o correo). Cada día trae una
  sola cifra explicada, una pregunta de un toque y una microacción. Las respuestas deciden el mensaje siguiente.
- **Para quién:** familias sin tiempo que leen a ratos en el móvil. Caso principal: los Weah (dos trabajos, hijos de
  6 y 3 años). Segundo: Samantha Lewis, con mensajes atados a sus fechas (matrícula cada agosto, casa en 2030).
- **Cómo lo vive la familia:**
  1. Día 1: su nota y la única cosa que más la frena, en un mensaje.
  2. Días 2 a 6: un tema al día, ordenados según lo que ha ido contestando.
  3. Cada mensaje acaba en una acción de un toque («Recuérdamelo el sábado», «Ya lo hice», «No lo entiendo»).
  4. Día 7: resumen de lo decidido y un primer paso con fecha.
  5. Día 30 y fechas clave del plan: el mensaje llega cuando toca actuar, no cuando se generó el plan.
- **Por qué puntúa:** es la que mejor cubre los días después. Ataca que no se sientan a leer un plan largo (5), que
  las dudas llegan cuando no hay nadie (9) y que el plan llega en su fecha y no cuando la familia actuaría (10).
- **Reparto:** Samuel genera la secuencia de mensajes y sus ramas. David hace el bot y la programación de envíos
  (y notas de voz opcionales). Raúl hace el panel que enseña la semana y el «viaje en el tiempo» para la demo.
- **Riesgos:** es la más parecida a un chat, que es justo lo que Sherpas dice que puntúa bajo en creatividad.
  El primer impacto es flojo: en dos minutos de pitch cuesta enseñar algo que pasa en siete días.
- **Coste:** bajo.

### S4 · The Family Tree (idea principal de Samuel desde el 12 nov por la noche)

- **Qué es:** el plan de la familia se ve como un árbol vivo. Cada parte del árbol es un pilar de la nota, cada
  miembro tiene su rama y cada paso del plan es un cuidado que lo hace reverdecer. Como está vivo, hay que volver.
- **La metáfora (con datos de `score.pillars`):**

  | Parte del árbol | Qué representa | Ejemplo real |
  |---|---|---|
  | Raíces | Liquidez y fondo de emergencia | Weah 15/15: raíces profundas. Michael 4/20: raíces cortas |
  | Tronco | Ahorro y flujo de caja | Michael 0/25: tronco fino |
  | Copa | Inversiones | Weah 8/15 |
  | Hiedra que lo ahoga | Deuda cara | La tarjeta al 18 % de los Weah |
  | Tutor y valla | Seguros y protección | Johnson 0/20: sin protección ante una tormenta |
  | Frutos | Objetivos con fecha | Casa en 2027, universidad de Liam en 2038, jubilación |

- **Para quién:** familias con o sin asesor. Demo: los Weah (pareja, una rama por persona) y Samantha Lewis (nota 82
  y ahorros que se agotan a los 73).
- **Cómo lo vive la familia:**
  1. Primer vistazo: su árbol con los nombres de la familia en las ramas. En tres segundos ven qué está verde y qué
     se seca.
  2. Estaciones: un deslizador recorre los años del plan (`projections.yearly`). Al árbol de Samantha, que parece
     perfecto, se le caen las hojas a los 73.
  3. Cuidar: cada paso del plan es un cuidado («podar la hiedra» = pagar $6.800 de la tarjeta; «poner la valla» =
     ampliar el seguro de vida). Al comprometerse con una fecha, el árbol reverdece y se ve la nota antes y después
     (Weah: 60 → 73 con los dos pasos, `combined_moves`).
  4. En pareja: cada uno cuida su rama y el tronco es común; los pasos que afectan a los dos necesitan que ambos
     los confirmen.
  5. Volver: cada día se despliega una hoja nueva (una parte del plan explicada en un minuto); los frutos maduran
     cuando se acerca su fecha (la matrícula de agosto de Samantha); el día 3 la hiedra sigue ahí si no se ha hecho
     el paso, y el día 30 un paso cumplido deja un anillo nuevo en el tronco, que queda como historial.
- **Por qué puntúa:** un árbol sano o marchito se entiende sin saber de finanzas, y tocar cualquier parte abre las
  cifras para el experto. Engancha porque es su familia, con sus nombres. Es la idea con más motivo para volver:
  la casa se repara y ya está; el árbol sigue vivo. Ataca los atascos 2 (cifras que no dicen si algo va bien),
  3 (la nota buena que esconde un problema), 5 (leer a ratos), 8 (pareja), 9 y 10 (seguimiento y fechas) y 11
  (primer paso).
- **Encaja con S1:** la configuración por persona (voz, gráfico o resumen; nivel de detalle) decide cómo se le
  cuenta a cada uno la hoja del día. Y las respuestas rellenan el «Subjective concerns» para el asesor.
- **Reparto:** Samuel: de los JSON al estado de cada parte, las hojas diarias por nivel de detalle, los cuidados
  (`top_moves` / `combined_moves`) y las fechas, todo por `guard`. Raúl: el árbol en SVG generado por código (ramas
  y hojas según los datos), estaciones, animación de reverdecer. David: la voz de la hoja del día y los avisos de
  los días 3 y 30.
- **Riesgos:**
  - **Se parece en tipo a «Your Financial Home» de David** (`idea-david.md`): las dos son un objeto cuyas partes son
    los pilares. La diferencia es que el árbol está vivo y da motivo para volver. Puede competir o fusionarse.
  - **Solo cambia con cosas reales** (compromisos, pasos hechos, fechas que se acercan, contenido nuevo). Nada de
    cambios inventados para simular vida: las bases prohíben inventar cifras, y solo hay proyección del plan actual.
  - **Lo visual:** tiene que parecer una lámina botánica, no un dibujo animado.
  - «Tutor y valla» para la protección es la parte menos intuitiva de la metáfora; hay que probarla con alguien.
- **Coste:** bajo. Textos pregenerados; voz con `edge-tts` en desarrollo.

### Comparación (estimación de Samuel, no medida)

| Criterio (puntos) | S1 Your Plan, Your Way | S2 Message from 2047 | S3 Sixty Seconds | S4 The Family Tree |
|---|---|---|---|---|
| Engancha (20) | Medio-alto | Muy alto | Medio | Muy alto |
| Se entiende (20) | Muy alto | Medio | Alto | Muy alto |
| Mueve a actuar (20) | Alto | Bajo | Alto | Alto |
| Personal (15) | Muy alto | Alto | Medio | Muy alto |
| Creatividad (15) | Medio | Alto | Bajo | Alto |
| Motivo para volver (extra) | Medio | Bajo | Alto | Muy alto |
| Dificultad en 6 días | Media-alta | Media | Baja | Media-alta |

**Preferencia de Samuel:** S4, con la configuración de S1 encima. S1 sola se parece demasiado a un chat sobre el
plan; el árbol le da la parte visual y el motivo para volver.

Otras metáforas valoradas el 12 nov y no desarrolladas: el plan como parte meteorológico («Money Weather»), como
revisión médica («The Check-up») y como vuelo con dos copilotos («Co-Pilots»). Versión anterior de S1
(«First Move»): la pareja ordenaba los pasos por separado y la app proponía un primer paso común.

---

## Ideas de David

<!-- David: escribe aquí tus tres ideas (D1, D2, D3) con la plantilla del final. -->

---

## Ideas de Raúl

<!-- Raúl: escribe aquí tus tres ideas (R1, R2, R3) con la plantilla del final. -->

---

## Votos

Cada uno rellena solo su columna con sus tres favoritas en orden (por ejemplo `S1, D2, R1`) y una línea de porqué.

| | Samuel | David | Raúl |
|---|---|---|---|
| Favoritas | | | |
| Por qué | | | |

## Plantilla

```markdown
### X1 · Nombre
- **Qué es:** dos o tres líneas.
- **Para quién:** tipo de familia y caso principal de la demo.
- **Cómo lo vive la familia:** pasos numerados.
- **Por qué puntúa:** criterios y atascos del brief que ataca.
- **Reparto:** qué haría cada uno de los tres.
- **Riesgos:** qué puede salir mal.
- **Coste:** créditos que gasta.
```
