# Screen Translator Desktop Client

Desktop application for capturing screenshots and translating text using either vLLM backend or Gemini API.

## Features

- **Full screen or window capture**
- **Multiple backends**: Choose between local vLLM server or Google Gemini API
- **Customizable prompts** with language placeholder
- **Dynamic model selection** for Gemini
- **YAML configuration** for persistent settings

## Setup

### 1. Install Dependencies

```bash
cd screen_translator/client
pip install -r requirements.txt
```

Or install individually:
```bash
pip install pyautogui pillow requests mss google-generativeai PyYAML
```

### 2. Configuration

The client automatically loads and saves configuration from `client_config.yaml` in the project root.

**Create your config** (optional):
```bash
cp client_config.example.yaml client_config.yaml
# Edit client_config.yaml with your preferences
```

**Configuration options**:
- `capture_mode`: "window" or "fullscreen"
- `backend`: "gemini" or "vllm"
- `prompt`: Custom prompt template (use ${TARGET_LANG} placeholder)
- `gemini_model`: Preferred Gemini model (e.g., "gemini-2.0-flash-exp")
- `gemini_key`: Your Gemini API key (optional, can enter in UI)

**Example config**:
```yaml
capture_mode: window
backend: gemini
prompt: Please detect the language in this image and translate all text to ${TARGET_LANG}. Only provide the translated text, nothing else.
gemini_model: gemini-2.0-flash-exp
gemini_key: ''  # Leave empty to enter in UI
```

The app automatically saves your settings when you close it.

## Usage

### Start the Application

From project root:
```bash
python run_client.py
```

Or directly:
```bash
python screen_translator/client/main.py
```

### Using the App

1. **Check Server Status** - The app will check if the backend server is running
2. **Select Target Language** - Choose from Traditional Chinese, Simplified Chinese, English, Japanese, or Korean
3. **Capture Screenshot** - Click the "📸 Capture Full Screen" button
4. **View Translation** - The translated text will appear in the result area
5. **Copy Result** - Use the "📋 Copy to Clipboard" button to copy the translation

## Features

- ✓ Full screen capture
- ✓ Multiple target language support
- ✓ Real-time server health checking
- ✓ Processing time and metrics display
- ✓ Copy to clipboard functionality
- ✓ Clean, simple UI

## Requirements

- Backend server must be running (see `screen_translator/server/README.md`)
- PyAutoGUI for screenshot capture
- tkinter (included with Python)

## Architecture

- **capture.py** - Screenshot capture using PyAutoGUI
- **api_client.py** - Backend API communication
- **main.py** - GUI application with tkinter

## Future Enhancements

- Region selection for partial screen capture
- Hotkey support for quick capture
- Translation history
- Multiple display support
- Overlay display mode
