# Idea de David · Your Financial Home

> Propuesta de David Sancho (`daviid-sc`) para elegir entre las ideas de los tres.
> 12 nov 2026. Nombre del producto en inglés (el producto va en inglés); el documento, en español.

## Actualización 13 nov · Propuesta de fusión de David: "the house that listens"

Tras leer S1 (Samuel) y R1 (Raúl), apoyo **fusionar las tres**: la casa en el tiempo de S1 como base, pero con
**la interrupción de Raúl en el centro**, un **modo sencillo por defecto** y una personalización que cambie la
experiencia de verdad, no solo el nombre. Frase de pitch: *"Your plan, as your home. Walk through the years — and
stop it anytime to ask."*

### 1. La interrupción, en el centro (de R1)

Recorrer una historia con paradas, por sí solo, es un tour bonito, y Sherpas ya tiene tours. Lo que nos distingue es
que **la casa escucha**: en cualquier momento la familia pregunta (hablando o tocando), la voz se detiene, la casa
enfoca la parte por la que se pregunta y responde con los datos del plan. Eso es lo que hay que enseñar en el pitch.

### 2. Dos modos: sencillo por defecto, explorar para quien quiera más

Tiene que poder usarlo alguien poco digital (una persona mayor, alguien que nunca ha leído un plan). "Funciona para
quien no sabe nada" es la mitad de "Se entiende" (20 puntos).

- **Modo sencillo (por defecto):** una cosa por pantalla y la voz lo hace todo.
  - Se abre y empieza a hablar sola, con voz tranquila.
  - La casa es una imagen quieta (sin 3D ni giros); se ilumina la parte de la que se habla.
  - Un único botón grande **Next**; sin deslizar ni gestos. Si no se toca nada, espera.
  - Para preguntar: un botón grande de micrófono que se **mantiene pulsado para hablar, como un audio de
    WhatsApp**. Si no quiere hablar, dos o tres preguntas escritas en botones grandes (*"What does this mean?"*,
    *"Is this bad?"*, *"What should I do?"*).
  - **"Explain it more simply"** siempre a mano. Letra grande, mucho contraste, subtítulos, nada de jerga sin explicar.
  - Acaba en **una sola cosa que hacer**, en una frase, con un botón **Remind me**.
- **Modo explorar:** todo lo de S1 (deslizar por los años, casa en 3D, dos finales, todos los datos). Para el
  experto o quien disfrute explorando. Así cubrimos a la vez al novato y al experto.
- **Prueba con usuarios reales** (como propone Raúl): probar el modo sencillo con 3–5 personas ajenas al equipo,
  incluida al menos una persona mayor poco digital. Si de verdad funciona, es una frase de pitch honesta y potente.
- **Riesgo técnico menor:** el modo sencillo se puede hacer en 2D (SVG); el 3D solo para el modo explorar, y solo si
  el primer prototipo funciona en el móvil.

### 3. Personal de verdad: para cada familia y para cada persona

Todo sale de los casos (`persona.md` y los JSON), sin inventar nada.

**a) Cada familia tiene una casa distinta, porque su vida es distinta:**

| Familia | Su "casa" | Detalles reales del caso |
|---|---|---|
| Michael | **Un piso de alquiler** ($2,800 al mes) y al lado **un solar con la casa de 2027 en obras** | Su BMW, Austin de fondo |
| Samantha | Casa en propiedad **sin hipoteca** ($900,000) | Su Porsche Cayenne; habitaciones de Ethan (18) y Ava (16) |
| Johnson | Casa con **hipoteca grande** ($560,000) y **sin tejado** (protección 0/20) | Habitaciones de Oliver (11) y Sophia (9); Denver |
| Weah | Casa con hipoteca pequeña ($50,000) | Habitaciones de Liam (6) y Josh (3); San Francisco |

En la línea del tiempo, la habitación de Ethan se queda vacía en agosto de 2026 (empieza la universidad) y la de Ava
en 2028. En el pitch, enseñar dos familias seguidas para que se vea que no es la misma plantilla con otro nombre.

**b) Cada persona ve su parte:**
- Weah: a Timothy le faltan $610,000 de seguro de vida y a Melanie $490,000; cada uno ve **su** hueco.
- Johnson: según el plan, Emily lleva las cuentas de ahorro, el 529 y la de inversión, y Daniel tiene a su nombre la
  tarjeta y el préstamo de estudios; cada uno empieza por lo que gestiona.
