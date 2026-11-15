---
created: 2026-11-15
status: in-progress
branch: feat/stage-house-journey
---
# Stage: la experiencia completa en la página (para que Samuel la pruebe al volver)

## Intención
La casa interactiva ya funciona (`stage-casa-interactiva.md`). Falta que la página use todo lo que el backend ya
ofrece, para que la demo se pueda recorrer entera: voz en las cuatro familias, modo simple/completo, persona en
una pareja, la preocupación antes del recorrido, la vuelta a los 3 días y la nota del asesor.

## Alcance
- Entra: `run.py --all` (las cuatro familias en los dos modos, con voz Edge, gratis), `stage_page.html`, `STAGE.md`.
- NO entra: tocar `ask.py`, `sessions.py`, `server.py` (son de la otra sesión), ElevenLabs, 3D, push sin permiso.
- Samuel se ha ido y quiere algo tangible al volver. **No hay permiso explícito de push**: todo queda en commits
  locales en `.worktrees/stage-house-journey` y con un servidor arrancado.

## Checklist (en este orden; un commit por punto)
- [ ] 1. `finagent.run --all` genera `out/families/<familia>/<modo>/` (página + audio) → listar carpetas, mp3 > 0.
- [ ] 2. La página cambia de familia y de modo navegando a esas carpetas; conserva sesión → navegador.
- [ ] 3. Modo simple: letra grande, menos datos → captura.
- [ ] 4. Persona en parejas (se envía `person` a `/ask`) → respuesta por su nombre.
- [ ] 5. «What worries you?» antes del recorrido (`/worry`) → la casa gira a esa parte.
- [ ] 6. El chat recupera el historial al recargar (`/history`) → recargar y ver las respuestas.
- [ ] 7. Volver a los 3 días (`/reminders?today=`, `/follow-up`) → la parte queda reparada.
- [ ] 8. Nota del asesor (`/advisor-note`) en un panel → captura.
- [ ] 9. `STAGE.md` en inglés, entrada en `visitas/samuel.md`, `verify`, servidor arrancado para Samuel.

## Evidencia
(se rellena punto a punto)

## Siguiente
Punto 1: `run.py --all`.
