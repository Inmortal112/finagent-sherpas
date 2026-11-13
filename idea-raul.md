# R1 · Common Ground — A plan you can interrupt

Propuesta de Raúl · 13 de noviembre de 2026 · Preparada para discusión del equipo, pendiente de elección. Nombre provisional.

## La propuesta

**Convertir el plan de Sherpas en una explicación visual y hablada que la familia puede interrumpir: cuando una persona expresa qué no entiende o qué le preocupa, cambia la escena para explicárselo.** Cada persona puede profundizar a su ritmo y terminar con un primer paso concreto. En pareja, dos perspectivas sobre el mismo plan pueden converger en una decisión compartida.

Frase para el pitch: **“One plan. Different questions. A next step you understand.”**

La presentación inicial describía una mesa de decisiones. Esta versión concreta su identidad: una explicación que escucha, se detiene y muestra lo necesario para resolver una duda. La mesa es una pantalla de apoyo, no la apertura ni toda la experiencia.

## Por qué encaja con el reto

Sherpas ya recoge datos, calcula y redacta el plan. El reto consiste en llevar a una familia a entenderlo y querer actuar, con o sin una reunión posterior. El material del evento destaca que el asesor puede percibir una duda y ajustar su explicación; cuando el plan llega solo, esa adaptación desaparece. Queremos recuperar esa capacidad en móvil.

Los cuatro casos no registran preocupaciones subjetivas. Preguntaremos qué necesita entender cada persona, sin inventarle un miedo a partir de su perfil. La IA selecciona y adapta explicaciones basadas en el plan; no sustituye su motor de cálculo.

## Tres momentos que deben hacer memorable el producto

### 1. La escena responde a tu pregunta

Los Weah ven juntos su efectivo disponible y la tarjeta al 18 %. La voz explica brevemente el paso propuesto por el plan. Durante la explicación, la persona toca “Wait…” o utiliza el micrófono y pregunta: “What happens to our safety cushion?”

El audio se detiene. La vista de deuda se aparta y la pantalla enfoca la reserva, el importe del paso y las necesidades recogidas en el plan. La voz responde a esa pregunta mientras señala los elementos correspondientes. El contexto de la deuda sigue accesible, sin empezar otra conversación desde cero.

Otra pregunta, “Why does my score barely change?”, produce otra escena: explica los límites de deuda y protección que condicionan la nota. “Explain it more simply” reduce la información visible y cambia la narración. “Show me the numbers” abre detalle y procedencia.

**Lo sorprendente debe ser la relación entre la pregunta y el cambio visual.** No basta una animación vistosa ni repetir una respuesta debajo de un gráfico fijo.

### 2. Dos personas, dos formas de entender el mismo plan

En la demo, Timothy elige entender el coste de la tarjeta y Melanie el colchón. Son elecciones de los actores, no características que afirmemos conocer de los clientes sintéticos.

En dos paneles del proyector se ven las dos explicaciones. Si podemos terminarlo y probarlo, cada panel vendrá de una sesión real en un teléfono; si no, se presentará honestamente como selector de perspectiva en un dispositivo.

Al volver a la decisión, aparecen las respuestas de cada persona: “Ready”, “I have a question” o “Not now”. Compartir una pregunta requiere que su autor lo decida. Una duda puede reabrir la escena adecuada; no se fuerza el acuerdo.

Cuando ambos eligen el paso, las dos perspectivas convergen visualmente en una tarjeta común. Esa transición es el cierre emocional: la familia comparte qué entiende y qué quiere hacer. En modo individual, la tarjeta se genera directamente, sin una segunda persona ficticia.

### 3. Al volver, la ayuda recuerda dónde te quedaste

La tarjeta guarda el paso elegido, el motivo escrito o confirmado por la persona, lo que falta comprobar y una fecha opcional. En el regreso del día 3, se pregunta qué ha ocurrido.

- “Done”: se registra como declarado por la persona, sin actualizar las cifras financieras originales.
- “I still have a question”: se retoma la explicación pertinente con su contexto.
- “I don't know how to start”: se prepara una lista breve o preguntas para el asesor.
- “Not now”: se revisa o pospone la decisión, sin penalización.

El retorno tiene utilidad porque ayuda con un obstáculo concreto. No requiere contenido diario nuevo ni una mascota que se deteriore por no entrar.

## Storyboard de la experiencia

| Pantalla | Lo que ve la familia | Interacción y propósito |
|---|---|---|
| **Your plan, starting with you** | Nombres, un dilema del caso y una frase breve. | Empezar o elegir la pregunta que importa. Sin configuración obligatoria. |
| **See what your plan means** | Una escena a pantalla completa, voz opcional y texto legible. | Pausar, tocar “Wait…”, preguntar o abrir detalle. |
| **The part you asked about** | La escena enfoca reserva, deuda, protección u objetivo según la pregunta. | Resolver la duda; cambiar de explicación si sigue sin entenderse. |
| **Explore this step** | Estado actual, propuesta de Sherpas, resultado calculado y condiciones. | Explorar sin ejecutar; comprobar qué sigue pendiente. |
| **Your next step** | Elección individual o compartida, motivo, requisitos y siguiente acción. | Guardar, cambiar de opinión o dejar una pregunta abierta. |
| **Pick up where you left off** | Lo acordado y la última duda que la persona quiso guardar. | Registrar lo ocurrido y recibir ayuda acorde. |

