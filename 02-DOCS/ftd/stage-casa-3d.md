# FTD — La casa en 3D (opción intermedia)

- Fecha: 2026-11-15 · Rama: `docs/stage-house-3d-plan` (solo este plan; el código irá en ramas `feat/stage-house-3d-*`)
- Decide: David, tras la decisión del equipo de hacer la casa en 3D. Etapa de Raúl (escena).
- Estado: **plan aprobado por David, sin código todavía.**

## Intención

Que la casa se vea en 3D y que **la cámara cuente la historia**: al hacer scroll se desliza de una parte a la
siguiente, y cuando la familia pregunta, la casa gira hacia la parte de la que se habla. Todo lo demás de la
página (scroll por partes y años, narración, chat `/ask`, pasos, vuelta del día 3, ficha del asesor) se queda
como está.

## De dónde sale

Un vídeo de referencia (una web de lujo, fuera del repo) visto en fotogramas. Lo que enseña: el scroll mueve la
cámara, una sola idea por pantalla, un único plano continuo sin cortes. Casi seguro que son vídeos ya hechos que
el scroll hace avanzar, no 3D calculado en directo: eso no nos sirve, porque nuestra casa cambia con los datos
de cada familia. **Tomamos la idea y la técnica, no su código ni su diseño.**

## Opciones comparadas

| Opción | Qué es | Por qué sí o no |
|---|---|---|
| A | El 3D sustituye solo el dibujo; cámara quieta | Descartada: casi todo el coste técnico y se ve casi igual que la 2D |
| **Intermedia** | Casa 3D + cámara que se mueve al cambiar de parte | **Elegida**: el 3D se nota y no se rehace nada de lo que funciona |
| B | Rehacer la página entera como el vídeo | Descartada: no cabe antes de la congelación y pone en riesgo lo probado en iPhone |

## Condiciones (valen para todo el trabajo)

- **La casa 2D se queda como respaldo.** Se usa si no hay WebGL (lo que permite al navegador usar la tarjeta
  gráfica), si la carga falla, si el móvil pide «reducir movimiento», si va a tirones, y **siempre en el modo
  sencillo («Simply»)**. El SVG de `stage_page.html` no se toca.
- **three.js dentro del repo**, no cargado de internet: la demo no puede depender de la red.
- **Detrás de un interruptor: `?house=3d`.** La página por defecto no cambia hasta probarlo en el iPhone de David.
- **Punto de decisión: 17 nov a las 14:00.** Si no va bien en el móvil, nos quedamos en 2D y el 3D sigue
  detrás del interruptor (no cuesta nada dejarlo).
- Congelación del código: 18 nov a las 18:00.

## Alcance

Dentro:
- Casa hecha con formas simples y colores planos (cajas, prisma del tejado, cilindros de las tuberías, esferas
  del árbol): diseño propio, carga rápida.
- Las mismas cuatro cosas que hace hoy `paint()`: los estados `solid / cracked / broken / repaired` de las 5
  partes (`roof`, `walls`, `plumbing`, `foundations`, `garden`), resaltar una parte y atenuar las demás, el
  jardín que se seca con los años (`lush`) y el brillo de lo reparado.
- Cámara que se desliza a cada parte con el scroll y con `turnHome()`, en movimientos cortos y lentos.

Fuera (recortado para llegar a tiempo):
- Modelos descargados, texturas, interior, sombras realistas y efectos de postproceso.
- Girar la casa con el dedo: en el móvil se pelea con el scroll.
- Una casa distinta por familia en 3D (como mucho, un color).
- ~~Etiquetas flotantes sobre cada parte~~: al final sí hay una marca por parte, porque en el móvil la leyenda está oculta
  y sin ella no se distinguía «agrietado» de «roto».
- Gotas que caen de las tuberías: en 3D están quietas (animarlas obliga a dibujar sin parar; se verá con la cámara).
- **Intro bajando desde las nubes: aparcada.** Solo cuando todo lo demás esté acabado, y preguntando antes a David.

## Archivos

| Archivo | Cambio |
|---|---|
| `src/finagent/web/vendor/three.module.min.js` | Nuevo. three.js 0.170.0 del paquete oficial de npm (un solo archivo, 692 KB; licencia MIT en `three.LICENSE`) |
| `src/finagent/web/house3d.js` | Nuevo. La casa 3D, aparte para no engordar `stage_page.html` |
| `src/finagent/server.py` | Una línea: sirve `src/finagent/web/` en `/web` (así no hay que copiar nada a cada carpeta de `out/`) |
| `src/finagent/stage_page.html` | Unas 35 líneas: con `?house=3d` carga `/web/house3d.js`; al final de `paint()` le pasa estados, foco y `lush` |

`?house=3d` se recuerda mientras la pestaña siga abierta (para que sobreviva al cambiar de familia); `?house=2d` lo apaga.

Abierta como archivo suelto (sin servidor), la página cae a 2D: el navegador no deja cargar módulos así.

## Orden: PRs pequeños

1. **Hecho (15 nov, `feat/stage-house-3d-switch`):** three.js en el repo, interruptor y casa 3D quieta con las 5 partes.
   Falta la primera prueba en iPhone.
2. **Hecho (15 nov, `feat/stage-house-3d-states`):** los cuatro estados, el brillo, el jardín y atenuar las partes sin foco.
   Además: una marca redonda por parte (✓ ! ✕, con los colores de la leyenda) y tocar una parte lleva a su capítulo.
3. **17 nov, mañana:** la cámara (scroll y `turnHome`).
4. **Solo si la decisión del 17 a las 14:00 es «sí»:** 3D por defecto en el modo completo.

Cada PR: `bash check.sh` en verde, **consola del navegador revisada** (los tests no ejecutan el JavaScript de la
página) y entrada en `visitas/david.md` con línea «Para Raúl».

## Qué se prueba en el iPhone

- [ ] Carga en un par de segundos por el túnel.
- [ ] El scroll va fluido.
- [ ] La casa y la hoja del chat caben a la vez.
- [ ] Al preguntar, la casa gira hacia la parte.
- [ ] Sigue funcionando al volver de otra app.
- [ ] Alguien que no la ha visto distingue «agrietado» de «roto».

## Riesgos

- **Legibilidad:** las grietas se leen peor en 3D que dibujadas. Por eso se mantiene la leyenda.
- **Gente mayor:** el movimiento puede marear. Por eso el modo sencillo es 2D y la cámara se mueve poco.
- **Móvil:** el lienzo 3D comparte pantalla con la hoja del chat; batería (se dibuja solo cuando algo cambia).
- **Tiempo:** son 1,5–2 jornadas (estimación) de las 2,5 que quedan. Siguen pendientes el micro en iPhone, el audio
  de ElevenLabs, el vídeo y el README. Si no caben, el 3D se queda detrás del interruptor.

## Pendiente de decidir

- Quién lo programa (por defecto, David con Claude Code). **Raúl, Samuel: si alguno ya está tocando la casa o
  `stage_page.html`, decidlo en vuestro archivo de `visitas/` antes del 16 por la mañana.**
