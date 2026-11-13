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

### S5 · Home Story — scroll through your plan (idea final de Samuel; nombre provisional)

- **Qué es:** una web interactiva en **3D** en la que la familia ve su plan como **su casa** y lo recorre con el
  dedo, **hacia delante y hacia atrás a su ritmo**. La casa empieza más o menos dañada según su nota de Sherpas; al
  avanzar por el plan se ve cómo se arregla cada parte, y el recorrido acaba en dos finales: la casa si siguen el
  plan y la casa si no lo siguen.
- **Cómo se mueve:** la página no se desplaza; el gesto (dedo o rueda) hace avanzar la escena actual y, al acabar,
  pasa a la siguiente. Al retroceder se entra por el final de la escena anterior. Nada avanza solo.
- **La casa de partida sale de la nota:** la nota global (`score.published_score` y su banda) fija el estado
  general y cada pilar (`score.pillars`) el de su parte. Michael (26, *critical*): casa muy dañada. Johnson (52,
  *vulnerable*): en pie y sin tejado. Weah (60, *stable*): estructura agrietada por la tarjeta. Samantha (82,
  *strong*): casi impecable.
- **Dos finales:**
  - **If you follow the plan:** todas las partes reparadas y la nota de llegada (Weah: 78).
  - **If you don't:** la casa tal como la deja el plan actual (`projections.yearly`). Puede seguir en pie y tener
    el jardín seco: es el caso de Samantha, con buena casa y activos líquidos agotados en 2053.
- **El asesor anota y la casa cambia:** en una vista aparte, el asesor apunta las dudas que van saliendo y marca
  qué pasos da por hechos y cuáles no. La casa de la familia se actualiza con esa combinación y enseña su
  consecuencia (Weah: sin el seguro de vida, la nota se queda en 62 en vez de 73). Las notas rellenan el
  «Subjective concerns» vacío. El asesor elige entre escenarios que el plan ya trae calculados; no cambia cifras.
- **Cómo llega:** es **un enlace que el asesor entrega a la familia**. Sin instalar nada ni crear cuenta: lo abren
  en el móvil y ahí está su plan completo, con su casa de hoy, su línea del tiempo y la casa como quedaría si hacen
  los pasos del plan.
- **Cada persona elige cómo quiere que se lo enseñen** (tres formas del mismo contenido, siempre a un toque):
  1. **Deslizar** (por defecto): la casa y la línea del tiempo.
  2. **Botón «Read it»:** todo el recorrido pasa a un resumen escrito, con las mismas paradas y cifras.
  3. **Botón «Listen»:** una voz lee ese resumen. Antes de empezar se elige **idioma y acento**.
  La elección se guarda por persona: en una pareja, uno puede deslizar y la otra escuchar el mismo plan.
- **De dónde sale cada pieza (es una fusión, no una idea nueva):**

  | Pieza | Viene de | Qué se conserva |
  |---|---|---|
  | La casa y sus cinco partes | David, `idea-david.md` | Cimientos = liquidez, tejado = protección, estructura = deuda, instalaciones = ahorro, jardín = inversiones. Reparar una parte = un paso del plan. Estilo de plano arquitectónico. |
  | Deslizar por el tiempo | Las «estaciones» de S4 y la línea del tiempo de David | Deja de ser un deslizador debajo del dibujo: el propio scroll de la página es la línea del tiempo. |
  | Una vista por persona | S4 | En pareja, cada uno abre la misma casa con su nombre y elige por dónde empieza. Sin pantalla de configuración previa. |
  | Elegir el formato | «Your Plan, Your Way» y S4 | Deslizar, leer o escuchar; sin configuración previa, son dos botones siempre visibles. |
  | Parar y preguntar | Raúl, `idea-raul.md` | En cualquier momento del recorrido, «Wait…» detiene el scroll y la casa enfoca la parte por la que se pregunta. |

