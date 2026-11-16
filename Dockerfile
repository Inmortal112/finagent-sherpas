# Under One Roof backend (finagent.server). Build: docker build -t under-one-roof .
# Run:   docker run -p 8000:8000 --env-file .env under-one-roof
FROM python:3.13-slim

WORKDIR /app
ENV PYTHONPATH=src:. PYTHONUNBUFFERED=1 PORT=8000

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY contracts contracts
COPY src src
COPY cases cases
COPY narrations narrations

# Every family in both modes (out/families/<family>/<mode>/), narrated with the free edge voice: no key is
# needed, only network during the build. If edge cannot be reached the voice stage falls back to silent mock
# audio, so check the build log for the mp3 count.
RUN VOICE_ENGINE=edge python -m finagent.run --all

# Hosts such as Render, Fly or Railway set PORT. Keys come from the host's environment, never from the image.
CMD ["sh", "-c", "uvicorn finagent.server:app --host 0.0.0.0 --port ${PORT}"]
