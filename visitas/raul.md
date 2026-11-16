# Visitas — Raúl (escena: `stage.py`)

<!-- Añade tu entrada más reciente justo debajo de esta línea. Plantilla en visitas/README.md -->

## 2026-11-16 — feat/stage-architectural-review · diseño de toda la web — Codex
- **Hecho:** extendida la revisión a portada, puntuación, capítulos numerados, navegación con progreso, proyecciones, propuestas, elección de paso y panel de preguntas. Azul noche, tarjetas claras y acentos iris; se mantienen Poppins y los colores del proyecto.
- **Escena:** cordilleras en tres capas, bosque mixto agrupado, plantación y flores; luz direccional y cámara más baja. Corregido el dato de color de las flores que activó temporalmente el respaldo 2D.
- **Verificado:** 171 tests, ocho páginas con voz mock; escritorio 1440×1000 y móvil, lienzo 3D activo, sin desborde horizontal. Rueda manual hasta 814.7 muestra la casa aún fijada.
- **Para Samuel y David:** conservados vuestros contenidos, partes, estados, clima y narraciones. Sin cambios de contrato, backend o voz ni consumo de servicios de IA. No se suman puntuaciones ni se confunde scroll con completar acciones.
- **Siguiente:** revisión visual de Raúl y fluidez en iPhone real. Cambios guardados solo en la rama local hasta aprobar la publicación.

## 2026-11-16 — feat/stage-architectural-review · scroll manual y ambiente — Codex
- **Hecho:** corregido el fallo señalado por Raúl: la escena queda fijada durante el descenso y muestra la casa antes de liberarse. Quitado el `overflow: hidden` que anulaba el sticky. No se transfiere el lienzo con el descenso a medias.
- **Verificado:** rueda manual, sin botón: scroll 603 con foto en y=72; scroll 814 con casa completamente visible, aún fijada. 171 tests funcionales y sintaxis JS correcta.
- **Ambiente:** horizonte continuo, sombra suave en nubes, césped y cubierta con textura fina y reflejos del cristal más discretos; se conserva el clima según puntuación.
- **Para Samuel y David:** solo escena y documentación de Raúl; sin nuevas dependencias ni cambios en datos, contrato o voz.
- **Siguiente:** revisión de Raúl y prueba real de fluidez en iPhone; sigue local hasta aprobar la publicación.

## 2026-11-16 — feat/stage-architectural-review · bajada original desde nubes — Codex
- **Hecho:** restaurada, a petición de Raúl, la trayectoria original `INTRO` y la capa alta de 26 nubes; el scroll baja hasta la casa. Sustituye el giro de llegada añadido en la cuarta revisión.
- **Decisiones:** se mantiene la contención para no atravesar textos. El botón reproduce la bajada en 2,2 s; cualquier entrada manual la interrumpe. No cambia la puntuación ni marca pasos hechos.
- **Estado:** `check.sh`: 171 tests; JS correcto; comprobado inicio sobre nubes y llegada al plan con nota original 82.
- **Para Samuel y David:** se conserva vuestra transición original, mejor encajada en el diseño de revisión. Sin cambios de contrato, backend ni voz.
- **Siguiente:** revisión visual de Raúl y prueba en iPhone real. Sigue sin publicar en GitHub.

## 2026-11-16 — feat/stage-architectural-review · paisaje, cámara y cabecera — Codex
- **Hecho:** recuperados terreno, montañas, árboles y pájaros articulados; tarjeta de puntuación nueva, centrada y con contexto. El clima sigue vuestra puntuación original.
- **Decisiones:** eliminado el lienzo fijo que atravesaba la página. Un único renderizador vive en cajas reales; conserva una imagen local al salir y anima giro/acercamiento al entrar. Continúa el movimiento de agua, nubes y jardín.
- **Estado:** `check.sh`: 171 tests; JS correcto. Navegador: 1280×800, 390×844 y 390×600; puntuación centrada, sin desborde del panel y con un solo lienzo.
- **Para Samuel y David:** cambios solo en escena y documentación de Raúl. Sin cambios de datos, contrato, backend o narraciones. iPhone real pendiente.
- **Siguiente:** valoración visual y de movimiento de Raúl; no publicado ni integrado hasta su aprobación.