- **Referencia de estilo:** [El cens del tallat](https://www.cens-del-tallat.domesticstreamers.com/) (Domestic
  Data Streamers), pero con la casa. Cómo está hecha (mirado el 13 nov): un solo HTML con `three.js`, una escena 3D
  a pantalla completa construida con cajas y cámara ortográfica (aspecto de maqueta), y **escenas encadenadas**: la
  página no se desplaza de verdad, la rueda o el dedo hacen avanzar la escena actual y, al acabar, pasa a la
  siguiente. Empieza con «entrar con sonido / sin sonido» y un selector de idioma. Se toma la técnica y el tono, no
  su código ni su diseño.
- **Para quién:** familias con o sin asesor, en el móvil (un solo gesto: deslizar con el pulgar). Demo: Samantha
  Lewis (el giro) y los Weah (la pareja y el paso).
- **Cómo lo vive la familia (cada punto es una parada del scroll):**
  1. **Today.** Su casa entera en 3D, con sus nombres y su nota; se puede girar con el dedo. En tres segundos se
     ve qué está sólido y qué agrietado (`score.pillars`). Johnson: casa en pie y sin tejado (protección 0/20) con dos hijos dentro.
  2. **What worries you most?** Una pregunta con cuatro tarjetas sacadas de su plan. La respuesta decide qué parte
     se enfoca primero y rellena el «Subjective concerns» que hoy está vacío en las cuatro familias.
  3. **Room by room.** Al deslizar, la cámara pasa por cada parte con una frase y su cifra. «Show me why» abre el
     detalle; quien no quiera leer, pulsa la voz.
  4. **The first repair.** La parte más dañada y el paso que propone el plan, con la nota antes y después
     (`score.top_moves`, `score.combined_moves`). Weah: pagar $6.800 de la tarjeta lleva de 60 a 62; con el seguro
     de vida, a 73. Al comprometerse con una fecha, esa parte se repara en pantalla.
     **Today / If you follow the plan:** un conmutador enseña la casa de hoy y la casa con todos los pasos hechos
     (cada paso repara su parte), con la nota de llegada (Weah: 60 → 78 con tarjeta, seguro de vida y umbrella).
  5. **The years ahead.** Se sigue deslizando y pasan los años (`projections.yearly`, `goals.chartGoals`): cada
     objetivo con fecha es una parada. Weah: coche en 2028, casa en 2030, universidad de Liam en 2038, jubilación
     en 2048. La deuda baja en la estructura hasta desaparecer (Weah: 2059).
  6. **The moment the plan breaks, if it does.** Samantha: nota 82 y casa impecable hasta que el scroll llega a
     2053 y el jardín se seca (`BANKRUPTCY_ZEROCASH`, a los 73). Michael: 2075. Es lo que la nota no enseña.
  7. **Two endings.** Las dos casas, una junto a otra: siguiendo el plan y sin seguirlo.
  8. **Your next step.** La página acaba en una tarjeta: el paso elegido, la fecha y lo que falta comprobar. Día 3
     y día 30: al volver, el scroll se abre en esa reparación, hecha o pendiente.
- **Por qué puntúa:**
  - **Engancha (20):** deslizar es el gesto que ya hace todo el mundo en el móvil; no hay que aprender nada.
  - **Se entiende (20):** una casa agrietada o sin tejado se entiende sin saber de finanzas, y el tiempo se
    entiende porque se recorre.
  - **Mueve a actuar (20):** la reparación está dentro del recorrido, con nota antes y después, y el final de la
    página es el primer paso.
  - **Personal (15):** sus nombres, sus hijos y sus fechas son las paradas; empieza por lo que les preocupa, y
    cada persona lo recibe como mejor lo entiende: deslizando, leyendo o escuchando en su idioma y acento.
  - **Creatividad (15):** no es un tour ni un chat (lo que Sherpas ya tiene): es el plan contado como una
    historia que avanza con el dedo.
  - Atascos del brief que ataca: 1, 2, 3, 6 y 11.
- **Integración en Sherpas:** una página web que lee el mismo JSON que Sherpas ya produce; el asesor comparte su
  enlace (una URL por familia) o se incrusta (`iframe`) en la página del plan. No conocemos su stack: es una decisión de diseño, no algo probado.
