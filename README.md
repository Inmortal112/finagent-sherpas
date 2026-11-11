# FinAgent — Sigma × Sherpas

Agente que presenta y narra diagnósticos financieros de Sherpas Wealth. Estado: esqueleto con mocks.

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

## Cómo trabajamos

Lee `AGENTS.md` (y dáselo a tu IA) antes de tocar nada: quién es dueño de qué, el contrato y cómo se fusiona.
