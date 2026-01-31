"""FastAPI server for screen translation"""
import argparse
import base64
import io
import os
import os.path
import tempfile
import time
from typing import Any
from typing import Dict
from typing import Optional

import uvicorn
from fastapi import FastAPI
from fastapi import HTTPException
from PIL import Image
from pydantic import BaseModel

from .config import Config
from .model import Qwen3VLModel


# Request/Response models
class TranslateRequest(BaseModel):
    """Translation request"""
    image: str  # base64-encoded image
    source_lang: Optional[str] = "auto"
    target_lang: Optional[str] = "en"
    max_tokens: Optional[int] = None
    custom_prompt: Optional[str] = None  # Custom prompt with ${TARGET_LANG} placeholder


class TranslateResponse(BaseModel):
    """Translation response"""
    translated_text: str
    detected_lang: Optional[str] = None
    processing_time: float  # Total API processing time (seconds)
    success: bool = True
    metrics: Optional[Dict[str, Any]] = None  # vLLM internal metrics (e2e_time, time_to_first_token, etc.)


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    model: str


class ServerApp():
    def __init__(self, config_yaml_path: str):
        # Initialize FastAPI app
        self.app = FastAPI(title="Screen Translator API", version="1.0.0")

        # Global model instance
        self.config = Config()

        # Try to load config from yaml file if it exists
        if os.path.exists(config_yaml_path):
            try:
                print(f"Loading configuration from {config_yaml_path}")
                self.config.load_yaml(config_yaml_path)
                print("Configuration loaded successfully")
            except Exception as e:
                print(f"Warning: Failed to load config.yaml: {e}")
                print("Using default configuration")

        self.model = Qwen3VLModel(self.config)

        self.app.on_event("startup")(self.startup_event)
        self.app.get("/health", response_model=HealthResponse)(self.health_check)
        self.app.post("/translate", response_model=TranslateResponse)(self.translate)
        self.app.get("/")(self.root)

    def run(self):
        """Run the FastAPI server"""

        uvicorn.run(
            self.app,
            host=self.config.HOST,
            port=self.config.PORT,
            log_level="info"
        )

    async def startup_event(self):
        """Load model on startup"""
        print("Starting up server...")
        self.model.load()
        print("Server ready!")

    async def health_check(self):
        """Health check endpoint"""
        return HealthResponse(
            status="healthy",
            model=self.config.MODEL_NAME
        )

    async def translate(self, request: TranslateRequest):
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
                # Perform translation and measure wall-clock time
                start_time = time.perf_counter()
                
                translated_text, vllm_metrics = self.model.translate(
                    image_path=tmp_path,
                    source_lang=request.source_lang or self.config.DEFAULT_SOURCE_LANG,
                    target_lang=request.target_lang or self.config.DEFAULT_TARGET_LANG,
                    max_tokens=request.max_tokens
                )
                
                processing_time = time.perf_counter() - start_time
                
                return TranslateResponse(
                    translated_text=translated_text,
                    detected_lang=None,  # TODO: Add language detection
                    processing_time=processing_time,
                    success=True,
                    metrics=vllm_metrics
                )
            finally:
                # Clean up temp file
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                    
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

    async def root(self):
        """Root endpoint"""
        return {
            "message": "Screen Translator API",
            "version": "1.0.0",
            "endpoints": {
                "health": "/health",
                "translate": "/translate (POST)"
            }
        }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", "-c", type=str, help="path to config file", default="")
    args = parser.parse_args()

    app = ServerApp(args.config)
    app.run()