- Timothy es "Growth" y Melanie "Moderate": la misma cartera se explica desde el punto de vista de cada uno.

**c) Hablarles de lo que les mueve, sin suponerlo:** `persona.md` trae una motivación (D6) y un estilo de decisión
(D5), marcados como de baja confianza. Se usan solo como **punto de partida**, y lo que diga la persona manda.
- Motivación, para el "para qué": Protección (Weah, Johnson: sus hijos), Libertad (Michael: jubilarse a los 58),
  Deber (Samantha: Ethan y Ava). El seguro de vida no es "una póliza": es proteger a sus hijos.
- Estilo de decisión, para el "cómo": Validator (Samantha) → botón *"How was this calculated?"* con la fuente de cada
  cifra; Collaborator (Weah, Michael) → explicar el razonamiento; Dual (Johnson) → cada uno su parte y luego juntos.
- La pregunta inicial (*"What worries you most?"*) puede corregir todo esto.

**d) Sus propias palabras vuelven a ellos:** lo que preguntó se le recuerda después con sus palabras (*"On Monday you
asked whether you could still buy the house in 2027…"*). Los días 3 y 30 retoman **su** duda. El informe al asesor
separa lo que dijo la familia de lo que dedujo el sistema.

**e) Cifras traducidas con sus propios números:** Weah, la tarjeta cuesta unos $3,240 al año y el efectivo parado da
unos $150; Michael, la hipoteca serían $3,015 al mes frente a $2,800 de alquiler; Samantha, el próximo pago de
Ethan, $12,500, llega en agosto de 2027.

**f) Los avisos llegan cuando su vida lo pide:** Samantha antes de cada agosto (universidad); Michael antes de enero
de 2027 (entrada de la casa y vacaciones de $3,500).

**g) La voz, personal:** dice sus nombres y los de sus hijos bien pronunciados; cada persona elige ritmo y modo
(sencillo o explorar), y el idioma y acento de S1.

Frase de pitch para "Personal": *"Not one template with a different name. Michael lives in a rented apartment with a
dream house under construction. Samantha's house is paid off — but Ethan's room just went quiet."*

### 4. Reparto con esta fusión

- **Samuel:** paradas, hechos y condiciones por familia y por persona (incluidos los datos de 3a–3f), con `guard`;
  interpretar la pregunta y elegir la escena.
- **Raúl:** la casa de cada familia (2D en modo sencillo, 3D en explorar), las escenas que cambian al preguntar, los
  dos modos y la vista de pareja.
- **David:** la voz que hace que la casa **escuche y hable**: narración, pausa y reanudación al interrumpir, preguntas
  habladas (voz a texto, `scribe-v2`) y respuesta hablada; nombres bien pronunciados y ritmo por persona.

---

# Idea original (12 nov)

## En una frase

El plan de la familia se convierte en **su casa**: cada parte de la casa es un pilar de su nota de Sherpas,
se ve al instante qué está sólido y qué está agrietado, una voz la recorre con ellos parte por parte, y cada
acción del plan **repara esa parte de la casa delante de sus ojos**.

## El problema que ataca

Sherpas ya hace los números; lo que falta es que la familia **entienda** su plan y **quiera actuar**. Hoy el plan
son cifras grandes y porcentajes que no dicen si algo va bien o mal, y una nota que puede esconder un problema
(Samantha tiene 82, "strong", y su plan dice que se queda sin ahorros a los 73). Atascos del brief que ataca
directamente: **1** (no ven cómo una decisión de hoy cambia su vida), **2** (las cifras no dicen si es bueno o
malo), **3** (una buena nota esconde un problema), **6** (las malas noticias hacen mirar a otro lado),
**11** (demasiadas opciones y ningún primer paso). Y rellena el hueco que tienen las cuatro familias:
**"Subjective concerns" está vacío** (nadie les ha preguntado qué les preocupa).

## La metáfora: cada pilar es una parte de la casa

Todo el mundo, tenga 30 u 80 años, entiende sin explicación una casa con los cimientos agrietados o sin tejado.
Los cinco pilares de la nota de Sherpas (`score.pillars`) encajan con las partes de una casa:

