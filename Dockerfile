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

# The page of the stage, built without audio: narration audio is made by the voice stage with its own keys.
RUN VOICE_ENGINE=mock python -m finagent.run

# Hosts such as Render, Fly or Railway set PORT. Keys come from the host's environment, never from the image.
CMD ["sh", "-c", "uvicorn finagent.server:app --host 0.0.0.0 --port ${PORT}"]
