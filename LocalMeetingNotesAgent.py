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
}}

Rules:
- Do not invent facts.
- Be concise.
- Use concluded_items only for clear decisions or confirmed outcomes.
- Use open_items only for unresolved questions, dependencies, or pending clarifications.
- Use action_items only for explicit or strongly implied next steps.

Transcript:
{transcript}
'''


def summarize_transcript(transcript: str) -> LiveNotes:
    trimmed = transcript[-MAX_TRANSCRIPT_CHARS_FOR_SUMMARY:]
    raw = call_ollama(build_summary_prompt(trimmed))
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {
            "summary": "Unable to parse local AI summary output.",
            "discussed_points": [],
            "concluded_items": [],
            "open_items": [],
            "action_items": [],
            "risks": [],
        }
    return LiveNotes(
        summary=data.get("summary", ""),
        discussed_points=data.get("discussed_points", []),
        concluded_items=data.get("concluded_items", []),
        open_items=data.get("open_items", []),
        action_items=data.get("action_items", []),
        risks=data.get("risks", []),
    )


# =========================
# Transcriber
# =========================

class LocalTranscriber:
    def __init__(self) -> None:
        self.model = WhisperModel(
            WHISPER_MODEL_SIZE,
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE_TYPE,
        )

    def transcribe_audio(self, audio_mono: np.ndarray, sample_rate: int) -> str:
        wav_bytes = write_wav_bytes(audio_mono, sample_rate)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(wav_bytes)
            tmp_path = tmp.name
        try:
            segments, _ = self.model.transcribe(tmp_path, beam_size=1, vad_filter=True)
            text = " ".join(seg.text.strip() for seg in segments).strip()
            return text
        finally:
            try:
                os.remove(tmp_path)
            except OSError:
                pass


# =========================
# Audio capture and mixing
# =========================

def to_mono(arr: np.ndarray) -> np.ndarray:
    arr = np.asarray(arr, dtype=np.float32)
    if arr.ndim == 1:
        return arr
    if arr.ndim == 2:
        return arr.mean(axis=1)
    raise ValueError("Unexpected audio array shape")


class DualAudioMixer:
    def __init__(self, speaker, mic, sample_rate: int = SAMPLE_RATE):
        self.speaker = speaker
        self.mic = mic
        self.sample_rate = sample_rate

    def record_system(self, seconds: int) -> np.ndarray:
        if not ENABLE_SYSTEM_AUDIO or self.speaker is None:
            return np.zeros(int(seconds * self.sample_rate), dtype=np.float32)
        with self.speaker.recorder(samplerate=self.sample_rate) as rec:
            data = rec.record(numframes=int(seconds * self.sample_rate))
        mono = to_mono(data) * SYSTEM_GAIN
        return mono.astype(np.float32)

    def record_mic(self, seconds: int) -> np.ndarray:
        if not ENABLE_MIC_AUDIO or self.mic is None:
            return np.zeros(int(seconds * self.sample_rate), dtype=np.float32)
        with self.mic.recorder(samplerate=self.sample_rate) as rec:
            data = rec.record(numframes=int(seconds * self.sample_rate))
        mono = to_mono(data) * MIC_GAIN
        return mono.astype(np.float32)

    def record_mixed_chunk(self, seconds: int) -> np.ndarray:
        results: Dict[str, np.ndarray] = {}

        def run_system():
            results["system"] = self.record_system(seconds)

        def run_mic():
            results["mic"] = self.record_mic(seconds)

        threads = []
        if ENABLE_SYSTEM_AUDIO:
            t1 = threading.Thread(target=run_system, daemon=True)
            threads.append(t1)
            t1.start()
        if ENABLE_MIC_AUDIO:
            t2 = threading.Thread(target=run_mic, daemon=True)
            threads.append(t2)
            t2.start()

        for t in threads:
            t.join()

        system_audio = results.get("system", np.zeros(int(seconds * self.sample_rate), dtype=np.float32))
        mic_audio = results.get("mic", np.zeros(int(seconds * self.sample_rate), dtype=np.float32))

        min_len = min(len(system_audio), len(mic_audio)) if len(system_audio) and len(mic_audio) else max(len(system_audio), len(mic_audio))
        if min_len == 0:
            return np.zeros(int(seconds * self.sample_rate), dtype=np.float32)

        if len(system_audio) != min_len:
            system_audio = system_audio[:min_len]
        if len(mic_audio) != min_len:
            mic_audio = mic_audio[:min_len]

        mixed = system_audio + mic_audio
        peak = np.max(np.abs(mixed)) if mixed.size else 0.0
        if peak > MIX_CLIP and peak > 0:
            mixed = mixed * (MIX_CLIP / peak)
        return mixed.astype(np.float32)


# =========================
# Notes engine
# =========================

class MeetingNotesAgent:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.transcriber = LocalTranscriber()
        self.transcript_chunks: List[TranscriptChunk] = []
        self.live_notes = LiveNotes("", [], [], [], [], [])
        self.chunk_counter = 0
        self.stop_event = threading.Event()

        self.transcript_path = os.path.join(output_dir, "transcript.txt")
        self.notes_path = os.path.join(output_dir, "live_notes.md")
        self.summary_json_path = os.path.join(output_dir, "latest_summary.json")
        self.config_json_path = os.path.join(output_dir, "run_config.json")
        self.chunks_dir = os.path.join(output_dir, "chunks")
        if SAVE_CHUNK_WAVS:
            os.makedirs(self.chunks_dir, exist_ok=True)

        save_text(self.transcript_path, f"# {MEETING_TITLE}\n\n")
        save_text(self.notes_path, f"# {MEETING_TITLE}\n\nWaiting for transcript...\n")
        save_json(self.config_json_path, {
            "meeting_title": MEETING_TITLE,
            "sample_rate": SAMPLE_RATE,
            "chunk_seconds": CHUNK_SECONDS,
            "summary_every_n_chunks": SUMMARY_EVERY_N_CHUNKS,
            "ollama_model": OLLAMA_MODEL,
            "whisper_model": WHISPER_MODEL_SIZE,
            "enable_system_audio": ENABLE_SYSTEM_AUDIO,
            "enable_mic_audio": ENABLE_MIC_AUDIO,
        })

    def full_transcript(self) -> str:
        return "\n".join(
            f"[{x.started_at} - {x.ended_at}] {x.text}" for x in self.transcript_chunks if x.text
        )

    def update_live_notes(self) -> None:
        self.live_notes = summarize_transcript(self.full_transcript())
        self.render_notes()
        save_json(self.summary_json_path, asdict(self.live_notes))

    def render_notes(self) -> None:
        ln = self.live_notes
        lines = [
            f"# {MEETING_TITLE}",
            "",
            "## Live Summary",
            ln.summary or "No summary yet.",
            "",
            "## Discussed Points",
        ]
        lines.extend([f"- {x}" for x in ln.discussed_points] or ["- None yet"])
        lines += ["", "## Concluded Items"]
        lines.extend([f"- {x}" for x in ln.concluded_items] or ["- None yet"])
        lines += ["", "## Open Items"]
        lines.extend([f"- {x}" for x in ln.open_items] or ["- None yet"])
        lines += ["", "## Action Items"]
        lines.extend([f"- {x}" for x in ln.action_items] or ["- None yet"])
        lines += ["", "## Risks"]
        lines.extend([f"- {x}" for x in ln.risks] or ["- None yet"])
        save_text(self.notes_path, "\n".join(lines) + "\n")

    def run(self, mixer: DualAudioMixer) -> None:
        print("Listening... Press Ctrl+C to stop.\n")
        while not self.stop_event.is_set():
            started_at = dt.datetime.now()
            audio = mixer.record_mixed_chunk(CHUNK_SECONDS)
            ended_at = dt.datetime.now()

            if SAVE_CHUNK_WAVS:
                wav_path = os.path.join(self.chunks_dir, f"chunk_{self.chunk_counter + 1:04d}.wav")
                save_wav_file(wav_path, audio, SAMPLE_RATE)

            text = self.transcriber.transcribe_audio(audio, SAMPLE_RATE)
            self.chunk_counter += 1
            chunk = TranscriptChunk(
                chunk_id=self.chunk_counter,
                started_at=started_at.strftime("%H:%M:%S"),
                ended_at=ended_at.strftime("%H:%M:%S"),
                text=text,
            )
            self.transcript_chunks.append(chunk)

            line = f"[{chunk.started_at} - {chunk.ended_at}] {text}\n"
            append_text(self.transcript_path, line)
            print(line.strip())

            if self.chunk_counter % SUMMARY_EVERY_N_CHUNKS == 0:
                try:
                    self.update_live_notes()
                    print(f"Updated live notes -> {self.notes_path}")
                except Exception as exc:
                    print(f"Summary update failed: {exc}")

        try:
            self.update_live_notes()
        except Exception as exc:
            print(f"Final summary update failed: {exc}")


# =========================
# Main
# =========================

def main() -> None:
    print("Local Live Meeting Notes Agent (Windows-ready)")
    print("This records only local audio available on your machine.")
    print("It does not connect to or control Teams directly.")

    out_dir = ensure_output_dir()
    print(f"\nOutput folder: {out_dir}")

    list_audio_devices()

    speaker = find_speaker_by_name(SYSTEM_SPEAKER_NAME_CONTAINS) if ENABLE_SYSTEM_AUDIO else None
    mic = find_mic_by_name(MIC_NAME_CONTAINS) if ENABLE_MIC_AUDIO else None

    print("Selected sources:")
    print(f"- System audio: {speaker.name if speaker else 'disabled'}")
    print(f"- Microphone:   {mic.name if mic else 'disabled'}")
    print(f"- Whisper:      {WHISPER_MODEL_SIZE}")
    print(f"- Ollama:       {OLLAMA_MODEL}")
    print()

    mixer = DualAudioMixer(speaker=speaker, mic=mic, sample_rate=SAMPLE_RATE)
    agent = MeetingNotesAgent(out_dir)

    try:
        agent.run(mixer)
    except KeyboardInterrupt:
        print("\nStopping and writing final notes...")
        agent.stop_event.set()
        try:
            agent.update_live_notes()
        except Exception as exc:
            print(f"Final write failed: {exc}")

    print("\nDone.")
    print(f"Transcript file : {agent.transcript_path}")
    print(f"Live notes file : {agent.notes_path}")
    print(f"Summary JSON    : {agent.summary_json_path}")


if __name__ == "__main__":
    main()
