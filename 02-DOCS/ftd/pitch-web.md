---
created: 2026-11-17
status: done
branch: feat/pitch-web
---
# Web del pitch: el recorrido completo en 2 minutos

## Intención
Una página que se proyecta durante el pitch y cuenta, sola y en 2:00 exactos, cómo funciona Under One Roof:
entrar, elegir persona, modo y forma de explicarlo, recorrer el plan como su casa, una consulta al chat, cómo
viaja esa consulta en milisegundos (teléfono → servidor → proxy de Sherpas → proveedor → guard → teléfono) con su
precio, y el score nuevo. Cierra con por qué Sherpas lo necesita.

## Alcance
- Dentro: `pitch/index.html` (estática, sin build), `pitch/data.js` generado por `scripts/build_pitch.py` desde
  `cases/` y `narrations/`. Mismo estilo que el producto (Poppins, Fragment Mono, degradado violeta-azul).
- Fuera: el producto (`stage_page.html`, servidor), el contrato, llamadas reales al modelo.

## Checklist
- [x] Ninguna cifra a mano: scores, pilares, pasos, narración y tokens salen del script → `data.js` regenerado.
- [x] Tokens de la consulta medidos con el prompt real de `ask.answer` (modelo falso, coste 0) → 4.322 a 5.235.
- [x] Precio con la tarifa del brief (`deepseek-flash`, $0,30 / $1,20 por 1M) → $0,0015 a $0,0017 por pregunta.
- [x] Tiempos por salto marcados como reparto ilustrativo del total medido (2,6 a 4,4 s) → nota al pie.
- [x] Dura 2:00 en reproducción automática → Chromium headless en tiempo real por CDP: reloj 2:00 al terminar.
- [x] Sin errores de consola (solo el 404 de `favicon.ico`) → driver CDP.
- [x] Escritorio 1440×860 y móvil 390×844 → capturas revisadas.
- [x] `./check.sh` pasa.

## Evidencia
- Capítulos: Problem 13 s · Open 15 · Walk 20 · Ask 8 · The wire 23 · Act 20 · Why 21 = 120 s.
- Michael (por defecto): 26 → 62 con «Plan to spend less from savings in retirement»; Timothy y Melanie 60 → 78 y
  Daniel y Emily 52 → 60 con la combinación de Sherpas (`combined_moves`); Samantha 82 → 84.
- Controles: espacio pausa, ← → capítulos, R reinicia, `?ch=wire` abre un capítulo. Tocar una opción en el teléfono
  cambia la familia, el modo o el estilo del resto del recorrido.

- verify (base `a8626cb`, sucio: cambios de esta rama sin commit): `./check.sh` 241 passed; `compileall` OK;
  `build_pitch.py` regenera 4 familias; servidor estático responde 200. **HERRAMIENTA-AUSENTE:** ruff no está
  instalado. **SUSTITUIDA:** no hay tests automáticos de la página; se probó con el driver CDP (no detecta fallos
  en Safari/iPhone). Veredicto: PASA.

## Siguiente
Ensayar el pitch con la página proyectada y decidir si se publica en Render junto al MVP.
