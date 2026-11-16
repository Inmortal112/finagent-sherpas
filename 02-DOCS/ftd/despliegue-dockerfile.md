---
created: 2026-11-17
status: done
branch: feat/deploy-dockerfile
---
# El Dockerfile genera la web completa con voz para desplegarla en Render

## Intención
La imagen generaba una sola página con `VOICE_ENGINE=mock` (sin audio). Para el enlace del MVP en Render debe
generar las 8 páginas (4 familias × 2 modos) con la voz gratuita `edge`, igual que en local.

## Alcance
- Dentro: línea de generación del `Dockerfile` y su nota en `BACKEND.md`.
- Fuera: crear el servicio en Render (lo hace Samuel en el panel, con sus claves), voz Matilda (ElevenLabs) en la
  imagen, disco persistente para `data/sessions/`.

## Checklist
- [x] `Dockerfile`: `RUN VOICE_ENGINE=edge python -m finagent.run --all` → mismo comando en local da 8 páginas con mp3.
- [x] `BACKEND.md` explica qué genera la imagen → una línea añadida.
- [x] `./check.sh` pasa.
- [ ] `docker build` → **no comprobable aquí**: no hay Docker en esta máquina; lo comprueba el build de Render.

## Evidencia
- Simulación de la imagen: worktree **sin `.env`** (como la imagen), caché de voz vacía y `out/` borrado →
  `VOICE_ENGINE=edge python -m finagent.run --all` en 1 min 15 s: 9 `index.html` (portada + 8), 204 mp3, ninguno
  de menos de 2 KB (no cayó al mock).
- `./check.sh` → 218 passed.
- verify (sobre `0beb9b9` + cambios sin commit): `./check.sh` 218 passed. **HERRAMIENTA-AUSENTE:** ni Docker ni
  hadolint; la sintaxis del `Dockerfile` y el build real solo los comprueba Render. **SUSTITUIDA:** el build se simuló
  con el mismo comando fuera de Docker; no detecta fallos de red ni de paquetes propios de la imagen
  `python:3.13-slim`. Veredicto: PASA en local, pendiente del build de Render.

## Siguiente
Crear el Web Service en Render (runtime Docker) y poner el enlace en `SUBMISSION.md`.
