@AGENTS.md

## Solo para Claude Code

- Flujo: `ftd` por tarea, `verify` antes de cada commit.
- Los tres trabajamos de igual a igual (acordado por Samuel, David y Raúl el 12 nov): cada uno sube
  sus ramas y fusiona sus PRs sin pedir permiso a nadie, siempre que `./check.sh` pase. Nada de
  push directo ni force-push a `main`. Cambios en archivos de otro o en el contrato: avisar antes
  (regla 1 y 2 de `AGENTS.md`) y anotarlo en `comunicacion.md`.
- Remoto por SSH (`git@github.com:`).
- `fixtures/diagnostic_sample.json` es inventado: sustituirlo por un diagnóstico real del MCP tras el kick-off.
