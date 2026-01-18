"""FastAPI server for screen translation"""
import base64
import io
import tempfile
import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from PIL import Image

from .config import Config
from .model import Qwen3VLModel


# Request/Response models
class TranslateRequest(BaseModel):
    """Translation request"""
    image: str  # base64-encoded image
    source_lang: Optional[str] = "auto"
    target_lang: Optional[str] = "en"
    max_tokens: Optional[int] = None


class TranslateResponse(BaseModel):
    """Translation response"""
    translated_text: str
    detected_lang: Optional[str] = None
    success: bool = True


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    model: str


# Initialize FastAPI app
app = FastAPI(title="Screen Translator API", version="1.0.0")

# Global model instance
config = Config()
model = Qwen3VLModel(config)


@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    print("Starting up server...")
    model.load()
    print("Server ready!")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        model=config.MODEL_NAME
    )


@app.post("/translate", response_model=TranslateResponse)
async def translate(request: TranslateRequest):
    """
    Translate text in image
    
    Args:
        request: Translation request with base64-encoded image
        
    Returns:
        Translation response with translated text
    """
    try:
        # Decode base64 image
        try:
            image_data = base64.b64decode(request.image)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid base64 image: {str(e)}")
        
        # Validate image
        try:
            image = Image.open(io.BytesIO(image_data))
            image.verify()
            image = Image.open(io.BytesIO(image_data))  # Re-open after verify
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image format: {str(e)}")
        
        # Save to temporary file (vLLM requires file path)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
            image.save(tmp_file.name, format="PNG")
            tmp_path = tmp_file.name
        
        try:
            # Perform translation
            translated_text = model.translate(
                image_path=tmp_path,
                source_lang=request.source_lang or config.DEFAULT_SOURCE_LANG,
                target_lang=request.target_lang or config.DEFAULT_TARGET_LANG,
                max_tokens=request.max_tokens
            )
            
            return TranslateResponse(
                translated_text=translated_text,
                detected_lang=None,  # TODO: Add language detection
                success=True
            )
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Screen Translator API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "translate": "/translate (POST)"
        }
    }


def run_server():
    """Run the FastAPI server"""
    import uvicorn
    uvicorn.run(
        app,
        host=config.HOST,
        port=config.PORT,
        log_level="info"
    )


if __name__ == "__main__":
    run_server()
