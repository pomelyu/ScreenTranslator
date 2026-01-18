# Real-time Screen Translator POC - Implementation Plan

## Project Overview

Build a minimum viable POC for a real-time screen translator service consisting of:
- **Backend Server**: vLLM + Qwen3VL-2B/4B for vision-language model inference
- **Desktop Client**: Screenshot capture and translation query/display

## Current Workspace State

- **Status**: Clean slate - empty `screen_translator/` directory
- **Configuration**: Only `setup.cfg` with isort settings
- **Ready for**: Greenfield development with structured architecture

## Architecture Design

### Backend Server (vLLM + Qwen3VL)

**Technology Stack:**
- vLLM (inference engine with OpenAI-compatible API)
- FastAPI (REST API framework)
- Qwen3VL-2B or 4B (vision-language model)
- Uvicorn (ASGI server)

**Core Components:**
1. Model serving layer with vLLM
2. REST API endpoints:
   - `POST /translate` - Accept image + language params, return translated text
   - `GET /health` - Server health check
3. Image processing pipeline:
   - Decode base64-encoded images
   - Validate and preprocess
   - Pass to Qwen3VL with translation prompts
   - Return JSON response

**Dependencies:**
```
vllm>=0.3.0
transformers>=4.36.0
fastapi>=0.100.0
uvicorn>=0.23.0
pillow>=10.0.0
torch>=2.1.0 (with CUDA support)
```

**GPU Requirements:**
- Qwen3VL-2B: ~8GB VRAM minimum
- Qwen3VL-4B: ~16GB VRAM minimum

### Desktop Client

**Technology Stack:**
- `mss` (fast cross-platform screenshots - preferred over PyAutoGUI)
- `requests` (HTTP client for API communication)
- `pynput` (global hotkey binding)
- `tkinter` (minimal UI - built-in with Python)

**Core Components:**
1. Screenshot capture (full screen or region selection)
2. API client for backend communication
3. Hotkey binding for quick capture
4. Result display (popup/overlay window)

**Dependencies:**
```
mss>=9.0.0
requests>=2.31.0
pillow>=10.0.0
pynput>=1.7.6
```

### Communication Protocol

**REST API with JSON:**

Request format:
```json
{
  "image": "base64_encoded_string",
  "source_lang": "auto",
  "target_lang": "en"
}
```

Response format:
```json
{
  "translated_text": "Hello world",
  "detected_lang": "zh",
  "confidence": 0.95
}
```

**Image Encoding:**
- Format: PNG (lossless) or JPEG (compressed)
- Transmission: Base64-encoded in JSON payload
- Size consideration: ~33% overhead with base64, but simplifies handling

## Project Structure

```
screen_translator/
├── server/
│   ├── __init__.py
│   ├── api.py           # FastAPI endpoints
│   ├── model.py         # vLLM/Qwen3VL wrapper
│   ├── config.py        # Server configuration
│   └── requirements.txt
├── client/
│   ├── __init__.py
│   ├── capture.py       # Screenshot logic with mss
│   ├── api_client.py    # Backend communication
│   ├── main.py          # Entry point + UI
│   └── requirements.txt
└── tests/
    └── test_integration.py
```

## Implementation Steps

### Phase 1: Backend Development

1. **Verify vLLM + Qwen3VL compatibility**
   - Test model loading with sample script
   - Verify vision input support in vLLM
   - Fallback: Use HuggingFace `transformers` directly if needed

2. **Set up FastAPI server**
   - Create `POST /translate` endpoint
   - Implement image decoding and validation
   - Add error handling and logging

3. **Integrate Qwen3VL model**
   - Load model with vLLM
   - Craft effective translation prompts
   - Test inference with sample images

4. **Test backend standalone**
   - Use curl/Postman to test endpoints
   - Measure inference latency
   - Validate translation quality

### Phase 2: Client Development

1. **Implement screenshot capture**
   - Use `mss` for fast capture
   - Add region selection logic
   - Handle multi-monitor scenarios

