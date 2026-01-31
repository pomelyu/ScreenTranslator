# Screen Translator Desktop Client

Desktop application for capturing screenshots and translating on-screen text.

## Setup

### Install Dependencies

```bash
cd screen_translator/client
pip install -r requirements.txt
```

Or install individually:
```bash
pip install pyautogui pillow requests
```

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
