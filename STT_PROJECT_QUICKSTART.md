# STT Editor Project - Quick Start Guide

**Option 1: Separate Repository** (Recommended)
```
~/CsProjects/stt-editor/
we have decided to name the stt-editor lil_bro
```
- Completely independent
- Can be used in multiple projects
- Easy to version control separately

**Recommendation**: Separate repository for maximum reusability.

## Technology Recommendations

### STT Engine: **faster-whisper** (Recommended)
- **Why**: Best balance of accuracy and speed
- **Install**: `pip install faster-whisper`
- **Model**: Start with `base` (good accuracy, reasonable speed)
- **Alternative**: `small` for better accuracy, `tiny` for faster
(we will test faster whisper before we make a choice)
### Text Editor: **Rich + prompt_toolkit** (Recommended)
- **Why**: Powerful, flexible, good documentation
- **Install**: `pip install rich prompt-toolkit`
- **Alternative**: `textual` (newer, more modern, but less mature)

### LLM: **Ollama** (Recommended)
- **Why**: Local, privacy-focused, free
- **Install**: `curl -fsSL https://ollama.ai/install.sh | sh`
- **Model**: `llama3` or `mistral` (good for text cleanup)
- **Python**: `pip install ollama`

---

## Minimal Viable Product (MVP) Features

Start with these core features, then expand:

0. **Test files
1. **Basic STT** - Whisper transcribes microphone input
2. **Simple Display** - Text appears in terminal as it's transcribed
3. **Keyboard Editing** - Can type and edit text
4. **Save Function** - Save transcribed text to file
5. **Exit Command** - Clean exit

**Then add**:
- LLM cleanup
- Advanced editor features
- Configuration options
- Error handling

---

## Getting Started Checklist

### Phase 1: Setup
- [v] Create project directory
- [v] Initialize git repository
- [...] Create `requirements.txt`
- [...](conda lil_bro) Set up virtual environment
    Note we need to be using python 3.11 for wheels when working with faster wisperer.
- [ ] Install dependencies
- [ ] Create basic project structure

### Phase 2: Basic STT
- [ ] Install faster-whisper
- [ ] Test microphone access
- [ ] Implement basic transcription loop
- [ ] Print transcribed text to console
- [ ] Test with microphone

### Phase 3: Simple Editor
- [ ] Install rich/prompt_toolkit
- [ ] Create basic text buffer
- [ ] Display text in terminal
- [ ] Add keyboard input handling
- [ ] Test simultaneous STT + keyboard

### Phase 4: Polish
- [ ] Add save functionality
- [ ] Add configuration file
- [ ] Add error handling
- [ ] Test thoroughly
- [ ] Document usage

---

## Example Project Structure (Minimal)

```
stt-editor/
├── README.md
├── requirements.txt
├── config.py
├── main.py
├── stt/
│   ├── __init__.py
│   └── whisper_engine.py
├── editor/
│   ├── __init__.py
│   └── simple_editor.py
└── utils/
    ├── __init__.py
    └── audio_utils.py
```

---

## First Code Snippet (Basic STT)

```python
# stt/whisper_engine.py
from faster_whisper import WhisperModel
import sounddevice as sd
import numpy as np

class WhisperSTT:
    def __init__(self, model_size="base"):
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
        self.sample_rate = 16000
    
    def transcribe_stream(self, audio_chunk):
        """Transcribe a single audio chunk"""
        segments, info = self.model.transcribe(
            audio_chunk,
            language="en",
            beam_size=5
        )
        text = " ".join([segment.text for segment in segments])
        return text
```

---

## Next Steps

1. **Review the full plan** (`STT_PROJECT_PLAN.md`)
2. **Decide on project location** (separate repo vs subdirectory)
3. **Choose technology stack** (Whisper + Rich + Ollama recommended)
4. **Start with Phase 1** - Basic STT working
5. **Iterate** - Add features incrementally

---

## Questions to Answer Before Starting

1. **Project Name**: What should we call it?
2. **Location**: Separate repo or subdirectory?
3. **STT Engine**: Whisper (accuracy) or Vosk (speed)?
4. **Editor Library**: Rich + prompt_toolkit or Textual?
5. **LLM**: Ollama (local) or cloud API?

Once you decide, we can start building!

