from celery import Celery
import base64
from pathlib import Path
import tempfile
from transformers import pipeline

celery = Celery(
    "tasks",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

# Ładowanie modelu ASR Whisper Tiny
transcriber = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-small"
)

@celery.task(name="tasks.transcribe_audio")
def transcribe_audio(audio_b64: str):
    audio_bytes = base64.b64decode(audio_b64)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = Path(tmp.name)

    try:
        result = transcriber(str(tmp_path), return_timestamps=True)
        return result["text"]
    finally:
        tmp_path.unlink(missing_ok=True)