2. **Build API client**
   - Encode screenshots to base64
   - Send POST requests to backend
   - Parse and handle responses
   - Add retry logic and error handling

3. **Create minimal UI**
   - Tkinter for region selection overlay
   - Display translation results (popup window)
   - Add copy-to-clipboard functionality

4. **Implement hotkey binding**
   - Use `pynput` for global hotkeys
   - Bind common shortcuts (e.g., Ctrl+Shift+T)
   - Handle conflicts gracefully

### Phase 3: Integration & Testing

1. **End-to-end testing**
   - Test full workflow: capture → translate → display
   - Measure total latency (target: 1-4 seconds)
   - Test various languages and content types

2. **Performance optimization**
   - Image compression/resizing if needed
   - Batch requests (if applicable)
   - Cache common translations

3. **Error handling**
   - Network failures
   - Model errors
   - Invalid screenshots

## Technical Considerations & Decisions

### Critical Decisions to Make

1. **Model Selection**: Qwen3VL-2B (faster, less VRAM) vs 4B (better quality, more VRAM)?
   - Recommendation: Start with 2B for POC, upgrade if quality insufficient

2. **vLLM Compatibility**: Does vLLM support Qwen3VL natively?
   - Action: Test early with verification script
   - Fallback: Use `transformers` library directly

3. **Deployment Model**: Local (same machine) vs Remote (GPU server)?
   - Recommendation: Local for POC to minimize latency and simplify setup

4. **UI Framework**: Tkinter (simple) vs PyQt5 (feature-rich)?
   - Recommendation: Tkinter for MVP simplicity

5. **Screenshot Library**: PyAutoGUI vs mss?
   - Recommendation: mss (faster, ~10-50ms vs 100-300ms)

### Performance Expectations

**Latency breakdown:**
- Screenshot capture: 10-50ms (with mss)
- Image encoding: 10-50ms
- Network transmission: 50-200ms (local), 100-500ms (remote)
- Model inference: 500-3000ms (GPU-dependent)
- **Total expected: 1-4 seconds per translation**

**Optimization opportunities:**
- Image compression (JPEG with quality 80-90)
- Resolution downscaling (max 1920px width)
- Model quantization (if supported by vLLM)

### Potential Challenges

1. **vLLM Vision Support**: May not support all VL models yet
   - Mitigation: Have transformers fallback ready

2. **Cross-platform Compatibility**: Linux X11/Wayland, multi-monitor
   - Mitigation: Test on target platform early

3. **Translation Quality**: Model may need prompt engineering
   - Mitigation: Iterate on prompts with test cases

4. **Memory Management**: Model loading requires significant VRAM
   - Mitigation: Use appropriate model size for available GPU

## Success Criteria for POC

### Minimum Viable Features

- ✓ Capture screenshot of selected region
- ✓ Send to backend API
- ✓ Receive translated text
- ✓ Display result to user
- ✓ Basic error handling

### Performance Targets

- Latency: < 5 seconds per translation
- Accuracy: Subjectively acceptable for common languages
- Stability: Handles 10+ consecutive translations without crashes

### Nice-to-Have (Post-POC)

- Language auto-detection
- Translation history/caching
- Multiple UI themes
- OCR fallback for poor quality images
- Batch translation mode
- Clipboard monitoring mode

## Next Actions

1. Set up Python environment (conda/venv)
2. Create project structure (directories + `__init__.py` files)
3. Set up dependency files (requirements.txt for server + client)
4. Write vLLM compatibility test script
5. Begin backend implementation
6. Iterate based on test results

## Notes & References

- **Model Hub**: Qwen/Qwen2-VL-2B-Instruct on HuggingFace
- **vLLM Docs**: https://docs.vllm.ai/
- **mss Library**: https://python-mss.readthedocs.io/
- **Alternative to consider**: If vLLM proves difficult, consider using Ollama with vision models as simpler alternative