## 2026-11-16 — feat/stage-architectural-review · clima y recorrido — Codex
- **Hecho:** a petición de Raúl, recuperado el clima original según puntuación (lluvia/día/atardecer), con materiales y luz mejorados; escena delimitada, cámara más suave y sin encuadres extremos.
- **Estado:** `check.sh`: 171 tests; sintaxis JS; ocho páginas; navegación de 1/12 a 10/12 y revisión en escritorio y móvil.
- **Decisiones:** puntuación y contexto fuera del dibujo; Back/Next y contador de capítulos; resumen inicial desplegable; textos opacos y anclaje al cambiar tamaño. Leer no completa pasos ni mejora la nota.
- **Para Samuel y David:** se conserva vuestra lógica y paletas del clima; Michael 26 sigue lluvioso y su simulación individual 62 cambia a despejado sin registrar pasos completados. Sin cambios de backend, contrato ni voz.
- **Siguiente:** revisión de Raúl y prueba en iPhone real; la rama continúa local hasta autorizar publicación.

## 2026-11-16 — feat/stage-architectural-review · segunda revisión — Codex
- **Hecho:** tras valorar Raúl que quedaba apagado: azul/violeta, sol lateral, sombras más profundas, cristal con reflejos, agua con ondas y vegetación más llena.
- **Estado:** `VOICE_ENGINE=mock bash check.sh`: 171 tests; ocho páginas; sintaxis JS correcta; revisión en escritorio y móvil.
- **Decisiones:** entrada con pregunta sugerida de cada caso y, si existe, edad de agotamiento ya suministrada por el plan. Navegación nombra conceptos financieros. Sin proyecciones nuevas ni narraciones modificadas.
- **Para Samuel y David:** misma rama local; sin publicación hasta aprobación de Raúl. Backend, contrato y voz sin cambios; iPhone real pendiente.
- **Siguiente:** valoración visual de la segunda versión y aprobación para compartir en GitHub.

## 2026-11-16 — feat/stage-architectural-review — Codex
- **Hecho:** propuesta local sobre PR #60: casa protagonista, materiales y luz, identidad visual y separación entre explorar, simular y completar. Detalle en `02-DOCS/ftd/stage-architectural-review.md`.
- **Estado:** `VOICE_ENGINE=mock bash check.sh`: 171 tests; ocho páginas de familias generadas; pruebas de escritorio y móvil. Sin llamadas nuevas de voz ni modelos reales.
- **Decisiones:** no se completa al hacer scroll; no se muestra una nota conjunta sin `all_moves`; pagar parte de la deuda no la dibuja resuelta; empezar en el día 3 no significa terminar.
- **Bloqueos:** aprobación visual de Raúl y prueba en iPhone real pendientes. Rama solo local, sin issue/PR hasta autorizar publicación.
- **Para Samuel y David:** se conserva vuestra base; solo escena y pruebas. Sin cambios de contrato, backend ni narraciones. La vista previa usa voz mock.
- **Siguiente:** revisión de Raúl; con su aprobación, issue/PR e integración. Después, revisión de experiencia frente a toda la rúbrica.

## 2026-11-13 — docs/raul-common-ground — Codex (Astra y Sol 6.1)
- **Hecho:** propuesta R1 en `idea-raul.md` y resumen en mi sección de `ideas.md`; issue #11.
- **Estado:** solo documentación; no se ha ejecutado `./check.sh` ni se propone merge sin verificarlo.
- **Decisiones:** Common Ground — A plan you can interrupt: una duda transforma la explicación visual del plan; paso individual o compartido y seguimiento según el obstáculo.
- **Bloqueos:** Git y conector devuelven 404; publicado desde la sesión autenticada de Edge.
- **Para Samuel y David:** propuesta para comparar con casa y árbol; incluye demo, alcance, reparto tentativo, riesgos y condiciones de los escenarios. Pendiente de elección conjunta.
- **Siguiente:** comentar y acordar la idea final. Implementación pendiente de esa decisión.
