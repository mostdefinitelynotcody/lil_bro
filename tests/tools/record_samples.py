#!/usr/bin/env python3
"""Interactive utility for recording paired audio/transcript fixtures.

Usage:
    python -m tests.tools.record_samples [options]

The tool will:
  * Show available test scripts loaded from tests/fixtures/scripts.json
  * Prompt you to choose a script to read aloud
  * Record audio via the system microphone and save a WAV file
  * Save the reference transcript text alongside the audio
  * Update tests/fixtures/manifest.json with metadata about the sample

The generated fixtures can be reused by automated tests to validate
speech-to-text accuracy against a known reference transcript.
"""

from __future__ import annotations

import argparse
import json
import sys
import wave
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import sounddevice as sd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures"
SCRIPTS_PATH = FIXTURES_DIR / "scripts.json"
AUDIO_DIR = FIXTURES_DIR / "audio"
TRANSCRIPT_DIR = FIXTURES_DIR / "transcripts"
MANIFEST_PATH = FIXTURES_DIR / "manifest.json"


def load_scripts() -> List[Dict[str, Any]]:
    if not SCRIPTS_PATH.exists():
        raise FileNotFoundError(
            f"Could not find script file at {SCRIPTS_PATH}. "
            "Run `python tests/tools/record_samples.py --check` "
            "to verify setup."
        )
    with SCRIPTS_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def ensure_directories() -> None:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)


def countdown(seconds: int) -> None:
    for remaining in range(seconds, 0, -1):
        print(f"  Recording starts in {remaining}…", end="\r", flush=True)
        sd.sleep(1000)
    print("  Recording…          ", flush=True)


def record_audio_until_enter(samplerate: int, device: int | None) -> np.ndarray:
    """Capture audio until the user presses Enter."""
    buffers: List[np.ndarray] = []

    def callback(indata, frames, time_info, status):  # pragma: no cover - realtime callback
        if status:
            print(f"[sounddevice] {status}", file=sys.stderr)
        buffers.append(indata.copy())

    try:
        with sd.InputStream(
            samplerate=samplerate,
            channels=1,
            dtype="float32",
            device=device,
            callback=callback,
        ):
            input("  Recording… Press Enter to stop.\n")
    except Exception as exc:  # pragma: no cover - interactive hardware access
        raise RuntimeError(
            "Recording failed. Check microphone permissions or device index."
        ) from exc
    if not buffers:
        return np.empty((0, 1), dtype="float32")
    return np.concatenate(buffers, axis=0)


def save_wav(audio: np.ndarray, samplerate: int, filepath: Path) -> None:
    audio = np.clip(audio.squeeze(), -1.0, 1.0)
    pcm16 = np.int16(audio * 32767)
    with wave.open(str(filepath), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)  # 16-bit PCM
        wav_file.setframerate(samplerate)
        wav_file.writeframes(pcm16.tobytes())


def update_manifest(entry: Dict[str, Any]) -> None:
    manifest: Dict[str, Any]
    if MANIFEST_PATH.exists():
        with MANIFEST_PATH.open("r", encoding="utf-8") as file:
            manifest = json.load(file)
    else:
        manifest = {"samples": []}

    manifest.setdefault("samples", []).append(entry)
    with MANIFEST_PATH.open("w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=2)


def prompt_choice(scripts: List[Dict[str, Any]]) -> Dict[str, Any] | None:
    print("\nAvailable test scripts:")
    for idx, script in enumerate(scripts, start=1):
        print(f"  {idx}. {script['title']} ({script['id']})")

    while True:
        raw = input("\nSelect a script number to record (or 'q' to quit): ").strip()
        if raw.lower() in {"q", "quit", "exit"}:
            return None
        if not raw.isdigit():
            print("Please enter a valid number.")
            continue
        index = int(raw) - 1
        if 0 <= index < len(scripts):
            return scripts[index]
        print("Selection out of range. Try again.")


def record_script_sample(
    script: Dict[str, Any],
    args: argparse.Namespace,
) -> None:
    print("\n--- Recording Script ---")
    print(f"Title: {script['title']}")
    print("Please read the following text aloud during the recording:\n")
    print(script["text"])
    input("\nPress Enter when you're ready. You'll get a short countdown.")

    countdown(args.countdown)
    audio = record_audio_until_enter(args.samplerate, args.device)
    print("Recording complete. You can press Ctrl+C to exit at any time.\n")

    if audio.size == 0:
        print("No audio captured. Skipping save.")
        return

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    slug = f"{timestamp}_{script['id']}"
    audio_path = AUDIO_DIR / f"{slug}.wav"
    transcript_path = TRANSCRIPT_DIR / f"{slug}.txt"

    save_wav(audio, args.samplerate, audio_path)
    transcript_path.write_text(script["text"], encoding="utf-8")

    update_manifest(
        {
            "id": slug,
            "script_id": script["id"],
            "title": script["title"],
            "audio_path": str(audio_path.relative_to(PROJECT_ROOT)),
            "transcript_path": str(transcript_path.relative_to(PROJECT_ROOT)),
            "samplerate": args.samplerate,
            "duration_seconds": round(audio.shape[0] / args.samplerate, 2),
            "recorded_at": timestamp,
        }
    )
    print(f"Saved audio to {audio_path}")
    print(f"Saved transcript to {transcript_path}")


def list_devices() -> None:
    print("\nDetected audio devices:")
    print(sd.query_devices())


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Record paired audio fixtures for STT testing.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--samplerate",
        type=int,
        default=16_000,
        help="Sample rate for recordings (Hz).",
    )
    parser.add_argument(
        "--device",
        type=int,
        default=None,
        help="Sounddevice input device index. Use --list-devices to inspect.",
    )
    parser.add_argument(
        "--countdown",
        type=int,
        default=3,
        help="Countdown seconds before recording starts.",
    )
    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="List available audio devices and exit.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify directories and script file exist, then exit.",
    )
    return parser.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)

    if args.list_devices:
        list_devices()
        return 0

    ensure_directories()

    if args.check:
        if not SCRIPTS_PATH.exists():
            print(f"Missing scripts file at {SCRIPTS_PATH}")
            return 1
        print("Environment looks good. Ready to record samples.")
        return 0

    scripts = load_scripts()
    if not scripts:
        print("No scripts available. Add entries to scripts.json first.")
        return 1

    while True:
        script = prompt_choice(scripts)
        if script is None:
            print("Exiting.")
            return 0
        try:
            record_script_sample(script, args)
        except Exception as exc:  # pragma: no cover - interactive flow
            print(f"Error: {exc}")
            continue
        again = input("\nRecord another sample? [Y/n]: ").strip().lower()
        if again in {"n", "no"}:
            print("Done. Happy testing!")
            return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main(sys.argv[1:]))

