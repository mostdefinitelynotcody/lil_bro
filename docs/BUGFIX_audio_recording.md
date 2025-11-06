# Bug Investigation: `paInvalidSampleRate` on Recording

## Summary
- **Command**: `python -m tests.tools.record_samples --samplerate 16000 --duration 12 --device 0`
- **Error**:
  ```
  Expression 'paInvalidSampleRate' failed in 'src/hostapi/alsa/pa_linux_alsa.c', line: 2050
  ...
  Error: Recording failed. Check microphone permissions or device index.
  ```
- **Impact**: Utility cannot record audio fixtures; no WAV/transcript saved.

## Observations
- Device list (`--list-devices`) shows:
  - `0 HDA Intel PCH: ALC255 Analog (hw:0,0), ALSA (2 in, 2 out)`
  - `12 default, ALSA (64 in, 64 out)`
- Recording fails immediately after the countdown.
- Error originates from PortAudio via ALSA config (`paInvalidSampleRate`).

## Hypotheses
1. Input device `0` does not support 16 kHz (`16000 Hz`) sample rate; may require 44.1 kHz or 48 kHz.
2. PipeWire/ALSA default (device `12`) handles resampling; using `--device 12` might work.
3. Need to specify `channels=1` (already enforced) but some drivers expect `frames_per_buffer` tweak.

## Findings
- Probe results:
  - Device `0` rejected 16 kHz but accepted 44.1 kHz and 48 kHz.
  - Default device (`None`/`12`) accepted 16 kHz, 44.1 kHz, and 48 kHz.
- Recording with `--device 12 --samplerate 16000` succeeded; generated fixtures:
  - `tests/fixtures/audio/20251106-155936_punctuation_practice.wav`
  - `tests/fixtures/audio/20251106-160028_numbers_and_dates.wav`
- Manifest updated with matching transcript metadata.

## Next Steps
1. Detect unsupported sample rates in the recorder and auto-fallback (or prompt) before capturing.
2. Provide a user-friendly device selector in the CLI (tracked in Phase 5 polish tasks).
3. Consider optional resampling when hardware prefers 48 kHz.

## Workaround Ideas
- Allow the tool to fall back to supported sample rates (e.g., detect via `sd.query_devices()`).
- Expose `--samplerate 48000` as default with internal resampling to 16 kHz before saving.
- Integrate device selector producing `default` if ALSA/PipeWire handles resampling better.

## Notes
- Fedora/PipeWire often advertises large channel counts but still forwards to the actual hardware.
- Ensure microphone permissions (PipeWire/JACK) are granted, but error indicates sample rate mismatch rather than permissions.