| Parte de la casa | Pilar de Sherpas | Por qué |
|---|---|---|
| **Cimientos** | Liquidity and emergency fund | Lo que te sostiene cuando algo falla |
| **Tejado** | Insurance and protection | Te protege de lo que cae (el seguro "umbrella" es literalmente un paraguas) |
| **Estructura** | Debt | Lo que carga peso o lo que la agrieta |
| **Instalaciones** (agua y luz) | Savings and cash flow | El dinero que entra y sale cada mes |
| **Jardín** | Investments (y la jubilación) | Lo que crece para el futuro |

Cada parte tiene tres estados (sólido / con grietas / roto) según los puntos del pilar. Ejemplos con datos reales:

- **Michael Carter (26, "critical"):** instalaciones rotas (ahorro y flujo de caja 0/25), cimientos débiles
  (liquidez 4/20: su efectivo cubre unos 3 meses frente a los 5 o 6 recomendados), tejado roto (protección 4/20).
- **Samantha Lewis (82, "strong"):** una casa casi perfecta (deuda 20/20, liquidez 15/15)… hasta que la línea del
  tiempo llega a sus 73 años y el jardín se seca.
- **Daniel y Emily Johnson (52):** casa en pie, pero **sin tejado** (protección 0/20) con dos hijos dentro.

## Cómo lo vive la familia

1. **"What worries you most about your home?"** Antes de explicar nada, una sola pregunta, con cuatro tarjetas
   grandes sacadas de su plan (y una respuesta libre, hablada o escrita). El recorrido empieza por lo que le
   preocupa. Es la primera vez que alguien les pregunta.
2. **Recorrido guiado.** La casa aparece entera; la cámara se acerca a una parte cada vez, una voz la explica en
   una o dos frases con sus cifras, y salen dos botones grandes: *Explain more* y *Next*. Como un asesor en la
   sala, pero a su ritmo.
3. **Repair.** En cada parte dañada, la acción que propone el plan (`score.top_moves`) con la nota antes y después.
   Al comprometerse ("I'll do it" + fecha), **esa parte se repara en la pantalla**. Cuando el plan solo mueve la
   nota con acciones combinadas, se muestran juntas: en los Weah, pagar la tarjeta sola lleva de 60 a 62, pero
   tarjeta + seguro de vida llevan a 73, y añadiendo el umbrella a 78 (`score.combined_moves`).
4. **Línea del tiempo.** Un deslizador debajo de la casa recorre los años del plan (`projections.yearly`): la casa
   envejece con ellos, los hijos se van a la universidad, llega la jubilación. Es donde se ve lo que la nota no
   enseña (el jardín de Samantha se seca a los 73; el de Michael, hacia los 85).
5. **"What if a storm hits?"** Un test de estrés con datos reales: el plan trae cómo se habría comportado **su
   propia cartera** en crisis históricas (`investment-analysis` → `key_metrics.portfolioAnalysis.marketEnvironments`;
   por ejemplo, en la cartera de Samantha, la crisis de 2008 −17,9 % y el COVID −15,5 %). Pasa una tormenta por
   la casa: si los cimientos son débiles, se nota. El fondo de emergencia deja de ser abstracto.
6. **Días después.** La casa sigue ahí. Día 3: un aviso de una frase sobre lo que se comprometieron a hacer.
   Día 30: si lo hicieron, la casa luce reparada y aparece el siguiente paso; si no, la grieta sigue visible.
