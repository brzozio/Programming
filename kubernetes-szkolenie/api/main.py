import base64
import time
from pathlib import Path
from celery import Celery
import gradio as gr

celery = Celery(
    "tasks",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

def transcribe(audio_path: str) -> str:
    if not audio_path:
        return "Brak pliku audio."

    audio_bytes = Path(audio_path).read_bytes()
    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    task = celery.send_task("tasks.transcribe_audio", args=[audio_b64])

    timeout_seconds = 250
    start = time.time()
    while time.time() - start < timeout_seconds:
        result = celery.AsyncResult(task.id)
        if result.state == "SUCCESS":
            return str(result.result)
        if result.state in {"FAILURE", "REVOKED"}:
            return f"Blad zadania: {result.state}"
        time.sleep(1)

    return "Przekroczono czas oczekiwania na wynik."


ui = gr.Interface(
    fn=transcribe,
    inputs=gr.Audio(type="filepath", label="Audio"),
    outputs=gr.Textbox(label="Transkrypcja"),
    title="Whisper Tiny Transcriber",
    description="Wgraj plik audio, aby uzyskac transkrypcje przez Celery + Redis."
)


if __name__ == "__main__":
    ui.launch(server_name="0.0.0.0", server_port=7860)