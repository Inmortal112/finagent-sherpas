---
created: 2026-11-15
status: done
branch: feat/brain-family-experience (worktree `.worktrees/family-experience`: hay otra sesión en `main`)
---
# Backend: voz real, por persona, dos modos, preocupación, avisos, chat que se escribe y URL pública

- Dueño: Samuel (`Inmortal112`)

## Intención
Cerrar lo que la nota de idea promete y el backend aún no hace (puntos 1, 4, 5, 6, 7 y 8 de la lista de pendientes),
y añadir lo que pidió Samuel: que la respuesta se vaya escribiendo poco a poco en un chat, para leerla mientras
suena y releerla después.

## Alcance
- Entra:
  1. Pregunta por voz probada con audio real (webm/Opus) contra el servidor real.
  4. Despliegue: el servidor escucha en la red, `Dockerfile`, y un enlace público temporal (`scripts/share.sh`).
  5. Hechos por persona en las parejas (escena `person_<nombre>`), y `/ask` sabe quién pregunta.
  6. Modo `simple` y modo `complete`: narración y respuestas.
  7. «¿Qué te preocupa?» al empezar (`POST /worry`), guardado para el asesor.
  8. Avisos: día 3 tras elegir un paso y fechas del plan (`GET /reminders`, con `today` para simular el paso del tiempo).
  +. `POST /ask/stream`: la respuesta llega palabra a palabra; página de chat en `/chat`.
  +. Tope de preguntas por sesión y por minuto (necesario si hay enlace público).
- NO entra: la página del producto (Raúl); cuentas de usuario; envío real de avisos (correo, SMS); alojamiento
  permanente (necesita una cuenta en un proveedor); resumen del historial como contexto (ver `escalabilidad.md`);
  audio de la narración de las cuatro familias (punto 2); el contrato `Presentation` (no cambia).

## Decisiones
- **El texto que se escribe poco a poco es el ya aprobado por `guard`.** No se envían al chat las palabras del modelo
  según salen: una cifra inventada se vería antes de poder pararla. Primero se obtiene la respuesta entera (2-4 s),
  `guard` la revisa y después se envía palabra a palabra.
- **Por persona solo en parejas** (Weah, Johnson): con un solo adulto, su parte es toda la casa.
- **Modo sin cambiar el contrato:** `brain.build(diagnostic, language, mode)`; el modo sencillo es otra narración
  guardada (`simple` en `narrations/<familia>.json`), más corta y con una cifra como mucho.
- **Avisos sin modelo:** frases fijas con el nombre del paso y las fechas de `goals.chartGoals`, escritas como mes y
  año (regla del caso). No se envía nada: la página pregunta qué toca hoy.
- **Enlace público temporal** por túnel SSH (sin instalar nada): vive mientras el ordenador esté encendido.

## Checklist
- [x] 1 · Pregunta hablada real → transcrita y respondida (con el modelo de respaldo; ver «Añadido después»).
- [x] 4 (parte) · Servidor accesible por la red local; `scripts/serve.sh`, `scripts/share.sh` y `Dockerfile` escritos.
- [ ] 4 (parte) · Enlace público abierto y `Dockerfile` construido. **Sin hacer:** ver Evidencia.
- [x] 5 · Escena por persona en Weah y Johnson; `/ask` con `person` → tests y prueba real.
- [x] 6 · Narración sencilla guardada para las cuatro familias y aceptada por `guard`; `/ask` con `mode` → tests y prueba real.
- [x] 7 · `/worry` guarda la preocupación y aparece en la ficha del asesor → test y prueba real.
- [x] 8 · `/reminders` da el aviso del día 3 y las fechas del plan; `/follow-up` → tests y prueba real.
- [x] + · `/ask/stream` envía la respuesta en trozos y el turno queda en el historial → test y prueba real.
- [x] + · Topes de uso → test.
- [x] `./check.sh` pasa sin llamar al modelo.

## Evidencia (2026-11-15)
- `./check.sh` → `126 passed` (antes 110) y `OK -> out/index.html`.
- Narración: `python -m finagent.narrator … --missing` → 2 escenas por persona en Weah y en Johnson; `--all --simple`
  → 13, 10, 10 y 13 escenas, `template kept for []`. Corregida a mano una frase de Melanie (decía «leave you and the
  children» donde era Timothy).
