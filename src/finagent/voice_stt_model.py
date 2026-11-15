"""Speech to text with a model that listens, through the Sherpas proxy. The fallback when Scribe fails.

Added by Samuel on 2026-11-15: that day the proxy answered 401 "Invalid API key" from ElevenLabs on both
speech and transcription, so without a personal ELEVENLABS_API_KEY nobody could ask out loud.
`gemini-3.5-flash-lite` takes the browser recording as it is (webm, ogg, mp3, wav, m4a) and answered in
1.3 to 2.4 s. No extra library: plain urllib, like voice_eleven.
"""
import base64
import json
import os
import urllib.request

DEFAULT_MODEL = "gemini-3.5-flash-lite"
NOTHING_SAID = "NONE"
MIME_TYPES = {"webm": "audio/webm", "ogg": "audio/ogg", "oga": "audio/ogg", "mp3": "audio/mpeg",
              "wav": "audio/wav", "m4a": "audio/mp4", "mp4": "audio/mp4", "flac": "audio/flac"}
PROMPT = ("Transcribe this recording word for word, in {language}. Reply with the spoken words only, "
          f"no quotes and no comments. If nobody speaks, reply with exactly {NOTHING_SAID}.")
LANGUAGES = {"en": "English", "es": "Spanish"}


def available() -> bool:
    return bool((os.getenv("TEAM_KEY") or "").strip() and (os.getenv("LLM_PROXY_URL") or "").strip())


def transcribe(audio: bytes, filename: str, language: str = "en") -> str:
    """Text of one recorded question, or "" when nothing was said. Raises on any failure."""
    proxy = os.environ["LLM_PROXY_URL"].strip().rstrip("/")
    base = proxy if proxy.endswith("/v1") else f"{proxy}/v1"
    extension = os.path.splitext(filename)[1].lstrip(".").lower()
    mime = MIME_TYPES.get(extension, "audio/webm")
    body = {
        "model": (os.getenv("STT_FALLBACK_MODEL") or DEFAULT_MODEL).strip(),
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": PROMPT.format(language=LANGUAGES.get(language, "English"))},
            {"type": "file", "file": {"file_data": f"data:{mime};base64,{base64.b64encode(audio).decode()}"}},
        ]}],
    }
    request = urllib.request.Request(
        f"{base}/chat/completions", data=json.dumps(body).encode(), method="POST",
        headers={"Authorization": f"Bearer {os.environ['TEAM_KEY'].strip()}", "Content-Type": "application/json"})
    reply = json.loads(_post(request))
    text = (reply["choices"][0]["message"]["content"] or "").strip().strip('"')
    return "" if text.upper().rstrip(".") == NOTHING_SAID else text


def _post(request: urllib.request.Request) -> bytes:
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read()
