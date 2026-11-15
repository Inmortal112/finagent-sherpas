---
created: 2026-11-16
status: done
branch: feat/stage-family-worries
---
# Las preocupaciones sugeridas salen del plan de cada familia

## Intención
Bajo «What worries you most about money?» había cuatro botones iguales para todas las familias. Ahora cada
familia ve tres, sacados de las «Objective concerns» de su `persona.md`, en sus palabras. Se siente hecho para
ellos (criterio «Personal») sin atribuirles nada que no dijeron.

## Alcance
- Entra: tabla `house.WORRIES` (caso → concern de `persona.md` y su frase), `visual.data.worries` en `intro`,
  y la página los dibuja (si no hay, los cuatro genéricos de antes).
- No entra: un campo para que el asesor escriba la preocupación (descartado por ahora); leer `persona.md` en
  tiempo de ejecución; el contrato (no cambia).
- Decisión: las «Subjective concerns» de las cuatro familias están vacías («none recorded»), así que no se
  presenta nada como «lo que dijo la familia». Son sugerencias; la familia elige una o escribe la suya.
- Decisión: frases escritas a mano y sin cifras; un test comprueba que cada una apunta a un concern que existe
  en el `persona.md` de esa familia.

## Checklist
- [x] `house.worries` y `intro.visual.data.worries` para las cuatro familias. → test nuevo en `test_house.py`
- [x] La página muestra los botones de la familia. → navegador, Samantha, Michael y los Weah
- [x] Caben en un móvil (375 px). → el botón más largo acaba en 320 px, la caja en 336
- [x] Cada botón lleva a la parte correcta de la casa con el modelo real. → 12 de 12
- [ ] Una persona lo ha visto en un móvil real.

## Evidencia
- `./check.sh` → `167 passed`, `OK -> out/index.html`.
- `finagent.run --all` → 8 páginas, 105 mp3. Consola del navegador sin errores.
- `/worry` con el modelo real, las 12 frases: todas `source: model` y la parte esperada (p. ej. «Will my savings
  last?» → `timeline`/garden; «Our credit card» → `pillar_debt`/walls; «Being covered if something happens to
  me» → roof; «Having enough set aside for an emergency» → foundations).
- **Visto, sin arreglar:** una respuesta de Michael dice «six years before the plan ends at 91» (91 − 85, una
  cuenta hecha por el modelo y escrita en letras: `guard` solo rechaza de «twenty» en adelante).

## Siguiente
Decidir si `guard` debe rechazar también los números pequeños en letras cuando van con «years» o «months».
