# Reto — Bring the plan to life (Sigma Data Club UPV × Sherpas Wealth)

Fuentes: canales de Discord `#reto-sherpas`, `#recursos`, `#faq`, `#normas`, `#anuncios` (capturas del 12 nov 2026) y
el README del repo de partida <https://github.com/SherpasEngineering/hackathon-upv-2026> (leído el 12 nov 2026).
Si Discord y el README se contradicen, manda el anuncio más reciente de Discord.

## El reto

Sherpas es una plataforma de IA para asesores financieros en EE. UU. Con cada cliente el asesor hace tres trabajos:
recoger los datos, hacer los números y **explicar el plan**. Sherpas ya resuelve los dos primeros; el tercero se
sigue haciendo a mano, reunión a reunión.

**Haz que el plan cobre vida:** llevar a una familia desde su plan hasta entenderlo y querer actuar, "como tener a
un asesor en la sala, o mejor". Se puede diseñar para familias que verán a un asesor después o para familias que
nunca lo verán (el plan tiene que funcionar solo).

- Cualquier formato, canal o dispositivo.
- **Sherpas ya tiene tours guiados y un chat sobre el plan: una idea que sea solo eso puntúa bajo en creatividad.**
- Clavar cada cifra no puntúa: usar los datos del caso, no inventar números, dedicar el tiempo a la experiencia.
- **Producto, demo y explicación en inglés.** La comunicación del evento, en español.

## Evaluación (100 puntos)

| Puntos | Criterio | Pregunta del jurado |
|---|---|---|
| 20 | Engancha | ¿Capta la atención en segundos y la mantiene? |
| 20 | Se entiende | ¿Funciona para quien no sabe de finanzas y para un experto? |
| 20 | Mueve a actuar | ¿Quieren dar el primer paso y vuelven hasta darlo? |
| 15 | Personal | ¿Se siente hecho para esta familia y para cada persona de ella? |
| 15 | Creatividad | ¿Qué añade que no se pidió? |
| 10 | Nota de idea del viernes | ¿Elección clara y honesta sobre lo descartado y por qué? |

Extra: los días de después (dudas del día 3 o del día 30).

## Fechas y entregas (desde el canal del equipo en Discord)

| Fecha | Qué |
|---|---|
| Jue 12 nov, 15:00 | Kick-off (edificio 1E, aula 2.3) |
| **Vie 13 nov, 22:00** | `/idea`: una página como máximo, en puntos, privada para mentores. Qué vamos a construir y por qué; qué descartamos y por qué. Se puede cambiar de idea después. **10 puntos.** |
| **Mié 18 nov, 23:59** | `/entregar`: repo de GitHub, enlace al MVP funcionando o instrucciones para ejecutarlo, vídeo de 2 min (no puntúa; YouTube oculto o Drive) y explicación breve en inglés de qué y por qué |
| Jue 19 nov, 12:45 | Demo Day: pitch de 2 minutos por equipo y premios |

Se puede enviar cada entrega varias veces; cuenta la última. Tarde se acepta, marcada como fuera de plazo. Ya no se
entregan slides. Premios: 600 € / 250 € / 150 € y prácticas en Sherpas.

## Los cuatro casos (familias ficticias, importes en USD)

| Caso (`caseId`) | Nota | Pregunta |
|---|---|---|
| `timothy-melanie-weah` | 60 | Mucho efectivo y una tarjeta al 18 %. ¿A dónde va cada dólar? |
| `michael-carter` | 26 | Casa de $550.000 en 2027 y jubilarse a los 58. ¿Puede con las dos? |
| `daniel-emily-johnson` | 52 | Universidad de dos hijos y jubilarse a los 62. ¿Qué va primero? |
| `samantha-lewis` | 82 | Sin deudas; empieza la universidad y quiere segunda casa en 2030. ¿Y ahora qué? |

Cada caso tiene `financial-health.json`, `investment-analysis.json` y `persona.md` (secciones D0–D6, alertas,
preocupaciones subjetivas/objetivas y tensiones). El README del repo de partida lista 11 "puntos donde las familias
se atascan" (comprensión, atención, emoción, parejas, seguimiento, acción): es el mejor material para elegir idea.

## Recursos técnicos

- **Datos:** MCP de solo lectura `https://mcp-hackathon.sherpaswealth.com/mcp` (HTTP, tools `list_cases` y
  `get_case`), o los mismos JSON en `cases/` del repo de partida. **El MCP ya no es obligatorio.**
- **Token del MCP:** personal, dura **72 h**; cada login genera uno nuevo e invalida el anterior. Uno sacado en el
  kick-off caduca el dom 15 nov. Para que el MVP siga vivo tras la entrega, leer los JSON locales.
- **Modelos:** proxy compatible con OpenAI en `https://llm-hackathon.sherpaswealth.com/v1` con la **clave del equipo**
  (una sola para los tres, **$50** en total, válida hasta el 21 nov). Límites: 60 peticiones/min y 4 a la vez
  (una sesión de voz abierta cuenta como una).
- **Página de acceso:** <https://mcp-hackathon.sherpaswealth.com/personal-token> (correo de inscripción + código).
  Da un bloque `.env` con `MCP_URL`, `MCP_TOKEN`, `LLM_PROXY_URL`, `TEAM_KEY`.
- **Gasto:** `GET /key/info` en el proxy con la clave → `info.spend` e `info.max_budget`.

| Modelo | Tipo | Precio |
|---|---|---|
| `deepseek-flash` | Texto | $0,30 / $1,20 por 1M tokens |
| `gemini-3.5-flash-lite` | Texto | $0,30 / $2,50 |
| `gpt-5-mini` | Texto | $0,25 / $2,00 (no poner `max_tokens` < 1000) |
| `gpt-live-1` | Voz en tiempo real | $0,05 por minuto de sesión |
| `gemini-3.8-live` | Voz en tiempo real | $3 / $12 audio |
| `gpt-realtime-2.1-mini` | Voz en tiempo real | $10 / $20 audio |
| `gpt-realtime-2.1` | Voz en tiempo real | $32 / $64 audio |
| `eleven-flash-v2.5` | TTS | $0,04 por 1.000 caracteres |
| `eleven-multilingual-v2`, `eleven-v3` | TTS | $0,08 por 1.000 caracteres |
| `scribe-v2` | Voz a texto | $0,22 por hora |

**ElevenLabs tiene un tope de $1,40** dentro de los $50 (≈ 35.000 caracteres de `eleven-flash-v2.5`, unos 40 min).
El uso de voz se registra al cerrar la sesión: cerrar siempre las sesiones.

## Normas que nos afectan

- Claves solo en backend y `.env`; nunca en el repo, en código de navegador, capturas ni vídeos.
- No compartir la clave, el token ni los datos fuera del equipo. La clave es solo para el proyecto.
- El trabajo debe hacerse durante el hackathon y por los miembros del equipo.
- El código desarrollado será propiedad de Sherpas Wealth.

## ⚠️ Pendiente de aclarar (preguntar en `#dudas-reto-mcp`)

1. **Repo público o privado.** El README pide repo **público**; la norma 3 dice no subir los datos de prueba a
   repos públicos. El nuestro es privado. ¿Público con los casos dentro, público sin datos, o privado invitando a
   los mentores?
2. Comando de entrega: Discord dice `/idea` y `/entregar`; el README dice `/entrega`. Vale Discord (más reciente).