## Cómo debe verse y sentirse

- Diseño pensado primero para móvil: fondo marfil, texto azul oscuro, un color de acento y espacio generoso. Una cifra principal por escena, etiquetas directas y fuentes disponibles.
- Tipografía grande, voz calmada, subtítulos y controles visibles. La información no depende únicamente del color o del audio.
- Animaciones breves que expliquen relaciones: enfocar el colchón, separar deuda y protección, unir dos elecciones. Movimiento reducido disponible.
- El detalle financiero se abre progresivamente. La primera pantalla no es un dashboard con cinco gráficos ni un formulario de preferencias.
- Evitar incendios, ruina, árboles muertos o lenguaje culpabilizador. Una dificultad se presenta como algo que se puede entender y abordar.
- No simular rasgos psicológicos, medir emociones por cámara ni clonar la voz de familiares. La adaptación se basa en lo que la persona expresa.

La estética es una hipótesis de diseño. Debe probarse con personas ajenas al equipo, especialmente para comprobar que no parezca un juego infantil ni una herramienta financiera intimidante.

## El ejemplo real que podemos demostrar

Fuente: `cases/timothy-melanie-weah/financial-health.json`.

- `score.top_moves`: pagar **6.800 USD** de una tarjeta de **18.000 USD**, dejando **11.200 USD**; nota modelada **60 → 62**.
- Añadir cobertura de vida por sí solo puede dejar la nota en 60. La explicación debe mostrar que protección y puntuación no son lo mismo.
- La combinación de pago y cobertura puede llevar a **73**, con la condición de cobertura total de **491.800 USD** indicada en `score.combined_moves`. La cantidad de cobertura de la acción individual no se puede reutilizar sin esa condición.

No presentaremos “pagar toda la tarjeta” como si fuera ese escenario ni sumaremos incrementos de nota. El objetivo es comprender el paso, no maximizar puntos. Un compromiso no cambia el saldo ni la nota actuales. La proyección año a año describe el plan actual; no se reescribe al tocar una tarjeta.

Para Samantha, un segundo recorrido individual podría explicar la diferencia entre su nota de **82**, los activos líquidos y su agotamiento proyectado a los **73**. No implica que no tenga patrimonio a esa edad, ni que una acción que sube la nota solucione su jubilación. Es un buen caso de contraste, pero el pitch principal debe contar una sola historia completa.

## Demo de dos minutos

| Tiempo | Acción observable | Mensaje |
|---|---|---|
| 0–12 s | Dos nombres y el dilema del plan Weah. | “Sherpas has done the analysis. Now each person needs to understand it.” |
| 12–35 s | Empieza la explicación. Una pregunta sobre el colchón interrumpe la voz y transforma la escena. | El producto escucha una duda y cambia cómo explica. |
| 35–60 s | Mostramos la segunda perspectiva, centrada en deuda, sobre el mismo plan. | Personalizar significa responder a preguntas diferentes. |
| 60–85 s | Exploran el paso; aparece qué queda pendiente. Cada participante responde y se guarda el siguiente paso. | Entender antes de comprometerse; puede quedar una pregunta abierta. |
| 85–108 s | Control rotulado “Demo: day 3”. Eligen una dificultad y se retoma ayuda relevante. | La explicación continúa después de la primera sesión. |
| 108–120 s | Vista previa de la ficha para el asesor: preocupaciones expresadas, preguntas y paso elegido. | El asesor puede empezar por la conversación que la familia necesita. |

Ensayar una ruta clara, pero permitir que al menos una pregunta o elección cambie realmente el resultado. Si todo reproduce un vídeo prefijado, la demostración no prueba la propuesta.

## Cómo se materializa sin depender de magia

Tres tipos de escenas cuidadosamente diseñadas bastan para empezar: reserva, deuda y protección. Cada una tiene una explicación breve y otra detallada. Los datos se extraen de fuentes concretas y se validan antes de mostrarse o narrarse.

La IA identifica la intención de la pregunta y selecciona una escena y sus hechos. Puede adaptar el lenguaje dentro de esos hechos. Una pregunta fuera del alcance produce una limitación explícita o una pregunta preparada para el asesor. El estado de la decisión y los cálculos no se delegan al texto libre del modelo.

Para validar la adaptación, probar varias formulaciones de la misma preocupación y preguntas distintas, no solo la frase exacta del pitch. Medir latencia y que la respuesta visual corresponda. Las rutas predefinidas mediante botones garantizan acceso y una demo estable; el micrófono y las preguntas libres añaden la interrupción natural cuando estén probados.

`Presentation` puede seguir transportando hechos, escenas y audio, pero no representa sesiones, decisiones o respuestas de usuarios. Acordar un contrato adicional pequeño antes de implementar. El guard actual tampoco garantiza por sí solo que un número esté asociado a la condición correcta.

