---
created: 2026-11-15
status: done
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
- [x] 1. `finagent.run --all` genera `out/families/<familia>/<modo>/` (página + audio) → listar carpetas, mp3 > 0.
- [x] 2. La página cambia de familia y de modo navegando a esas carpetas; conserva sesión → navegador.
- [x] 3. Modo simple: letra grande, menos datos → captura.
- [x] 4. Persona en parejas (se envía `person` a `/ask`) → respuesta por su nombre.
- [x] 5. «What worries you?» antes del recorrido (`/worry`) → la casa gira a esa parte.
- [x] 6. El chat recupera el historial al recargar (`/history`) → recargar y ver las respuestas.
- [x] 7. Volver a los 3 días (`/reminders?today=`, `/follow-up`) → la parte queda reparada.
- [x] 8. Nota del asesor (`/advisor-note`) en un panel → captura.
- [x] 9. `STAGE.md` en inglés, entrada en `visitas/samuel.md`, `verify`, servidor arrancado para Samuel.

## Evidencia
- 1: `finagent.run --all` (Edge, 2 min) → 8 páginas en `out/families/<familia>/<modo>/`, 92 mp3, ninguno vacío.
- 2-8, Chromium sin ventana contra el servidor real (:8010), Weah, sin errores de consola:
  - cambiar de familia lleva a `/families/timothy-melanie-weah/complete/`, nota 60, suena `audio/intro.mp3`;
  - «I am Melanie» + preocupación («…if one of us dies») → «Melanie, you both hold life cover, but the plan shows a
    gap…» y la casa gira al tejado; pregunta → «Melanie, you hold $110,000 of life insurance…»;
  - elegir «Add life cover» → «Come back three days from now» → «Have you been able to start it?» → «Yes» →
    «Your roof is repaired», tejado en `repaired`; nota del asesor con preocupación, pregunta, paso y seguimiento;
  - recargar: 5 mensajes recuperados, paso elegido, tejado reparado, persona Melanie;
  - «Simply» lleva a `/simple/`, `body.simple`, letra grande y menos datos.
- `./check.sh` → 152 passed (2 tests nuevos de la escena).
- 9: `STAGE.md` escrito y enlazado en el README. Servidor en :8001 → `/healthz` ok, página de Samantha, página
  sencilla de Weah 200, `intro.mp3` de Michael 200 (92 KB). El :8000 lo ocupa un servidor viejo (pid 398275) que
  sirve el mock antiguo y que no se me permitió parar.
- Sin comprobar: micrófono, iPhone real, cómo suena la voz Edge de punta a punta, modo sencillo en móvil.
- Visto y no tocado (es del cerebro): en modo sencillo algunas escenas de Weah usan la frase de plantilla
  («Your walls are cracked. Debt score 12 out of 20 points.»), no un texto propio.

## Siguiente
Samuel la prueba en http://localhost:8001 (servidor arrancado desde este worktree) y para el servidor viejo del 8000. La otra sesión une y sube la rama.
