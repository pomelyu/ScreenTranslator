"""API client for backend communication"""
import base64
import requests
from io import BytesIO
from typing import Optional, Dict, Any
from PIL import Image


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
    
    def translate_image(
        self,
        image: Image.Image,
        source_lang: str = "auto",
        target_lang: str = "Traditional Chinese",
        max_tokens: Optional[int] = None,
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Translate text in image
        
        Args:
            image: PIL Image to translate
            source_lang: Source language (default: auto-detect)
            target_lang: Target language
            max_tokens: Maximum tokens to generate
            custom_prompt: Custom prompt template (use ${TARGET_LANG} as placeholder)
            
        Returns:
            Dictionary containing translation result and metrics
            
        Raises:
            Exception if translation fails
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
    
    def close(self):
        """Close the session"""
        self.session.close()
