---
created: 2026-11-14
status: done
branch: docs/mode-choice-on-open
---
# El modo se elige al abrir (sin modo por defecto)

## Intención
Los documentos de idea decían dos cosas distintas sobre el arranque: «modo sencillo por defecto» (`ideas.md`,
`idea-david.md`) y «cada persona elige su modo al abrir» (`nota-idea.md`, la nota enviada al jurado). Samuel fija la
segunda: al abrir, una pantalla con dos botones (sencillo o completo) y nada empieza hasta elegir.

## Alcance
- Entra: `ideas.md` (cabecera, D1 punto 3, «Idea elegida») e `idea-david.md` (actualización del 13 nov, sección 2,
  y «Para todos los públicos» de la idea original); la entrada de `visitas/samuel.md` va en el PR de `feat/brain-real-cases`.
- NO entra: `nota-idea.md` (ya decía «elige»); `visitas/david.md` (solo lo escribe David; sus entradas del 13 nov
  siguen diciendo «por defecto» como registro histórico); `ideas.md` línea 60, «Deslizar (por defecto)», que es otra
  cosa (las tres formas de ver S1, idea ya sustituida); código.

## Checklist
- [x] Ningún documento de idea dice «sencillo por defecto» → `grep`.
- [x] `./check.sh` pasa.

## Evidencia
- `grep -rnE "sencillo por defecto|Guiado por defecto|sencillo \(por defecto\)" --include='*.md' .` → solo
  `visitas/david.md` (fuera de alcance).
- `./check.sh` → `4 passed`, `OK -> out/index.html`.

## Siguiente
Fusionar el PR y avisar a David y Raúl para que hagan `git pull`.
