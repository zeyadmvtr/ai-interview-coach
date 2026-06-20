FROM python:3.12-slim

# ffmpeg is required by faster-whisper for decoding audio formats like mp3/m4a.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY .env.example .env.example

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

# NOTE: Ollama itself is NOT bundled in this image. Run Ollama separately
# (or as a sibling container) and point OLLAMA_HOST at it -- see README.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
