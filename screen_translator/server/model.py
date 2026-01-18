"""vLLM model wrapper for Qwen3-VL"""
import os
from typing import Optional, Dict, Any
import torch
from vllm import LLM, SamplingParams
from transformers import AutoProcessor
from qwen_vl_utils import process_vision_info
from .config import Config


class Qwen3VLModel:
    """Wrapper for Qwen3-VL model using vLLM"""
    
    def __init__(self, config: Config):
        self.config = config
        self.model: Optional[LLM] = None
        self.processor = None
        
    def load(self):
        """Load the vLLM model and processor"""
        print(f"Loading model: {self.config.MODEL_NAME}")
        
        # Set environment variable for vLLM multiprocessing
        os.environ['VLLM_WORKER_MULTIPROC_METHOD'] = 'spawn'
        
        # Determine tensor parallel size
        tensor_parallel_size = self.config.TENSOR_PARALLEL_SIZE
        if tensor_parallel_size is None:
            tensor_parallel_size = torch.cuda.device_count()
            print(f"Auto-detected {tensor_parallel_size} GPUs")
        
        # Initialize vLLM model
        self.model = LLM(
            model=self.config.MODEL_NAME,
            trust_remote_code=True,
            gpu_memory_utilization=self.config.GPU_MEMORY_UTILIZATION,
            enforce_eager=False,
            tensor_parallel_size=tensor_parallel_size,
            seed=0
        )
        
        # Load processor
        self.processor = AutoProcessor.from_pretrained(self.config.MODEL_NAME)
        
        print("Model loaded successfully")
        
    def _prepare_inputs(self, messages: list) -> Dict[str, Any]:
        """Prepare inputs for vLLM inference"""
        # Apply chat template to get text prompt
        text = self.processor.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        # Process vision info (images/videos)
        image_inputs, video_inputs, video_kwargs = process_vision_info(
            messages,
            image_patch_size=self.processor.image_processor.patch_size,
            return_video_kwargs=True,
            return_video_metadata=True
        )
        
        # Prepare multimodal data
        mm_data = {}
        if image_inputs is not None:
            mm_data['image'] = image_inputs
        if video_inputs is not None:
            mm_data['video'] = video_inputs
        
        return {
            'prompt': text,
            'multi_modal_data': mm_data,
            'mm_processor_kwargs': video_kwargs
        }
    
    def translate(
        self,
        image_path: str,
        source_lang: str = "auto",
        target_lang: str = "en",
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Translate text in image to target language
        
        Args:
            image_path: Path to image file
            source_lang: Source language (auto-detect if "auto")
            target_lang: Target language code
            max_tokens: Maximum tokens to generate
            
        Returns:
            Translated text
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load() first.")
        
        # Create translation prompt
        if source_lang == "auto":
            prompt = f"Please detect the language in this image and translate all text to {target_lang}. Only provide the translated text, nothing else."
        else:
            prompt = f"Please translate all text in this image from {source_lang} to {target_lang}. Only provide the translated text, nothing else."
        
        # Prepare messages in Qwen3-VL format
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": f"file://{os.path.abspath(image_path)}"},
                    {"type": "text", "text": prompt}
                ]
            }
        ]
        
        # Prepare inputs for vLLM
        inputs = self._prepare_inputs(messages)
        
        # Set sampling parameters
        sampling_params = SamplingParams(
            max_tokens=max_tokens or self.config.MAX_TOKENS,
            temperature=self.config.TEMPERATURE
        )
        
        # Generate with vLLM
        outputs = self.model.generate(inputs, sampling_params=sampling_params)
        
        # Extract generated text
        if outputs and len(outputs) > 0 and len(outputs[0].outputs) > 0:
            return outputs[0].outputs[0].text.strip()
        
        return ""
