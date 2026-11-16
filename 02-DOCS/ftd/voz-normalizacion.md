---
created: 2026-11-14
status: done
branch: feat/voice-normalization
---
# FTD — Voz, fase 2: que las cifras suenen bien

- Dueño: David (`daviid-sc`)

## Intención
Una voz TTS lee literalmente: `$15,032/yr` sale como «slash Y R», `-$8,336` sin el «menos» y `**` o `## ` se cuelan.
Los textos `narrative` de los casos (los que usarán la narración con LLM y las respuestas de `/ask`) traen markdown
(611), dinero (900), `/yr` (78), rangos con raya, siglas (`IRA`, `401(k)`, `529`, `HSA`) y tickers (`VTI`, `SPDR`).

## Alcance
- Entra: `src/finagent/speech_text.py` (`to_speech(text, language)`, reglas fijas en inglés), `voice.py` envía
  `to_speech(narration)` al motor, `tests/test_speech_text.py`, `scripts/voice_listen_test.py` (prueba de escucha).
- NO entra: español (solo se quita el markdown), SSML (edge-tts ya no lo acepta), normalización con LLM, motor ElevenLabs.

## Decisiones
- **`narration` no cambia**: `guard` y los subtítulos de la escena usan el texto original; solo el audio cambia.
  El contrato no cambia.
- **Sin LLM**: reglas de expresiones regulares, gratis y deterministas. Solo cambian cómo se dice un número, nunca
  su valor: no se redondea (`$1,177,586.50` se queda entero).
- Siglas y tickers en una tabla editable (`SPOKEN_TERMS`). Las dudosas (`REIT`, `SPDR`, `FTSE`, `TBIL`, `UPRO`) van
  marcadas «check by ear».
- Raya larga: punto si empieza frase nueva (`**Title** — You hold`), coma si no.

## Checklist
- [x] Tests de cada regla y de lo que no debe tocar (`30-year`, `11/14/2026`, importes largos).
- [x] En los 312 textos de los cuatro casos: ninguna cifra cambia y no queda markdown.
- [x] `bash check.sh` pasa.
- [x] `voice_listen_test.py` genera `out/listen/before.mp3`, `after.mp3` y `samples.txt` (11 muestras).
- [x] Comprobado transcribiendo el audio con Whisper (`small.en`, local): ver Evidencia.
- [x] `JNK`: con guiones o comas se entendía «J and K»; escrito «J N K» (con espacios) Whisper lo transcribe bien en
  las cuatro frases de los casos probadas con la voz gratuita (17 nov). Sin probar con ElevenLabs.

## Evidencia (2026-11-14, Windows 11)
- `pytest -q tests/test_speech_text.py` → 27 passed.
- 155 de 312 textos de los casos cambian al normalizar; revisados a ojo 14 al azar más las 11 muestras.

- Whisper sobre `before.mp3` / `after.mp3`: antes, la lista de siglas salía como basura («Stigest jedna», «SBDR»,
  «NAF») y `~3%` perdía el «about»; después se entiende casi todo. Probadas por separado en una frase:
  `four-oh-one-Ks` → «4-1 cast» (cambiado a «four-oh-one-K plans» → «401k plans»), `N-A-V` → «and AV» (→ «net asset
  value»), `U-PRO` → «you pro» (→ `U-P-R-O`), `V-O-O` → «Vio» (→ «V-double-O»). `IRAs`, `HSA`, `ETF`, `529`, `VTI`,
  `SCHD`, `LQD`, `TBIL`, `SPDR`, `REIT`, `FTSE` se entienden bien.
- edge-tts ya leía bien `/year`, `-$8,336` y `$1M`: esas reglas sobran con edge, pero se quedan por ElevenLabs.

## Siguiente
Motor ElevenLabs para la demo (fase 3), reutilizando `to_speech`.
