# Speech-to-Text Project Plan

## Project Overview

A standalone, high-quality speech-to-text (STT) application with:
- **Live transcription** - Real-time speech-to-text conversion
- **Local processing** - All processing happens offline
- **Inline CLI editor** - Text appears in a terminal-based editor
- **Simultaneous editing** - Keyboard input works while STT is active
- **LLM cleanup module** - AI-powered error correction for STT mistakes

**Goal**: Create a reusable STT tool that can be integrated into multiple projects (including GlassSpector).

---

## Core Features

### 1. Live Transcription Engine
- Real-time speech-to-text conversion
- Low latency (< 500ms)
- High accuracy
- Continuous listening mode
- Visual feedback (waveform, confidence indicators)

### 2. Inline CLI Text Editor
- Terminal-based text editor (like nano/vim but simpler)
- Real-time text insertion from STT
- Keyboard shortcuts for editing
- Cursor management
- Text formatting support

### 3. Simultaneous Input Handling
- STT audio input (microphone)
- Keyboard input (editing)
- Both work concurrently without conflicts
- Thread-safe text buffer

### 4. LLM Cleanup Module
- Trigger via keyboard shortcut or voice keyword
- Sends current text to LLM with context
- LLM fixes common STT errors:
  - Homophones (there/their/they're)
  - Punctuation
  - Capitalization
  - Grammar
  - Context-aware corrections
- Returns cleaned text
- Option to accept/reject changes

---

## Technology Stack

### Speech-to-Text Options

#### Option 1: Whisper (Recommended)
- **Library**: `openai-whisper` or `faster-whisper`
- **Pros**:
  - Very high accuracy
  - Multiple model sizes (tiny to large)
  - Supports many languages
  - Good punctuation/capitalization
- **Cons**:
  - Higher latency than Vosk
  - More CPU/GPU intensive
- **Best for**: High accuracy, offline use

#### Option 2: Vosk (Current in GlassSpector)
- **Library**: `vosk`
- **Pros**:
  - Very fast (low latency)
  - Lightweight
  - Good for real-time
- **Cons**:
  - Lower accuracy than Whisper
  - Less punctuation
- **Best for**: Real-time, low-resource systems

#### Option 3: Hybrid Approach
- Use Vosk for real-time transcription
- Use Whisper for cleanup/verification
- Best of both worlds

**Recommendation**: Start with **Whisper (faster-whisper)** for best accuracy, with option to switch to Vosk for lower latency.

### Text Editor
- **Library**: `rich` + `prompt_toolkit` or `textual`
- **Alternative**: Custom implementation with `curses` or `blessed`
- **Features needed**:
  - Real-time text updates
  - Cursor positioning
  - Keyboard shortcuts
  - Scrolling
  - Syntax highlighting (optional)

### LLM Integration
- **Options**:
  - Ollama (local, recommended)
  - OpenAI API (cloud)
  - Gemini API (cloud)
  - Local model via transformers
- **Recommendation**: Ollama for local, privacy-focused cleanup

### Audio Input
- **Library**: `sounddevice` or `pyaudio`
- **Features**:
  - Microphone selection
  - Audio level monitoring
  - Noise reduction (optional)

---

## Project Structure

```
stt-editor/
├── README.md
├── requirements.txt
├── setup.py
├── config.py                 # Configuration file
├── main.py                   # Entry point
├── stt/
│   ├── __init__.py
│   ├── whisper_engine.py     # Whisper STT implementation
│   ├── vosk_engine.py        # Vosk STT implementation (optional)
│   ├── audio_input.py        # Microphone input handling
│   └── transcription.py      # Transcription management
├── editor/
│   ├── __init__.py
│   ├── cli_editor.py         # Main CLI editor
│   ├── text_buffer.py        # Thread-safe text buffer
│   ├── cursor.py             # Cursor management
│   └── keyboard_handler.py   # Keyboard input handling
├── cleanup/
│   ├── __init__.py
│   ├── llm_cleanup.py        # LLM integration for cleanup
│   ├── error_detection.py   # Detect common STT errors
│   └── prompt_templates.py  # LLM prompts for cleanup
├── utils/
│   ├── __init__.py
│   ├── audio_utils.py       # Audio utilities
│   └── text_utils.py        # Text processing utilities
└── tests/
    ├── test_stt.py
    ├── test_editor.py
    └── test_cleanup.py
```

---

## Architecture

### Component Interaction

```
┌─────────────────┐
│  Audio Input    │
│  (Microphone)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  STT Engine     │
│  (Whisper/Vosk) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌─────────────────┐
│  Text Buffer    │◄─────┤  Keyboard Input │
│  (Thread-safe)  │      │  (Editing)      │
└────────┬────────┘      └─────────────────┘
         │
         ▼
┌─────────────────┐
│  CLI Editor     │
│  (Display)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LLM Cleanup    │
│  (On demand)    │
└─────────────────┘
```

### Threading Model

1. **Main Thread**: CLI editor display and keyboard input
2. **STT Thread**: Continuous audio capture and transcription
3. **LLM Thread**: Async cleanup requests (non-blocking)

### Data Flow

1. **Audio → STT**: Microphone captures audio → STT engine transcribes
2. **STT → Buffer**: Transcribed text appended to thread-safe buffer
3. **Buffer → Editor**: Editor reads from buffer and displays
4. **Keyboard → Buffer**: User edits directly modify buffer
5. **Buffer → LLM**: On cleanup trigger, send buffer to LLM
6. **LLM → Buffer**: LLM returns cleaned text, user accepts/rejects

---

## Implementation Phases

### Phase 1: Core STT Engine
**Goal**: Get basic STT working with live transcription

**Tasks**:
- [ ] Set up project structure
- [ ] Install and configure Whisper (faster-whisper)
- [ ] Implement audio input capture
- [ ] Create basic transcription loop
- [ ] Output transcribed text to console
- [ ] Test with microphone

**Deliverable**: Working STT that prints text to terminal

---

### Phase 2: CLI Text Editor
**Goal**: Create inline text editor with real-time updates

**Tasks**:
- [ ] Choose text editor library (rich + prompt_toolkit)
- [ ] Implement text buffer (thread-safe)
- [ ] Create basic editor UI
- [ ] Integrate STT output into editor
- [ ] Add cursor management
- [ ] Add basic keyboard shortcuts (save, exit, etc.)

**Deliverable**: Text editor that displays STT output in real-time

---

### Phase 3: Simultaneous Editing
**Goal**: Allow keyboard editing while STT is active

**Tasks**:
- [ ] Implement keyboard input handler
- [ ] Thread-safe text buffer operations
- [ ] Handle cursor positioning during STT updates
- [ ] Prevent conflicts between STT and keyboard input
- [ ] Add visual indicators (STT active, editing mode)

**Deliverable**: Can type and edit while STT is transcribing

---

### Phase 4: LLM Cleanup Module
**Goal**: AI-powered error correction

**Tasks**:
- [ ] Set up LLM integration (Ollama recommended)
- [ ] Create cleanup prompt templates
- [ ] Implement cleanup trigger (keyboard shortcut + voice keyword)
- [ ] Send text to LLM with context
- [ ] Display diff (before/after)
- [ ] Accept/reject mechanism
- [ ] Batch cleanup option

**Deliverable**: Can trigger LLM to fix STT errors

---

### Phase 5: Polish & Features
**Goal**: Production-ready tool

**Tasks**:
- [ ] Configuration file (model selection, shortcuts, etc.)
- [ ] Audio level visualization
- [ ] Confidence indicators
- [ ] Multiple STT engine support (Whisper/Vosk)
- [ ] Save/load functionality
- [ ] Export options (txt, markdown, etc.)
- [ ] Error handling and recovery
- [ ] Documentation
- [ ] Example integrations

**Deliverable**: Complete, polished STT editor tool

---

## Configuration Options

```python
# config.py example
STT_ENGINE = "whisper"  # "whisper" or "vosk"
WHISPER_MODEL = "base"  # tiny, base, small, medium, large
VOSK_MODEL_PATH = "vosk-model-small-en-us-0.15"

AUDIO_DEVICE = None  # None = default, or device index
SAMPLE_RATE = 16000  # Whisper uses 16kHz
CHUNK_SIZE = 1024

CLEANUP_SHORTCUT = "ctrl+l"  # Keyboard shortcut
CLEANUP_KEYWORD = "cleanup"  # Voice keyword
CLEANUP_LLM = "ollama"  # "ollama", "openai", "gemini"
CLEANUP_MODEL = "llama3"  # Ollama model name

EDITOR_THEME = "dark"  # "dark" or "light"
AUTO_SAVE = True
SAVE_PATH = "./transcriptions/"
```

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+S` | Save current text |
| `Ctrl+L` | Trigger LLM cleanup |
| `Ctrl+C` | Copy text |
| `Ctrl+V` | Paste text |
| `Ctrl+Z` | Undo |
| `Ctrl+X` | Exit |
| `Ctrl+R` | Start/stop recording |
| `Ctrl+K` | Clear text |
| `Ctrl+/` | Show help |

---

## LLM Cleanup Prompts

### Basic Cleanup Prompt
```
You are a text cleanup assistant. The following text was generated by 
speech-to-text software and may contain errors. Please fix:

1. Homophones (there/their/they're, to/too/two, etc.)
2. Punctuation and capitalization
3. Grammar errors
4. Missing words
5. Context-appropriate corrections

Original text:
{text}

Return only the corrected text, no explanations.
```

### Advanced Cleanup Prompt (with context)
```
You are a text cleanup assistant. The following text was generated by 
speech-to-text software. The context is: {context}

Please fix common STT errors while preserving the original meaning and style.

Original text:
{text}

Return the corrected text in this format:
CORRECTED_TEXT: [your corrected text here]
```

---

## Integration with GlassSpector

Once this STT editor is complete, it can be integrated into GlassSpector:

1. **Replace current Vosk implementation** with the new STT engine
2. **Use the editor** for transcription display
3. **Add cleanup** to improve transcription quality before sending to LLM
4. **Reuse components** (audio input, STT engine) across both projects

**Benefits**:
- Better transcription quality
- Reusable components
- Cleaner codebase
- More features (editing, cleanup)

---

## Dependencies

```txt
# Core STT
faster-whisper>=1.0.0  # or openai-whisper
# Alternative: vosk>=0.3.45

# Audio
sounddevice>=0.4.6
numpy>=1.24.0

# Text Editor
rich>=13.0.0
prompt-toolkit>=3.0.0
# Alternative: textual>=0.40.0

# LLM
ollama>=0.1.0  # For local LLM
# Alternative: openai>=1.0.0, google-genai>=1.0.0

# Utilities
python-dotenv>=1.0.0
pyyaml>=6.0.0
```

---

## Testing Strategy

### Unit Tests
- STT engine transcription accuracy
- Text buffer thread safety
- Keyboard input handling
- LLM cleanup prompts

### Integration Tests
- STT → Editor flow
- Keyboard + STT simultaneous input
- LLM cleanup → Editor update
- Save/load functionality

### Manual Testing
- Real-world transcription accuracy
- Latency measurements
- User experience testing
- Different microphone qualities

---

## Success Metrics

1. **Accuracy**: >95% word accuracy on clear speech
2. **Latency**: <500ms from speech to text display
3. **Usability**: Can edit while transcribing without conflicts
4. **Cleanup**: LLM fixes >80% of common STT errors
5. **Performance**: Runs smoothly on mid-range hardware

---

## Future Enhancements

- [ ] Multi-language support
- [ ] Speaker diarization (identify different speakers)
- [ ] Real-time translation
- [ ] Voice commands (beyond cleanup)
- [ ] Cloud sync
- [ ] Mobile app version
- [ ] Web interface
- [ ] Plugin system
- [ ] Custom LLM prompts
- [ ] Batch processing mode

---

## Timeline Estimate

- **Phase 1**: 1-2 days (basic STT)
- **Phase 2**: 2-3 days (CLI editor)
- **Phase 3**: 1-2 days (simultaneous editing)
- **Phase 4**: 2-3 days (LLM cleanup)
- **Phase 5**: 2-3 days (polish)

**Total**: ~8-13 days for a complete, production-ready tool

---

## Next Steps

1. **Review this plan** and adjust as needed
2. **Set up project structure** in a new directory
3. **Start with Phase 1** - get basic STT working
4. **Iterate** through phases, testing as we go
5. **Integrate** into GlassSpector when ready

---

## Questions to Consider

1. **STT Engine**: Whisper (accuracy) vs Vosk (speed) - or both?
2. **Editor Library**: Rich + prompt_toolkit vs Textual vs custom?
3. **LLM**: Ollama (local) vs cloud API?
4. **Project Location**: Separate repo or subdirectory?
5. **License**: What license for reuse?

---

**Ready to start?** Let me know which phase you'd like to begin with, or if you want to adjust anything in this plan!