- Servidor real (puerto 8010, desde el worktree):
  - `/ask/stream`, Weah, `person=Melanie`, `mode=simple`, «Is my life insurance enough?» → `thinking` a 0,0 s,
    `turn` a 4,4 s (`person_melanie`), 16 `delta` cada 0,09 s, `done` a 5,9 s: «Melanie, no. Your plan recommends at
    least $600,000 of life cover, so you have a shortfall.»
  - `/worry` (Timothy, «…pay for the kids college») → `plumbing`; `/ask` «How much do I owe on my card?» →
    `person_timothy`: «Timothy, you owe $18,000 on your Chase card, and it carries an 18% rate…».
  - `/decision move_1` → `/reminders?today=` (tres días después) → «A few days ago you chose a first step: Pay down
    revolving card…» y «…coming up in January 2027: Go on vacation»; `/follow-up done` → `repaired_house_part: walls`;
    `/advisor-note` con preocupación, pregunta, decisión y seguimiento.
  - `/presentation/samantha-lewis?mode=simple`, línea del tiempo: 2 frases frente a 3 largas del modo completo.
  - `curl http://192.168.1.189:8010/healthz` → 200: escucha en la red local.
- **Punto 1, no conseguido.** Grabación real en webm/Opus (pregunta sintetizada con edge-tts y convertida con ffmpeg)
  enviada a `/ask` → 422 «I could not hear the question…» en 0,4 s. Causa: el proxy de Sherpas devuelve 401 en
  `/v1/audio/transcriptions` (`scribe-v2`) **y** en `/v1/audio/speech` (`eleven-flash-v2.5`): «ElevenlabsException…
  Invalid API key». Es la clave de ElevenLabs del propio proxy, no la nuestra. En esta máquina no hay
  `ELEVENLABS_API_KEY` personal (la tiene David). Lo que sí queda probado: la subida del archivo llega a la
  transcripción y, si falla, la página recibe el mensaje para escribir la pregunta.
- **Punto 4, a medias.** No se ha abierto el enlace público: el túnel SSH lo bloqueó el modo automático de Claude
  Code (hay que lanzarlo a mano: `scripts/share.sh`). El `Dockerfile` no se ha construido: no hay Docker en esta máquina.
- La página `/chat`: el servidor la sirve (200) y su JavaScript pasa `node --check`. **No probada en un navegador.**
- Gasto (`/key/info`): $0.31 de $50.
- **verify (15 nov, sobre `3002269` + cambios sin commit):** `./check.sh` → `126 passed`, `OK`; `compileall src
  contracts tests` → sin errores. `ruff` y `mypy`: HERRAMIENTA-AUSENTE. Veredicto: PASA para lo marcado; 1 y parte del 4, pendientes.

## Añadido después (15 nov, rama `feat/voice-stt-fallback`): punto 1 conseguido
- `voice_stt_model.py`: si Scribe falla, transcribe `gemini-3.5-flash-lite` por el proxy (acepta el webm del
  navegador tal cual). `voice.transcribe_async` lo usa de respaldo; sin `TEAM_KEY` no se intenta. Es la etapa de
  David: anotado en `visitas/samuel.md`.
- Medido antes de escribirlo: wav 2,4 s, webm 1,3 s, mp3 1,3 s, las tres «Why does my garden dry up?».
  `gpt-5-mini` y `deepseek-flash` no aceptan audio (404).
- Servidor real, grabación webm/Opus → `/ask`: `heard_from: voice`, pregunta transcrita bien, `timeline` / `garden`,
  200 en 4,9 s. → `/ask/stream` (Weah, Timothy): «How much life insurance do I have, and is it enough?» →
  `person_timothy`, 28 trozos. Silencio de 2 s → 422 «I could not hear the question…».
- `./check.sh` → `132 passed`.
- Límite: las grabaciones son voz sintetizada (edge-tts) pasada a webm con ffmpeg, no un micrófono de verdad.

## Siguiente
Samuel: lanzar `scripts/share.sh` para el enlace público, avisar a los mentores de la clave de ElevenLabs del proxy y
probar `/chat` en el navegador y en el móvil.
