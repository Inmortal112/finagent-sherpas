@AGENTS.md

## Solo para Claude Code

- Flujo: `ftd` por tarea, `verify` antes de cada commit.
- Los tres trabajamos de igual a igual (acordado por Samuel, David y Raúl el 12 nov): cada uno sube
  sus ramas y fusiona sus PRs sin pedir permiso a nadie, siempre que `./check.sh` pase. Nada de
  push directo ni force-push a `main`. Todos pueden editar cualquier archivo (regla 1 de `AGENTS.md`);
  si tocas una etapa que no es la tuya, anótalo en tu archivo de `visitas/`. Cambios en el contrato:
  avisar antes (regla 2).
- Remoto por SSH (`git@github.com:`).
- `fixtures/diagnostic_sample.json` es inventado: sustituirlo por un diagnóstico real del MCP tras el kick-off.
