---
created: 2026-11-16
status: done
branch: feat/stage-house-heals
---
# La casa mejora cuando la familia hace las cosas bien (y el 3D, al estilo del vídeo)

## Intención

Otro equipo también hace una casa. Lo que nos distingue: **la casa reacciona a lo que hace la familia**. Cada paso
que marca como hecho repara su parte con una animación, la puntuación sube en directo y el cielo pasa de gris y
lluvioso a un atardecer dorado. Además, en 3D, la página toma el lenguaje del vídeo de referencia (web cinematográfica
de TikTok, 16 nov): cielo a pantalla completa, la cámara baja desde las nubes hasta la casa al hacer scroll y las
tarjetas flotan sobre la escena.

## Decisiones

- **Avanzar es hacer.** En el capítulo del paso N cuentan como hechos los pasos anteriores (1…N−1), más los que la
  familia marque con «I've done this»; el paso N se repara al pulsarlo o al pasar al siguiente. El capítulo final
  cuenta todos. Así la puntuación sube mientras se baja por la página (Samuel, 16 nov: «el score no va variando»,
  porque en la primera versión solo subía con el botón).
- **Ninguna cifra inventada.** La puntuación alcanzada es la mayor cifra de Sherpas para lo que han hecho: la de cada
  paso por separado (`score_after`) o la de todos juntos (`all_moves`) si los han hecho todos. Sherpas no puntúa
  combinaciones parciales, así que no se suman ni se calculan, y la cifra nunca baja (Michael: 26 → 31 → 62). En una
  familia sin `all_moves` (Michael, Samantha), el capítulo final muestra la mejor cifra de un paso suelto.
- **Casa moderna (Samuel, 16 nov, con una imagen de referencia de casa minimalista isométrica):** volúmenes blancos,
  planta alta en voladizo, cubiertas planas oscuras, ventanales con perfil negro, zócalo blanco con césped, árboles
  redondos y piscina. Partes: tejado = cubiertas; paredes = volúmenes y cristales (rotos si «broken»); fontanería =
  piscina (agua baja si «cracked», vacía y con charco si «broken»); cimientos = zócalo; jardín = césped y árboles.
- **Más movimiento:** cámara que orbita despacio y sigue al ratón, árboles que se mecen (más con lluvia), marcas que
  flotan, agua que brilla, pájaros con buen tiempo, onda de luz al reparar, portada que aparece y tarjetas que entran.
- **El «Yes, I started» del día 3 cuenta como paso hecho**: también sube la puntuación.
- **Lo hecho se guarda en el navegador** (`localStorage`, por familia), con «Start again» para la demo. No toca el
  backend ni el contrato.
- **Cielo según la puntuación**: 25 o menos, gris con lluvia; ~55, día claro; 85 o más, atardecer dorado.
- **Sigue detrás de `?house=3d`** (decisión del equipo el 17 a las 14:00). Lo de marcar pasos y la puntuación en
  directo funciona también en 2D.

## Alcance

Dentro:
- `stage_page.html`: botón por paso, puntuación alcanzada, animación de la cifra, «Start again», maquetación a pantalla
  completa cuando hay 3D (escritorio: fondo; móvil: la mitad de arriba).
- `web/house3d.js`: cielo, sol, nubes, lluvia, sombras, ventanas encendidas, reparación animada (grietas que se cierran
  y chispas), intro desde las nubes guiada por el scroll y casa centrada en el hueco de la escena.

Fuera: modelos o texturas descargados, posprocesado, cambios en el backend o el contrato, 3D en el modo «Simply».

## Checklist

- [x] Marcar un paso repara su parte y sube la puntuación (2D y 3D) — navegador sin interfaz
- [x] La puntuación nunca muestra una cifra que no esté en los hechos — `achieved()`: base, `score_after` de un paso o `all_moves`
- [x] El cielo cambia con la puntuación (Michael 26 → 62 con el paso 2) — captura
- [x] Intro desde las nubes con el scroll del inicio — capturas (hero, mitad de bajada, casa)
- [x] Móvil (390 px): la casa arriba, las tarjetas debajo, sin solaparse — captura
- [x] Consola del navegador sin errores — headless, 3 familias
- [x] `./check.sh` pasa
- [ ] Probarlo en un iPhone de verdad (rendimiento con cielo, nubes y sombras) — sin hacer

## Evidencia

Chromium 1248 sin interfaz con WebGL por software (SwiftShader), servidor del worktree en `:8010`.
Las capturas en 3D se hicieron con un reloj de 60 fps simulado: con WebGL por software el vigilante de rendimiento
abandona el 3D y vuelve a la casa dibujada, que es lo previsto en un equipo sin tarjeta gráfica.

- Michael, 3D, paso 2: puntuación 26 → 62 (+36), fontanería ✕ → ✓ con chispas, lluvia → día claro. Sin errores.
- Samantha, 3D: atardecer dorado desde el inicio (82); paso 1 → 84.
- Weah, móvil 390×844: paso 1 → 62; capítulo final → 78 (`all_moves`, +18). Sin errores.
- Weah, 2D: tres pasos → 78 y paredes y tejado reparados; se conserva al recargar; «Start again» → 60 y paredes agrietadas.
- `./check.sh` → `167 passed`, pipeline OK.
- Segunda versión (casa moderna + avanzar es hacer): scroll por los pasos → Michael 26 → 31 → 62; Johnson 52 → 57 → 57,
  final 60 (`all_moves`); botón en el paso 2 de Michael: 31 → 62. 2D: igual que antes. Sin errores en consola (Michael,
  Samantha en móvil, Johnson). `./check.sh` → `167 passed`.
- Verificación (sobre 5729f4d + cambios sin commit): `./check.sh` 167 passed; `node --check` de `house3d.js` y del
  script de la página: OK; `/healthz` 200. **HERRAMIENTA-AUSENTE:** ruff no instalado. **SUSTITUIDA:** el JavaScript no
  tiene tests; se probó con Chromium sin interfaz, que no mide el rendimiento real de un móvil. Veredicto: PASA, con
  el iPhone pendiente.

## Siguiente

Probarlo en el iPhone de David antes de la decisión del 17 nov a las 14:00.
