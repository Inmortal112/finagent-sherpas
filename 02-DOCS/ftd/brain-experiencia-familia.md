---
created: 2026-11-15
status: in-progress
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
- [ ] 1 · Pregunta hablada real → transcrita y respondida.
- [ ] 4 · Servidor accesible desde otro dispositivo y por un enlace público; `Dockerfile` construye.
- [ ] 5 · Escena por persona en Weah y Johnson; `/ask` con `person` → tests.
- [ ] 6 · Narración sencilla guardada para las cuatro familias y aceptada por `guard`; `/ask` con `mode` → tests.
- [ ] 7 · `/worry` guarda la preocupación y aparece en la ficha del asesor → test.
- [ ] 8 · `/reminders` da el aviso del día 3 y las fechas del plan; `/follow-up` → tests.
- [ ] + · `/ask/stream` envía la respuesta en trozos y el turno queda en el historial → test y prueba real.
- [ ] + · Topes de uso → test.
- [ ] `./check.sh` pasa sin llamar al modelo.

## Evidencia

## Siguiente
