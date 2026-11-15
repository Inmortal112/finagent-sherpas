---
created: 2026-11-15
status: in-progress
branch: feat/brain-narration-fast-model (PR #31)
---
# Documento de escalabilidad: más contexto para el modelo

- Dueño: Samuel (`Inmortal112`)

## Intención
Samuel quiere dejar escrita en el repo la idea de que el producto crece dando más contexto al modelo, y marcar
como forma elegida el **resumen del historial**. Sirve al equipo para decidir el siguiente paso de `/ask` y al
pitch para contestar «¿cómo crece esto?».

## Alcance
- Entra: `escalabilidad.md` en la raíz (junto a `ideas.md` y `nota-idea.md`), esta ficha y la entrada en
  `visitas/samuel.md`.
- NO entra: construirlo. No se toca `ask.py`, `sessions.py`, `server.py` ni el contrato. Tampoco la traducción
  al inglés (solo si el documento entra en la entrega).

## Decisiones
- **En español:** es un documento entre nosotros, como `ideas.md` (regla 9).
- **Resumen sin cifras:** así `guard` no tiene que cambiar; las cifras siguen saliendo solo de los hechos.
- **Dos niveles (con código primero, con el modelo después):** el de código es gratis y determinista y reutiliza
  `sessions.advisor_note`. Es una recomendación de Claude; Samuel eligió la forma, no el nivel.

## Checklist
- [x] `escalabilidad.md` creado con la forma elegida, cómo funcionaría, reglas, riesgos y comprobación.
- [x] Lo que dice del código actual es cierto → comprobado leyendo el código (ver Evidencia).
- [x] `./check.sh` pasa (no se ha tocado código): `110 passed`, `OK -> out/index.html`.
- [ ] David y Raúl lo han leído.

## Evidencia (2026-11-15, sobre `c8581fa`)
- `ask.answer(presentation, diagnostic, question)` (`ask.py:74`) y `messages=[system, user]` (`ask.py:117`): la
  llamada no recibe turnos anteriores. `server.py:83` la llama solo con la pregunta.
- `sessions.py` guarda `turns` y `decision` por sesión; `advisor_note` devuelve partes, preguntas y lo que el plan
  no cubre. Solo lo leen `/history` y `/advisor-note`.
- Tiempos y modelos citados (2,6-4,0 s, `deepseek-flash`): de `02-DOCS/ftd/brain-ask.md`.
- Coste del nivel B: estimado con los precios de `BRIEF.md` ($0,30 / $1,20 por millón), unos 500 tokens de
  entrada y 100 de salida. **No medido.**
- `./check.sh` → `110 passed`, `OK -> out/index.html` (15 nov, sobre `c8581fa`).

## Siguiente
Samuel decide si se construye antes de la congelación (18 nov, 18:00). Si sí: issue, rama `feat/brain-ask-summary`
y nivel A primero.
