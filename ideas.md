# Ideas candidatas

Tres ideas por persona. Entre las nueve elegimos una y la enviamos con `/idea` antes del **vie 13 nov a las 22:00**
(10 puntos; hay que decir qué construimos y por qué, y qué descartamos y por qué: las ocho que no elijamos sirven
para esa segunda parte).

**Cómo añadir las tuyas:** escribe solo dentro de tu sección (abajo), con la misma plantilla. No edites las de otro;
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

### S1 · First Move

- **Qué es:** una experiencia de dos minutos en el móvil, una por cada persona de la familia, que acaba en un único
  primer paso acordado, con cómo hacerlo y una fecha. Vuelve los días 3 y 30.
- **Para quién:** familias con o sin asesor. Caso principal de la demo: los Weah (pareja). Segundo: Michael Carter
  (una persona sola, nota 26).
- **Cómo lo vive la familia:**
  1. Empieza con una pregunta, no con la nota: «Timothy, what worries you most?» y cuatro tarjetas sacadas de su plan.
  2. La app responde a esa preocupación con dos o tres cifras del plan hechas tangibles.
  3. Cada miembro de la pareja ordena los pasos del plan en su móvil, por separado.
  4. La app enseña dónde coinciden y dónde no, y propone un primer paso común con la nota antes y después
     (`combined_moves`).
  5. Compromiso: un paso, instrucciones concretas y una fecha. Día 3 y día 30: «¿lo hiciste?», la duda típica de ese
     momento y el siguiente paso.
- **Por qué puntúa:** la familia hace cosas (elige, ordena, se compromete) en vez de escuchar. Ataca cuatro de los
  atascos del brief: la pareja que no actúa hasta ponerse de acuerdo (8), demasiadas opciones sin primer paso (11),
  la preocupación que nadie ha preguntado (4) y leer a ratos en el móvil (5). Cubre el extra de los días después.
- **Argumento para el pitch:** las respuestas rellenan el «Subjective concerns» que hoy está vacío. El asesor llega
  a la reunión sabiendo qué le importa a cada uno y en qué discrepan, y el cliente de Sherpas es el asesor.
- **Reparto:** Samuel genera el recorrido por persona desde `cases/` (tarjetas, cifras, pasos, paso común) con
  `gpt-5-mini` y `guard`. Raúl hace la web móvil (tarjetas, ordenar, pantalla de coincidencias, botón «día 3 / día 30»
  para la demo). David hace los mensajes de seguimiento y la voz opcional pregenerada.
- **Riesgos:** sincronizar dos móviles en directo puede fallar en la demo (plan B: dos pestañas en una pantalla).
  El contrato `Presentation` actual no encaja y hay que cambiarlo entre los tres.
- **Coste:** bajo. Solo texto, generado una vez por familia y guardado.

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

### Comparación de las tres (estimación de Samuel, no medida)

| Criterio (puntos) | S1 First Move | S2 Message from 2047 | S3 Sixty Seconds |
|---|---|---|---|
| Engancha (20) | Alto | Muy alto | Medio |
| Se entiende (20) | Alto | Medio | Alto |
| Mueve a actuar (20) | Muy alto | Bajo | Alto |
| Personal (15) | Muy alto | Alto | Medio |
| Creatividad (15) | Alto | Alto | Bajo |
| Dificultad en 6 días | Media | Media | Baja |

**Preferencia de Samuel:** S1. Se le puede añadir lo mejor de S2 (una frase de voz al comprometerse) y de S3 (los
mensajes de los días 3 y 30) sin cambiar de idea.

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