- **Reparto:** Samuel (cerebro): de los JSON a la lista de paradas de cada familia (estado de cada parte, año,
  cifra, texto y paso), todo por `guard`. Raúl (escena): la casa en 3D con `three.js`, hecha de cajas (5 partes × 3 estados), las
  escenas y el gesto que las mueve, la vista del asesor, la reparación, el «Wait…» y los botones «Read it» / «Listen». David (voz): la narración de cada parada,
  la pausa al interrumpir y el selector de idioma y acento (voces de `edge-tts`).
  El contrato `Presentation` casi sirve: una escena pasa a ser una parada; faltan el año y la parte de la casa
  (campos opcionales, regla 2).
- **Riesgos:**
  - **La casa solo puede cambiar con datos reales.** Los pilares son de hoy; año a año solo hay patrimonio, deuda
    y activos invertibles del plan actual. En el tiempo cambian la estructura (deuda), el jardín (inversiones) y
    las paradas (objetivos); tejado y cimientos no se inventan a futuro.
  - **No hay proyección «si hago el paso».** Al reparar cambia la nota (calculada), no los años siguientes. La
    «casa si sigues el plan» enseña las partes reparadas y la nota de llegada, no una línea del tiempo nueva.
    Samantha y Michael no tienen `combined_moves`: su casa objetivo solo puede enseñar pasos sueltos.
  - **Idiomas:** las bases exigen producto, demo y explicación **en inglés**. El inglés es el idioma por defecto y
    el de la demo; los acentos del inglés (EE. UU., Reino Unido, Australia, India…) son gratis con `edge-tts`.
    Otros idiomas obligan a traducir y a pasar `guard` por cada uno: para el MVP, como mucho uno (español), y solo
    si da tiempo.
  - **Tres formatos son tres cosas que mantener:** el resumen escrito y el audio salen del mismo texto de las
    paradas, no se escriben aparte.
  - **50 años de scroll cansan:** se salta de parada en parada (unas 8 por familia), no año a año.
  - **El 3D con escenas encadenadas es lo más caro de construir** y cae casi entero en Raúl, que contaba con un
    SVG en 2D. Hay que probar una parte de la casa en el móvil el primer día; plan B: la misma casa en SVG con
    botones «Next» / «Back».
  - **El final bueno no siempre arregla el jardín.** Los pasos de Samantha suben la nota de 82 a 84 (seguro de
    hogar), pero el plan no trae calculado un escenario en el que sus activos dejen de agotarse. Su final «si
    sigues el plan» no puede enseñar un jardín sano sin inventarlo: hay que decirlo tal cual o elegir a los Weah
    para ese final.
  - **La vista del asesor añade una segunda pantalla y estado compartido** (lo que marca el asesor tiene que
    llegar a la casa de la familia). Para el MVP: los dos en el mismo dispositivo o un parámetro en el enlace.
  - **El asesor solo puede variar entre escenarios ya calculados** (`top_moves`, `combined_moves`); Samantha y
    Michael solo tienen pasos sueltos.
  - **Que parezca una infografía pasiva:** por eso la pregunta inicial, la reparación y el «Wait…» cambian lo que
    se ve.
- **Coste:** bajo. Textos y voz pregenerados por familia (`edge-tts` en desarrollo); llamadas al modelo solo para
  las preguntas libres.

### Descartadas por Samuel (para la nota del viernes, que pide decir qué se descartó y por qué)

- **S4 · The Family Tree** (el plan como árbol vivo, una rama por persona): mismo tipo de idea que la casa, con
  partes menos intuitivas («tutor y valla» para los seguros) y una configuración inicial de doce combinaciones.
  De ella quedan en S5 el recorrido por los años y la vista por persona. Texto completo en el historial de git.
- **Your Plan, Your Way** (agente configurable sin metáfora visual): sola se parece demasiado a un chat sobre el
  plan.
- **A Message from 2047** (mensaje de voz del yo futuro): de un solo uso y mueve poco a actuar.
- **Sixty Seconds a Day** (el plan por mensajes diarios): la más parecida a un chat.
- **Money Weather**, **The Check-up**, **Co-Pilots** (parte meteorológico, revisión médica, vuelo): menos motivo
  para volver o tono menos serio.

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
