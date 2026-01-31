"""API client for backend communication"""
import base64
import requests
from io import BytesIO
from typing import Optional, Dict, Any
from PIL import Image
import time

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class TranslatorAPIClient:
    """Client for communicating with the translation backend"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize API client
        
        Args:
            base_url: Base URL of the backend server
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
    def check_health(self) -> bool:
        """
        Check if backend server is healthy
        
        Returns:
            True if server is healthy, False otherwise
        """
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def get_gemini_models(self, api_key: str) -> list[str]:
        """
        Get list of available Gemini models
        
        Args:
            api_key: Gemini API key
            
        Returns:
            List of model names that support generateContent
            
        Raises:
            Exception if fetching fails
        """
        if not GEMINI_AVAILABLE:
            raise Exception(
                "google-generativeai package not installed. "
                "Install it with: pip install google-generativeai"
            )
        
        try:
            # Configure Gemini
            genai.configure(api_key=api_key)
            
            # List all models
            models = genai.list_models()
            
            # Filter for models that support generateContent (vision + text)
            vision_models = []
            for model in models:
                # Check if model supports generateContent method
                if 'generateContent' in model.supported_generation_methods:
                    vision_models.append(model.name.replace('models/', ''))
            
            return sorted(vision_models)
            
        except Exception as e:
            raise Exception(f"Failed to fetch Gemini models: {str(e)}")
    
    def translate_image(
        self,
        image: Image.Image,
        source_lang: str = "auto",
        target_lang: str = "Traditional Chinese",
        max_tokens: Optional[int] = None,
        custom_prompt: Optional[str] = None,
        backend: str = "vllm",
        gemini_api_key: Optional[str] = None,
        gemini_model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Translate text in image
        
        Args:
            image: PIL Image to translate
            source_lang: Source language (default: auto-detect)
            target_lang: Target language
            max_tokens: Maximum tokens to generate
            custom_prompt: Custom prompt template (use ${TARGET_LANG} as placeholder)
            backend: Backend to use ("vllm" or "gemini")
            gemini_api_key: Gemini API key (required if backend="gemini")
            gemini_model: Gemini model name (e.g., "gemini-1.5-flash")
            
        Returns:
            Dictionary containing translation result and metrics
            
        Raises:
            Exception if translation fails
        """
        if backend == "gemini":
            return self._translate_with_gemini(
                image, target_lang, custom_prompt, gemini_api_key, gemini_model
            )
        else:
            return self._translate_with_vllm(
                image, source_lang, target_lang, max_tokens, custom_prompt
            )
    
    def _translate_with_vllm(
        self,
        image: Image.Image,
        source_lang: str,
        target_lang: str,
        max_tokens: Optional[int],
        custom_prompt: Optional[str]
    ) -> Dict[str, Any]:
        """
        Translate using vLLM backend server
        """
        # Convert image to base64
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        image_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        # Prepare request
        payload = {
            "image": image_b64,
            "source_lang": source_lang,
            "target_lang": target_lang
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        if custom_prompt:
            payload["custom_prompt"] = custom_prompt
        
        # Send request
        response = self.session.post(
            f"{self.base_url}/translate",
            json=payload,
            timeout=120  # 2 minute timeout
        )
        
        # Check response
        if response.status_code == 200:
            return response.json()
        else:
            error_msg = f"Translation failed: {response.status_code}"
            try:
                error_detail = response.json().get('detail', response.text)
                error_msg = f"{error_msg} - {error_detail}"
            except:
                pass
            raise Exception(error_msg)
    
    def _translate_with_gemini(
        self,
        image: Image.Image,
        target_lang: str,
        custom_prompt: Optional[str],
        api_key: Optional[str],
        model_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Translate using Google Gemini API
        """
        if not GEMINI_AVAILABLE:
            raise Exception(
                "google-generativeai package not installed. "
                "Install it with: pip install google-generativeai"
            )
        
        if not api_key:
            raise Exception("Gemini API key is required")
        
        # Use default model if not specified
        if not model_name:
            model_name = "gemini-1.5-flash"
        
        try:
            # Configure Gemini
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name)
            
            # Prepare prompt
            if custom_prompt:
                prompt = custom_prompt.replace("${TARGET_LANG}", target_lang)
            else:
                prompt = f"Please detect the language in this image and translate all text to {target_lang}. Only provide the translated text, nothing else."
            
            # Generate response
            start_time = time.perf_counter()
            response = model.generate_content([prompt, image])
            processing_time = time.perf_counter() - start_time
            
            # Extract text
            translated_text = response.text if hasattr(response, 'text') else str(response)
            
            return {
                "translated_text": translated_text,
                "detected_lang": None,
                "success": True,
                "processing_time": processing_time,
                "metrics": {
                    "backend": "gemini",
                    "model": model_name
                }
            }
            
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def close(self):
        """Close the session"""
        self.session.close()
