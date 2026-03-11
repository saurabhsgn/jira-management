import os
import io
import json
import time
import wave
import queue
import tempfile
import threading
import datetime as dt
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

import numpy as np
import requests
import soundcard as sc
from faster_whisper import WhisperModel


# ==========================================================
# Windows-ready local Teams/live meeting notes agent
# - Captures SYSTEM SOUND + MICROPHONE together
# - Transcribes locally with faster-whisper
# - Summarizes locally with Ollama
# - Writes transcript + live notes to local files
# ==========================================================

# =========================
# Configuration
# =========================

SAMPLE_RATE = 16000
CHUNK_SECONDS = 10
SUMMARY_EVERY_N_CHUNKS = 3
OUTPUT_ROOT = "meeting_notes_output"
MEETING_TITLE = "Live Teams Call Notes"

# Audio controls
SYSTEM_GAIN = 1.0
MIC_GAIN = 1.0
MIX_CLIP = 0.95
ENABLE_SYSTEM_AUDIO = True
ENABLE_MIC_AUDIO = True

# Device selection
# Leave as None to auto-pick defaults.
# You can also set partial names like "Realtek".
SYSTEM_SPEAKER_NAME_CONTAINS = None
MIC_NAME_CONTAINS = None
INCLUDE_LOOPBACK = True

# Whisper
WHISPER_MODEL_SIZE = "base"
WHISPER_DEVICE = "cpu"
WHISPER_COMPUTE_TYPE = "int8"

# Ollama
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:7b"
MAX_TRANSCRIPT_CHARS_FOR_SUMMARY = 14000

# Optional: save raw audio chunks
SAVE_CHUNK_WAVS = False


# =========================
# Data models
# =========================

@dataclass
class TranscriptChunk:
    chunk_id: int
    started_at: str
    ended_at: str
    text: str


@dataclass
class LiveNotes:
    summary: str
    discussed_points: List[str]
    concluded_items: List[str]
    open_items: List[str]
    action_items: List[str]
    risks: List[str]


# =========================
# File helpers
# =========================

def ensure_output_dir() -> str:
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(OUTPUT_ROOT, ts)
    os.makedirs(path, exist_ok=True)
    return path


def save_text(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def append_text(path: str, content: str) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(content)


def save_json(path: str, data: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def write_wav_bytes(audio: np.ndarray, sample_rate: int) -> bytes:
    audio = np.asarray(audio, dtype=np.float32)
    audio = np.clip(audio, -1.0, 1.0)
    int16_audio = (audio * 32767.0).astype(np.int16)
    with io.BytesIO() as bio:
        with wave.open(bio, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(int16_audio.tobytes())
        return bio.getvalue()


def save_wav_file(path: str, audio: np.ndarray, sample_rate: int) -> None:
    audio = np.asarray(audio, dtype=np.float32)
    audio = np.clip(audio, -1.0, 1.0)
    int16_audio = (audio * 32767.0).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(int16_audio.tobytes())


# =========================
# Device discovery
# =========================

def list_audio_devices() -> None:
    print("\n=== Speakers / System outputs ===")
    for i, sp in enumerate(sc.all_speakers()):
        default_marker = " (default)" if sp.id == sc.default_speaker().id else ""
        print(f"[{i}] {sp.name}{default_marker}")

    print("\n=== Microphones / Inputs ===")
    for i, mic in enumerate(sc.all_microphones(include_loopback=INCLUDE_LOOPBACK)):
        default_mic = sc.default_microphone()
        default_marker = ""
        try:
            if default_mic and mic.id == default_mic.id:
                default_marker = " (default)"
        except Exception:
            pass
        print(f"[{i}] {mic.name}{default_marker}")
    print()


def find_speaker_by_name(name_contains: Optional[str]):
    speakers = sc.all_speakers()
    if name_contains:
        for sp in speakers:
            if name_contains.lower() in sp.name.lower():
                return sp
    return sc.default_speaker()


def find_mic_by_name(name_contains: Optional[str]):
    mics = sc.all_microphones(include_loopback=INCLUDE_LOOPBACK)
    if name_contains:
        for mic in mics:
            if name_contains.lower() in mic.name.lower():
                return mic
    try:
        return sc.default_microphone()
    except Exception:
        return mics[0] if mics else None


# =========================
# Local AI summarizer via Ollama
# ==========================

def call_ollama(prompt: str, model: str = OLLAMA_MODEL) -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
    }
    response = requests.post(OLLAMA_URL, json=payload, timeout=180)
    response.raise_for_status()
    return response.json().get("response", "{}").strip()


def build_summary_prompt(transcript: str) -> str:
    return f'''
You are a local meeting notes assistant.
Analyze the transcript and return STRICT JSON using exactly this schema:
{{
  "summary": "brief paragraph",
  "discussed_points": ["point 1", "point 2"],
  "concluded_items": ["decision 1"],
  "open_items": ["pending item 1"],
  "action_items": ["owner if known - task - due date if known"],
  "risks": ["risk 1"]
