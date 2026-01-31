# Screen Translator Backend Server

Backend server for real-time screen translation using vLLM and Qwen3-VL.

## Setup

### 1. Install Dependencies

```bash
cd screen_translator/server
pip install -r requirements.txt
```

### 2. GPU Requirements

- **Qwen2-VL-2B**: ~8GB VRAM minimum
- **Qwen2-VL-4B**: ~16GB VRAM minimum
- CUDA-capable NVIDIA GPU required

### 3. Test the Backend

Run the test script to verify model loading and translation:

```bash
python test_backend.py
```

This will:
- Load the Qwen3-VL model with vLLM
- Test translation on images in `tests/data/`
- Verify base64 encoding/decoding workflow

### 4. Start the Server

```bash
python api.py
```

Or use uvicorn directly:

```bash
uvicorn api:app --host 127.0.0.1 --port 8000
```

## API Endpoints

### Health Check

```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "model": "Qwen/Qwen2-VL-2B-Instruct"
}
```

### Translate

```bash
POST /translate
Content-Type: application/json

{
  "image": "base64_encoded_image_string",
  "source_lang": "auto",
  "target_lang": "en",
  "max_tokens": 1024
}
```

Response:
```json
{
  "translated_text": "Hello, world!",
  "detected_lang": null,
  "success": true
}
```

## Configuration

### 1. Environment Variables

```bash
MODEL_NAME="Qwen/Qwen2-VL-2B-Instruct"  # or Qwen2-VL-4B
GPU_MEMORY_UTILIZATION="0.70"
HOST="127.0.0.1"
PORT="8000"
```

### 2. YAML Configuration File (Recommended)

Create a `config.yaml` file in the project root:

```bash
cp config.example.yaml config.yaml
# Edit config.yaml with your settings
python run_server.py
```

The YAML configuration will automatically be loaded if the file exists. YAML settings override environment variables.

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `MODEL_NAME` | string | `Qwen/Qwen2-VL-2B-Instruct` | HuggingFace model identifier |
| `GPU_MEMORY_UTILIZATION` | float | `0.70` | GPU memory utilization (0.0-1.0) |
| `MAX_MODEL_LEN` | int | `8196` | Maximum model context length |
| `TENSOR_PARALLEL_SIZE` | int | auto-detect | Number of GPUs for tensor parallelism |
| `HOST` | string | `127.0.0.1` | Server host address |
| `PORT` | int | `8000` | Server port |
| `MAX_TOKENS` | int | `1024` | Maximum tokens to generate |
| `TEMPERATURE` | float | `0.7` | Sampling temperature |
| `DEFAULT_SOURCE_LANG` | string | `auto` | Default source language |
| `DEFAULT_TARGET_LANG` | string | `Traditional Chinese` | Default target language |

## Testing with curl

```bash
# Health check
curl http://localhost:8000/health

# Translate an image
base64_image=$(base64 -w 0 tests/data/screenshot1.jpg)
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d "{\"image\": \"$base64_image\", \"target_lang\": \"en\"}"
```

## Architecture

- **api.py**: FastAPI server with endpoints
- **model.py**: vLLM wrapper for Qwen3-VL
- **config.py**: Configuration settings
- **test_backend.py**: Standalone test script
