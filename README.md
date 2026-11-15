# FinAgent — Sigma × Sherpas

Agente que presenta y narra diagnósticos financieros de Sherpas Wealth. Estado: esqueleto con mocks.

## Qué viene del repo de partida de Sherpas

Este repo parte de [`SherpasEngineering/hackathon-upv-2026`](https://github.com/SherpasEngineering/hackathon-upv-2026) (remoto `upstream`).

- [`BRIEF.md`](BRIEF.md): el brief oficial (reto, casos, criterios, acceso al MCP y al proxy, precios).
- [`cases/`](cases/): las cuatro familias (`financial-health.json`, `investment-analysis.json`, `persona.md`, PDF).
- [`examples/voice/`](examples/voice/): ejemplo de voz en tiempo real (Node 22).

Para traer cambios de Sherpas: `git remote add upstream git@github.com:SherpasEngineering/hackathon-upv-2026.git`
(una vez) y `git pull upstream main`. Si cambian su `README.md`, el cambio va a `BRIEF.md`; nuestro `README.md` se conserva.

## Instalación

Linux/macOS:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
./check.sh
```

Windows (PowerShell; `check.sh` desde Git Bash):

```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
$env:PYTHONPATH="src;."; .venv\Scripts\python -m pytest -q tests; .venv\Scripts\python -m finagent.run
```

Abre `out/index.html`.

**Voz:** funciona sin clave (voces gratuitas). Para la voz de la demo (ElevenLabs), las opciones, el coste y cómo
usarla desde `/ask`: [`VOICE.md`](VOICE.md).
Backend (preguntas en vivo, historial, avisos y cómo compartir un enlace): [`BACKEND.md`](BACKEND.md).

## Cómo trabajamos

Lee `AGENTS.md` (y dáselo a tu IA) antes de tocar nada: quién es responsable de cada etapa (todos pueden editar todo), el contrato y cómo se fusiona.
