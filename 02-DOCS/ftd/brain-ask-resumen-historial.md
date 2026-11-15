---
created: 2026-11-15
status: done
branch: feat/brain-ask-summary
---
# `/ask` recuerda la conversación: resumen del historial

- Dueño: Samuel (`Inmortal112`)

## Intención
Hoy cada pregunta es independiente: el historial se guarda pero no vuelve al modelo. Si la familia pregunta «Why
does my garden dry up?» y después «and what can I do about it?», el modelo no sabe qué es «it». Samuel eligió el
**resumen del historial** como primera forma de escalar el contexto (`escalabilidad.md`). Este cambio construye el
nivel A: un resumen hecho con código, sin llamadas extra.

## Alcance
- Entra: `sessions.py` (`context_for`), `ask.py` (parámetro `context` y regla en las instrucciones), `server.py`
  (lo pasa en `/ask`, `/ask/stream` y `/worry`), `.env.example` (`ASK_HISTORY`), tests, `escalabilidad.md` y
  `BACKEND.md` al día.
- NO entra: el nivel B (resumen escrito por el modelo); memoria entre familias; el contrato `Presentation`; la
  página (`stage`, `chat_page.html`): la forma de las rutas no cambia.

## Decisiones
- **Se calcula al preguntar, no se guarda.** El resumen sale del propio archivo de la sesión (preocupaciones,
  partes más preguntadas, paso elegido). Guardarlo aparte sería un segundo dato que puede quedarse viejo.
- **Sin cifras en el resumen:** los números de lo que escribió la familia se cambian por «an amount». Así el
  resumen no puede meter una cifra en una escena que no la tiene.
- **El último turno va literal** (pregunta y respuesta), para entender «that» o «it». Puede traer cifras: las
  instrucciones dicen que no se usen, y `guard` rechaza la respuesta si aparecen en una escena que no las tiene.
- **Tamaño fijo:** como mucho 3 preocupaciones, 3 partes y 1 turno anterior, con textos cortados a 300 caracteres.
- **La primera pregunta no cambia:** sin historia, el mensaje y las instrucciones son los de antes.
- **Interruptor `ASK_HISTORY=off`** en `.env`, por si en un ensayo empeora las respuestas.

## Checklist
- [x] Sin turnos, no hay contexto y la llamada es idéntica a la de antes → test.
- [x] Con turnos, el contexto trae el turno anterior, las partes y el paso, y el resumen no lleva cifras → test.
- [x] `ask.answer` envía `conversation` y la regla solo cuando hay contexto → test.
- [x] Dos `/ask` seguidos en la misma sesión: la segunda llamada al modelo lleva la primera pregunta → test.
- [x] Una cifra del turno anterior usada en otra escena se rechaza → test.
- [x] `ASK_HISTORY=off` lo desactiva → test.
- [x] `./check.sh` pasa sin llamar al modelo.
- [x] Prueba real: pregunta de seguimiento con el servidor arrancado.

## Evidencia (2026-11-15)
- `pytest -q tests/test_ask_context.py` → `9 passed` (contexto vacío al empezar, resumen sin cifras, tamaño fijo
  con 30 turnos, respuesta no dada no se repite, interruptor, primera pregunta idéntica, seguimiento con
  `conversation`, cifra del turno anterior rechazada en otra escena, dos `/ask` por la ruta real).
- **Servidor real** (`uvicorn`, puerto 8765, `deepseek-flash`), diez preguntas en tres sesiones:
  - Samantha: «Why does my garden dry up?» → `timeline`, `garden` (2,4 s); «and what can I do about it?» →
    `move_3`, `garden` (4,2 s); «how much does that raise my score?» → `move_3` (2,1 s).
  - Michael: mismas tres → `timeline`, `move_3`, `move_3`, todas `garden` (2,0 / 6,2 / 2,1 s).
  - Weah: «How bad is the credit card?» → `pillar_debt`, `walls` (4,8 s); «what should we do about it?» →
    `move_1`, `walls` (1,7 s); «and after that one?» → `move_2`, `roof` (1,7 s); «Should I buy crypto with it?» →
    `off_plan` (1,0 s).
  - Las diez con `source` `model` u `off_plan`: ninguna rechazada por `guard`.
- **Antes de la regla «misma parte de la casa»** (primera prueba): la segunda pregunta de Samantha iba a `intro`
  y tardó 9,6 s. Sin historial iba a `move_1` (seguro de hogar), que no tiene que ver con el jardín.
- Gasto (`/key/info`): de `0.411` a `0.451` en esta sesión de pruebas (unas 16 preguntas; la otra sesión de
  Claude también pudo gastar en ese rato).
- **verify (15 nov, sobre `8811172` + cambios sin commit):** `./check.sh` → `141 passed`, `OK -> out/index.html`;
  `compileall src contracts tests` → sin errores. `ruff` y `mypy`: HERRAMIENTA-AUSENTE. Veredicto: PASA.
- Sin comprobar: la muestra es de diez preguntas; ninguna persona de fuera lo ha probado. No se ha medido si el
  mensaje más largo alarga la espera de forma apreciable (los tiempos entran en el rango de antes, 2,6-4,4 s,
  salvo uno de 6,2 s). Visto al pasar: una respuesta dijo «six years before your plan ends at 91», una resta
  que el modelo hizo por su cuenta; `guard` deja pasar los números pequeños escritos con letras.

## Siguiente
Probarlo en la página de la casa (`stage`) cuando esté fusionada, con preguntas seguidas.
