# Visitas — David (voz: `voice.py`)

<!-- Añade tu entrada más reciente justo debajo de esta línea. Plantilla en visitas/README.md -->
<!-- Las entradas del 12 nov vienen tal cual de `comunicacion.md`, sustituido por esta carpeta. -->

## 2026-11-12 (tarde) · David (`daviid-sc`) · Ya no hace falta permiso de Samuel para subir

- **PR #3 (`check.sh` en Windows) fusionado en `main`.** `./check.sh` funciona en Windows tal cual.
- `CLAUDE.md` (rama `docs/equal-team-push`): se quita "No hacer push sin permiso de Samuel".
  Acordado por los tres: **trabajamos de igual a igual**. Cada uno sube sus ramas y fusiona sus
  PRs cuando `./check.sh` pasa. Sigue prohibido el push directo o force-push a `main`, y los
  cambios en archivos de otro o en el contrato se avisan antes y se anotan aquí.
- `02-DOCS/ftd/voz-edge-tts.md`: actualizada (ya no espera el OK de Samuel; `check.sh` OK en Windows).

## 2026-11-12 (tarde) · David (`daviid-sc`) · Arreglo de `check.sh` en Windows

- **PR #1 (voz) y PR #2 (este archivo) ya están fusionados en `main`.** Tras `git pull`:
  `pip install -r requirements.txt` (añade `edge-tts` y `python-dotenv`).
- Rama `fix/windows-check` (PR #3). Toca dos archivos compartidos (no son de voz), con el OK de
  David; **en Linux/macOS no cambia nada**:
  - `check.sh`: en Windows (Git Bash) usa `;` como separador de `PYTHONPATH`, porque el Python
    de Windows no entiende `:`. Antes fallaba con `No module named 'finagent'`.
  - `tests/test_pipeline.py`: las 4 lecturas con `read_text()` ahora llevan `encoding="utf-8"`.
    En Windows la codificación por defecto es cp1252 y rompía textos con tildes ("Pérez").
- Resultado: **`./check.sh` funciona tal cual en Windows** (Git Bash), sin `PYTHONUTF8=1`.
  Comprobado: 4 tests pasan y `OK -> out/index.html`.
- Consejo para todos: al leer o escribir archivos de texto en Python, poner siempre
  `encoding="utf-8"`; si no, funciona en Linux y falla en Windows (Raúl y David).

## 2026-11-12 · David (`daviid-sc`) · Voz

### PR #1 — `feat/voice-edge-tts`: voz real con edge-tts
https://github.com/Inmortal112/finagent-sherpas/pull/1

- `src/finagent/voice.py`: sustituye el mock por TTS real con **edge-tts** (voces neuronales de
  Microsoft, gratis, sin clave). Genera un MP3 por escena en `out/audio/` y rellena `audio_path`
  (relativo a `out_dir`) y `duration_s` (medida del archivo). **No toca `narration`** y la firma
  `synthesize(presentation, out_dir) -> Presentation` no cambia.
- Si la síntesis falla (sin internet, etc.), usa duraciones estimadas: `main` nunca se rompe.
- Voz según `Presentation.language`: `en` → `en-US-EmmaMultilingualNeural`, `es` →
  `es-ES-ElviraNeural`. Como el producto va en inglés, **brain debe generar `language="en"`**.
- **Afecta a todos:**
  - `requirements.txt`: añade `edge-tts` y `python-dotenv`. Tras fusionar:
    `pip install -r requirements.txt`.
  - `.env.example`: se mantiene el bloque de Samuel (`MCP_URL`, `MCP_TOKEN`, `LLM_PROXY_URL`,
    `TEAM_KEY`) y se añaden `VOICE_ENGINE` y `VOICE_NAME` (opcionales). Hubo conflicto con
    `main` y ya está resuelto (merge de `main` en la rama).
- Comprobado: 4 tests pasan y `python -m finagent.run` genera `out/index.html`.

### Plan de la voz (próximos pasos)
1. **Normalización en inglés**: preparar el texto para que cifras y monedas se lean bien
   (p. ej. `$550,000` → "five hundred fifty thousand dollars"). Sin cambiar ninguna cifra.
2. **ElevenLabs para la demo** vía el proxy (`eleven-flash-v2.5`, $0.04/1000 caracteres).
   **Tope de ElevenLabs: $1,40 para todo el equipo** → en desarrollo se usa edge-tts (gratis) y
   ElevenLabs solo para generar el audio final. Por favor, que nadie lo gaste en pruebas.
3. Pausas, ritmo y elección final de voz.

### Avisos para el equipo
- **El repo es privado**, pero el brief de Sherpas pide que sea **público** para que mentores y
  jurado puedan abrirlo. Hay que decidirlo los tres antes de la entrega (18/11, 23:59).
  Los casos ya son públicos en el repo de Sherpas, así que no hay datos secretos en `cases/`.
- `fixtures/diagnostic_sample.json` sigue siendo el inventado; ya están los casos reales en `cases/`.
- ~~`check.sh` no funciona en Windows~~ → arreglado en PR #3 (ver entrada de arriba).
- ~~`CLAUDE.md` del repo dice "No hacer push sin permiso de Samuel"~~ → cambiado (ver entrada de arriba).
- Propuesta: añadir a `AGENTS.md` una línea tipo "Leer `comunicacion.md` al empezar" para que
  todas las IA lo carguen solas. No la he añadido: `AGENTS.md` es compartido.