7. **Para el asesor.** Un informe de una página: qué partes miró la familia, qué le preocupa (rellena "Subjective
   concerns"), qué se comprometió a reparar y cuándo. Los clientes de Sherpas son los asesores: esto les habla a
   ellos directamente.

## Para todos los públicos (también gente mayor)

- **Guiado por defecto, explorar si quieres.** No hay que moverse por ningún mundo: la casa se recorre sola.
- **Un solo gesto: tocar.** Sin arrastrar, sin pellizcar, sin menús escondidos.
- **Texto grande, buen contraste y voz siempre**, para quien ve mal o no quiere leer.
- **Modo experto**: cualquier parte se puede tocar para abrir todos los datos del plan. Sirve al novato y al experto.
- **Versión imprimible**: el "plano" de su casa en PDF para llevar a la reunión con el asesor.

## Que sea serio

Nada de dibujos animados ni de videojuego: **estilo de plano arquitectónico**, como la maqueta de un estudio de
arquitectura. Líneas limpias, colores sobrios; verde, ámbar y rojo solo para el estado de cada parte. Tiene que
transmitir "esto lo ha hecho un profesional", que es el tono de Sherpas y de un asesor.

## Por qué puede ganar (estimación propia, no medida)

| Criterio (puntos) | Cómo lo cubre |
|---|---|
| **Engancha (20)** | Ver tu propia casa agrietada impacta en 3 segundos; la tormenta y la línea del tiempo mantienen la atención |
| **Se entiende (20)** | La metáfora funciona sin saber nada de finanzas; el modo experto da todo el detalle |
| **Mueve a actuar (20)** | Reparar es la acción; se ve el resultado al momento y la casa recuerda lo pendiente los días 3 y 30 |
| **Personal (15)** | Su ciudad, sus hijos en la línea del tiempo, sus cifras, y empieza por lo que **les** preocupa |
| **Creatividad (15)** | No es un chat ni un tour: es una forma nueva de ver un plan; la tormenta y el informe al asesor son extras que no se piden |

## El pitch (2 minutos)

Abrimos con la casa de Samantha, impecable, con su 82 "strong". Movemos el deslizador hasta los 73: el jardín se
seca. *"Her plan says strong. Her house tells the truth."* Después, la casa de Michael (26): elegimos una
reparación y la vemos arreglarse. Cerramos con el informe que recibe el asesor.

## Reparto (encaja con las tres etapas que ya tenemos)

- **Samuel (cerebro):** de los JSON a la casa: estado de cada parte, textos de cada parte por nivel de detalle,
  reparaciones (`top_moves` / `combined_moves`), datos de la tormenta y de la línea del tiempo. Todo pasa por
  `guard`: ninguna cifra que no esté en el plan.
- **Raúl (escena):** la casa en SVG (5 partes × 3 estados), la animación de reparar, el deslizador del tiempo,
  la tormenta y la pantalla de la pregunta inicial.
- **David (voz):** la voz que guía el recorrido y explica cada parte (edge-tts en desarrollo, ElevenLabs para la
  demo), y la respuesta hablada a la pregunta inicial (voz a texto con `scribe-v2`) si da tiempo.

## Alcance del MVP (6 días)

- **Imprescindible:** casa con 5 partes y 3 estados, recorrido guiado con voz, Repair con nota antes y después,
  línea del tiempo. Dos familias completas: **Samantha** (giro de los 73) y **Michael** (casa agrietada).
- **Si da tiempo:** la tormenta, la pregunta inicial hablada, el informe al asesor, los avisos de los días 3 y 30,
  el PDF.
- **Fuera:** cuentas de usuario, envío real de avisos (en la demo se simula con un "viaje en el tiempo").

## Riesgos

- **Lo visual:** la casa tiene que verse muy bien con pocos recursos. Por eso el estilo de plano: es mucho más
  fácil hacerlo elegante que una ilustración detallada.
- **Encajar los pilares en las partes:** los pilares tienen escalas distintas por familia (por ejemplo, ahorro
  sobre 25 en Michael y sobre 30 en los Weah); el estado se calcula en porcentaje de su máximo.
- **No inventar:** la línea del tiempo solo enseña el plan actual (no hay proyección "si haces la reparación");
  lo que cambia al reparar es la nota, que sí viene calculada.

## Coste

Bajo. Textos con un modelo barato (`gpt-5-mini` o `deepseek-flash`), generados y guardados una vez por familia.
Voz pregenerada: edge-tts gratis en desarrollo y ElevenLabs (`eleven-flash-v2.5`) solo para el audio final.

## Ideas que valoré y descarté (para la nota del viernes)

- **Season 1 (el plan como serie):** engancha mucho, pero ver vídeos es pasivo y el tono de "serie" resta seriedad
  a algo que es el dinero de toda una vida.
- **Plan World (el plan como un pueblo o mundo):** gran impacto visual, pero moverse por un mundo puede costar a
  gente mayor o poco digital. Evolucionó a la casa: la misma idea, con una metáfora que todo el mundo entiende.
- **Two Advisors (dos asesores de IA que debaten el dilema de la familia):** explica muy bien las decisiones
  difíciles, pero se acerca demasiado a un chat, que es lo que Sherpas ya tiene.
- **Every Dollar (juego de repartir el dinero sobrante):** muy bueno para el primer paso, pero cubre solo una parte
  del reto, y dos de las cuatro familias no tienen datos de acciones combinadas.
