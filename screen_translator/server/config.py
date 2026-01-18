"""Configuration for the backend server"""
import os
from typing import Optional


class Config:
    """Server configuration"""
    
    # Model settings
    MODEL_NAME: str = os.getenv("MODEL_NAME", "Qwen/Qwen2-VL-2B-Instruct")
    GPU_MEMORY_UTILIZATION: float = float(os.getenv("GPU_MEMORY_UTILIZATION", "0.70"))
    TENSOR_PARALLEL_SIZE: Optional[int] = None  # Auto-detect GPU count
    
    # Server settings
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # vLLM settings
    MAX_TOKENS: int = 1024
    TEMPERATURE: float = 0.7
    
    # Translation settings
    DEFAULT_SOURCE_LANG: str = "auto"
    DEFAULT_TARGET_LANG: str = "en"
