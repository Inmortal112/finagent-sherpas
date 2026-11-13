# Ideas candidatas

Las ideas de cada uno. Entre todas elegimos una y la enviamos con `/idea` antes del **vie 13 nov a las 22:00**
(10 puntos; hay que decir qué construimos y por qué, y qué descartamos y por qué: las que no elijamos sirven
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

## Idea de Samuel

### S4 · The Family Tree

- **Qué es:** el plan de la familia se ve como un árbol vivo. Antes de nada, cada persona configura en medio minuto
  cómo quiere que se lo expliquen. Después, cada parte del árbol es un pilar de su nota, cada miembro tiene su rama
  y cada paso del plan es un cuidado que lo hace reverdecer. Como está vivo, hay que volver.
- **La metáfora (con datos de `score.pillars`):**

  | Parte del árbol | Qué representa | Ejemplo real |
  |---|---|---|
  | Raíces | Liquidez y fondo de emergencia | Weah 15/15: raíces profundas. Michael 4/20: raíces cortas |
  | Tronco | Ahorro y flujo de caja | Michael 0/25: tronco fino |
  | Copa | Inversiones | Weah 8/15 |
  | Hiedra que lo ahoga | Deuda cara | La tarjeta al 18 % de los Weah |
  | Tutor y valla | Seguros y protección | Johnson 0/20: sin protección ante una tormenta |
  | Frutos | Objetivos con fecha | Casa en 2027, universidad de Liam en 2038, jubilación |

- **Para quién:** familias con o sin asesor. Demo: los Weah (pareja, una rama y una configuración por persona:
  Timothy con gráficos y todo el detalle; Melanie con voz, resumen y «dime qué hacer») y Samantha Lewis (nota 82 y
  ahorros que se agotan a los 73).
- **Paso 0 · Configuración del entorno (30 s, por persona).** Es lo primero que se abre. No es un formulario de
  ajustes: la app enseña una cifra real de su plan de varias maneras y la persona elige la que mejor entiende.
  - **Formato** (uno o varios): datos concretos en el tiempo, gráfico interactivo, voz, resumen escrito.
  - **Nivel de detalle:** «Just tell me what to do» / «Show me why» / «Give me everything».
  - **Qué le preocupa más** (cuatro tarjetas sacadas de su plan): decide por dónde empieza su árbol.
  - Se guarda por persona y se puede cambiar en cualquier momento.
- **Cómo lo vive la familia después:**
  1. **Primer vistazo:** su árbol con los nombres de la familia en las ramas. En tres segundos ven qué está verde y
     qué se seca. El recorrido empieza por la parte ligada a lo que dijeron que les preocupa.
  2. **Plan reorganizado a su medida:** el agente ordena los temas según los datos de la familia (primero lo que más
     frena su nota) y explica cada parte del árbol en el formato y nivel que eligió esa persona.
  3. **Estaciones:** un deslizador recorre los años del plan (`projections.yearly`). Al árbol de Samantha, que
     parece perfecto, se le caen las hojas a los 73.
  4. **Preguntas:** puede preguntar al agente, que responde en su formato (un gráfico o una frase de voz, no solo
     texto) y solo con cifras del plan.
  5. **Cuidar:** cada paso del plan es un cuidado («podar la hiedra» = pagar $6.800 de la tarjeta; «poner la valla»
     = ampliar el seguro de vida). Al comprometerse con una fecha, el árbol reverdece y se ve la nota antes y
     después (Weah: 60 → 73 con los dos pasos, `combined_moves`).
  6. **En pareja:** cada uno cuida su rama y el tronco es común; los pasos que afectan a los dos necesitan que
     ambos los confirmen.
  7. **Volver:** cada día se despliega una hoja nueva (una parte del plan en un minuto, en el formato de esa
     persona); los frutos maduran cuando se acerca su fecha (la matrícula de agosto de Samantha); el día 3 la hiedra
     sigue ahí si no se ha hecho el paso, y el día 30 un paso cumplido deja un anillo nuevo en el tronco.
- **Por qué puntúa:**
  - **Engancha (20):** es su familia, con sus nombres, y está viva.
  - **Se entiende (20):** un árbol sano o marchito se entiende sin saber de finanzas; los niveles de detalle sirven
    al novato y al experto.
  - **Mueve a actuar (20):** cuidar es la acción, con resultado visible y nota antes y después.
  - **Personal (15):** una rama y una configuración por persona sobre el mismo plan.
  - **Creatividad (15):** no es un tour ni un chat; el chat es una pieza dentro del árbol.
  - **Extra, días después:** es la razón de ser de un árbol vivo.
  - Atascos del brief que ataca: 2, 3, 5, 8, 9, 10 y 11.
- **Argumento para el pitch:** lo que cada persona elige y dice que le preocupa rellena el «Subjective concerns»
  que hoy está vacío en las cuatro familias; el asesor llega a la reunión sabiendo cómo hablarle a cada uno.
- **Integración en Sherpas:** un widget (una etiqueta `<script>` o un `iframe`) en la página del plan
  (`app.sherpaswealth.com`), sobre un backend propio que lee el mismo JSON que Sherpas ya produce
  (`financial-health.json`, `investment-analysis.json`, `persona.md`). En la demo se enseña incrustado en una
  página de plan de ejemplo. No conocemos su stack: «fácil de integrar» es una decisión de diseño, no algo que
  podamos probar contra su web.
- **Reparto:** Samuel (cerebro): perfil de preferencias → estado de cada parte del árbol, orden de los temas, textos
  por nivel de detalle, cuidados (`top_moves` / `combined_moves`) y fechas, todo por `guard`. Raúl (escena):
  pantalla de configuración, árbol en SVG generado por código, estaciones, animación de reverdecer y un componente
  por formato (línea de tiempo, gráfico, resumen). David (voz): la voz de cada parte y de la hoja del día
  (`edge-tts` en desarrollo, ElevenLabs solo para la demo) y los avisos de los días 3 y 30.
  El contrato `Presentation` casi sirve: una escena pasa a ser una parte del árbol; falta el perfil de preferencias.
- **Riesgos:**
  - **Se parece en tipo a «Your Financial Home» de David** (`idea-david.md`): las dos son un objeto cuyas partes son
    los pilares. La diferencia es que el árbol está vivo y se adapta a cada persona. Puede competir o fusionarse.
  - **Empezar por una configuración es fricción:** por eso son tres elecciones con vista previa sobre sus datos.
  - **Alcance:** 4 formatos × 3 niveles son 12 combinaciones por parte del árbol, además del propio árbol. Para el
    MVP: dos familias, dos formatos completos (gráfico y voz + resumen), textos pregenerados.
  - **Solo cambia con cosas reales** (compromisos, pasos hechos, fechas, contenido nuevo): las bases prohíben
    inventar cifras, y solo hay proyección del plan actual.
  - **Lo visual:** tiene que parecer una lámina botánica, no un dibujo animado. «Tutor y valla» es la parte menos
    intuitiva de la metáfora; hay que probarla con alguien.
- **Coste:** bajo. Textos pregenerados; voz con `edge-tts` en desarrollo.

### Descartadas por Samuel (para la nota del viernes, que pide decir qué se descartó y por qué)

- **Your Plan, Your Way** (agente configurable sin metáfora visual): sola se parece demasiado a un chat sobre el
  plan. Su configuración por persona se ha incorporado a S4.
- **A Message from 2047** (mensaje de voz del yo futuro): de un solo uso y mueve poco a actuar.
- **Sixty Seconds a Day** (el plan por mensajes diarios): la más parecida a un chat. Su hoja diaria está en S4.
- **Money Weather**, **The Check-up**, **Co-Pilots** (parte meteorológico, revisión médica, vuelo): menos motivo
  para volver o tono menos serio que el árbol.

---

## Ideas de David

<!-- David: escribe aquí tus tres ideas (D1, D2, D3) con la plantilla del final. -->

---

## Ideas de Raúl

### R1 · Common Ground — A plan you can interrupt

- **Qué es:** una explicación visual y hablada del plan que puedes interrumpir. Una duda cambia la escena para mostrar lo que necesitas comprender; termina en un primer paso concreto, individual o compartido.
- **Para quién:** familias con o sin asesor. Caso principal: Timothy y Melanie Weah; Samantha como ampliación individual.
- **Cómo lo vive la familia:** dilema propio → explicación → pregunta que transforma la escena → explorar un paso ya calculado → elegir o dejar una duda → ayuda al volver según el obstáculo.
- **Por qué puntúa:** personalización por preguntas expresadas, comprensión visual, participación y seguimiento útil. La adaptación debe ser observable para distinguirse de un tour o chat.
- **Reparto:** Samuel, hechos y lógica de explicación; David, voz e interrupciones; Raúl, experiencia móvil y escenas. Persistencia y contrato adicional pendientes de acuerdo.
- **Riesgos:** parecer un formulario o chat con gráficos; latencia; confundir compromiso con mejora financiera. El MVP prioriza una historia completa y no recalcula futuros ausentes.
- **Coste:** voz base con edge-tts, contenido pregenerado y llamadas acotadas por el proxy.
- **Propuesta completa:** [idea-raul.md](idea-raul.md), con storyboard, demo de dos minutos, alcance, condiciones de los escenarios y comparación con las ideas del equipo.
- **Estado:** propuesta para discutir; no elegida ni implementación iniciada. No se registran votos.

<!-- Raúl: escribe aquí tus tres ideas (R1, R2, R3) con la plantilla del final. -->

---

## Votos

Cada uno rellena solo su columna con sus tres favoritas en orden (por ejemplo `S4, D1, R1`) y una línea de porqué.

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
