# Idea de David · Your Financial Home

> Propuesta de David Sancho (`daviid-sc`) para elegir entre las ideas de los tres.
> 12 nov 2026. Nombre del producto en inglés (el producto va en inglés); el documento, en español.

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