## Alcance y reparto

**Entrega esencial:** Weah, explicación visual y voz, tres escenas, cambio de explicación por pregunta seleccionada, dos perspectivas en un dispositivo, un paso completo guardado, regreso del día 3 y ficha básica. Debe funcionar sin sonido.

**Prioridad de ampliación:** preguntas libres que cambian escenas; interrupción por voz; dos dispositivos con estado compartido; Samantha individual; exportación. Si alguna ampliación falla, conservar la utilidad de la experiencia básica. No llamar “voz interactiva” a la versión que solo admite botones.

**Samuel:** hechos, condiciones, lógica de explicación, selección de escenas y validación. **David:** voz, pausa y reanudación, respuesta hablada y entrada de voz si entra en alcance. **Raúl:** diseño móvil, escenas, perspectiva individual/pareja, transiciones y flujo de decisiones. La persistencia y sincronización requieren un dueño explícito acordado entre los tres.

Textos y voz base pregenerados; llamadas limitadas para preguntas libres. Desarrollo con edge-tts, audio final opcional por el proxy. Mantener los 50 USD de equipo y el sublímite de 1,40 USD de ElevenLabs. No es necesario consumir créditos para presentar esta propuesta.

## Relación con las ideas de Samuel y David

La casa de David tiene una metáfora especialmente clara para protección y reserva. El árbol de Samuel aporta la visión de cada persona y continuidad. Ambas son factibles como SVG acotados; el tiempo dependerá del número de estados e interacciones, no solo de dibujar el objeto.

Nuestra propuesta comparte ingredientes que ellos ya han planteado: preocupaciones personales, pareja, seguimiento y ficha del asesor. Su contribución principal es organizar el producto alrededor de una **explicación que cambia al recibir una duda**, y hacer visible esa adaptación durante la demo.

Proponemos probar una escena de reserva/protección con la casa y otra con gráficos directos. Si la casa ayuda a comprender mejor, usarla en esa escena y reconocer la contribución de David. Lo mismo con una vista de objetivos del árbol. No es necesario mezclar las dos metáforas completas.

La diferencia respecto a un tour o un chat debe ser observable: una pregunta cambia la representación y el recorrido; las respuestas de la persona influyen en la ayuda posterior. Es una apuesta de producto, no una afirmación de originalidad absoluta.

## Evaluación y riesgos

| Criterio | Qué intentamos conseguir | Riesgo a comprobar |
|---|---|---|
| Engancha, 20 | Interrupción y cambio visual pertinente en los primeros segundos. | Mucha introducción o latencia antes de mostrar valor. |
| Comprensión, 20 | Mostrar relaciones, adaptar profundidad y detectar dudas restantes. | Animación bonita que oculta condiciones o unidades. |
| Ganas de actuar, 20 | Primer paso realizable y ayuda según el obstáculo. | Confundir pulsar un botón con actuar en el mundo real. |
| Personal, 15 | Preguntas expresadas, distintos ritmos y vista individual/pareja. | Cambiar solo nombres o estilos sin cambiar la explicación. |
| Creatividad, 15 | El plan responde visualmente; dos perspectivas se conectan. | Parecer otro chat con gráficos decorativos. |
| Nota del viernes, 10 | Elección razonada y alternativas descartadas. | Prometer más de lo que podremos demostrar. |

Antes de elegir definitivamente, enseñar una secuencia breve a entre tres y cinco personas ajenas al proyecto. Pedir que expliquen qué han entendido, qué queda pendiente y qué harían después. Preguntar qué recuerdan sin sugerir la respuesta. Observar si saben que explorar o elegir aún no ejecuta la acción.

Revisar la idea si no pueden describir el cambio que produjo su pregunta, si no recuerdan el paso o si la experiencia parece un cuestionario. No inventar puntuaciones esperadas del jurado ni prometer mejoras comerciales sin evidencia.

## Valor para Sherpas

Una familia puede llegar al asesor con más contexto y dudas concretas; quien no tenga reunión dispone de una explicación adaptable y un primer paso útil. La ficha se comparte tras revisión del usuario, separando expresiones propias de interpretaciones del sistema. El valor comercial es una hipótesis que habría que medir.

El producto puede empaquetarse como una experiencia vinculada al plan y un contrato de datos. Podemos mostrarlo incrustado en una página de ejemplo; no conocemos ni hemos probado su integración de producción con Sherpas.

## Estado y siguiente paso

Material: brief, reto, presentaciones UPV/MCP aportadas, casos locales, `ideas.md`, `idea-david.md` y `visitas/` del main descargado el 13 de noviembre (commit observado `d06a56b`). Sin pruebas de usuario realizadas todavía.

Tras discutir esta propuesta con Raúl, compartirla con el equipo en `idea-raul.md`, enlazarla desde su sección en `ideas.md` y añadir una entrada a `visitas/raul.md`, mediante rama y PR. No registrar una decisión conjunta ni un voto de otro miembro. Git autenticado sigue pendiente; la sesión de navegador sí permite acceso al repositorio privado.
