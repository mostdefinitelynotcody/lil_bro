# Test Audio Fixtures

This directory holds reusable audio/transcript pairs for validating the
speech-to-text pipeline.

## Structure

- `audio/` – recorded `.wav` files captured at 16 kHz, mono.
- `transcripts/` – text files containing the expected transcript for each audio sample.
- `scripts.json` – catalog of prompts that readers should speak when creating new samples.
- `manifest.json` – metadata index linking audio files to transcripts and recording details.

## Recording Workflow

1. Activate the project environment and ensure a microphone is available:
   ```bash
   conda activate lil_bro_py311
   python -m tests.tools.record_samples --list-devices
   ```
2. Launch the recorder and follow the prompts (press Enter to stop recording):
   ```bash
   python -m tests.tools.record_samples --samplerate 16000
   ```
3. Choose a script to read. After a countdown the tool captures the audio until you press Enter, saves the associated transcript, and updates `manifest.json`.
4. Review the output paths printed by the tool. Re-record as needed for clarity.

## Adding New Scripts

Edit `scripts.json` to add or modify the text prompts. Each entry should include:

- `id` – short unique slug.
- `title` – human-friendly label.
- `text` – the paragraph readers will voice during recording.

## Using Samples in Tests

Automated tests can iterate over the entries in `manifest.json` to load audio files
and compare STT output against the stored transcript text.

