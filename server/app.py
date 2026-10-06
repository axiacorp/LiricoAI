import os
import shutil
import tempfile
import threading
from pathlib import Path
from typing import Literal

import torch
import whisper
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
MODEL_NAMES = ("tiny", "tiny.en", "base", "base.en", "small", "small.en", "medium", "medium.en", "large-v1", "large-v2", "large-v3", "turbo")

app = FastAPI(title="Lírico AI Local Transcription Server", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://axiacorp.github.io",
        "http://127.0.0.1:8765",
        "http://localhost:8765",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

_models = {}
_models_lock = threading.Lock()


def preferred_device() -> str:
    requested = os.getenv("LIRICO_DEVICE", "auto").lower()
    if requested in {"cpu", "mps", "cuda"}:
        return requested
    if torch.cuda.is_available():
        return "cuda"
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def get_model(name: str, device: str):
    key = (name, device)
    with _models_lock:
        if key not in _models:
            _models[key] = whisper.load_model(name, device=device)
        return _models[key]


@app.get("/api/health")
def health():
    return {
        "ok": True,
        "device": preferred_device(),
        "models": list(MODEL_NAMES),
        "loaded_models": [name for (name, _device) in _models.keys()],
    }


@app.get("/api/models")
def models():
    return {
        "models": [{"id": name, "label": f"OpenAI Whisper local — {name}"} for name in MODEL_NAMES],
        "recommended_for_first_test": "base",
    }


@app.post("/api/transcribe")
def transcribe(
    file: UploadFile = File(...),
    model: str = Form("base"),
    language: str = Form("pt"),
    task: Literal["transcribe", "translate"] = Form("transcribe"),
    content_type: str = Form("Geral"),
):
    if model not in MODEL_NAMES:
        raise HTTPException(status_code=400, detail=f"Modelo inválido: {model}")

    suffix = Path(file.filename or "audio").suffix or ".bin"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        temp_path = Path(tmp.name)
        shutil.copyfileobj(file.file, tmp)

    prompts = {
        "Aula": "Aula em português brasileiro. Preserve termos técnicos, nomes próprios, números e unidades.",
        "Aula médica": "Aula médica em português brasileiro. Preserve terminologia médica, medicamentos, doses, vias, siglas, exames, anatomia e condutas. Não invente conteúdo incerto.",
        "Reunião": "Reunião em português brasileiro. Preserve nomes, decisões, números, datas e termos profissionais.",
        "Entrevista": "Entrevista em português brasileiro. Preserve nomes próprios, números e termos específicos.",
    }
    initial_prompt = prompts.get(content_type, "")

    device = preferred_device()
    used_device = device

    try:
        try:
            loaded_model = get_model(model, device)
            result = loaded_model.transcribe(
                str(temp_path),
                language=None if language == "auto" else language,
                task=task,
                fp16=device in {"cuda", "mps"},
                verbose=False,
                initial_prompt=initial_prompt or None,
            )
        except Exception:
            # Apple Silicon support varies between Torch/Whisper releases.
            # If MPS fails, retry the same request on CPU instead of failing the user.
            if device != "mps":
                raise
            used_device = "cpu"
            loaded_model = get_model(model, "cpu")
            result = loaded_model.transcribe(
                str(temp_path),
                language=None if language == "auto" else language,
                task=task,
                fp16=False,
                verbose=False,
                initial_prompt=initial_prompt or None,
            )

        return {
            "ok": True,
            "filename": file.filename,
            "model": model,
            "device": used_device,
            "language": result.get("language"),
            "text": (result.get("text") or "").strip(),
            "segments": [
                {
                    "start": segment.get("start"),
                    "end": segment.get("end"),
                    "text": (segment.get("text") or "").strip(),
                }
                for segment in result.get("segments", [])
            ],
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            pass


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")
