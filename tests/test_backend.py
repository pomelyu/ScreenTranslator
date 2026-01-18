"""Test script for backend server"""
import base64
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from screen_translator.server.config import Config
from screen_translator.server.model import Qwen3VLModel


def test_model_loading():
    """Test 1: Load model"""
    print("=" * 50)
    print("TEST 1: Loading Qwen3-VL model with vLLM")
    print("=" * 50)
    
    config = Config()
    model = Qwen3VLModel(config)
    
    try:
        model.load()
        print("✓ Model loaded successfully")
        return model
    except Exception as e:
        print(f"✗ Failed to load model: {e}")
        raise


def test_translation(model: Qwen3VLModel, image_path: str):
    """Test 2: Translate image"""
    print("\n" + "=" * 50)
    print(f"TEST 2: Translating image: {image_path}")
    print("=" * 50)
    
    if not os.path.exists(image_path):
        print(f"✗ Image not found: {image_path}")
        return
    
    try:
        result = model.translate(
            image_path=image_path,
            source_lang="auto",
            target_lang="en"
        )
        print(f"✓ Translation successful")
        print(f"Result: {result}")
        return result
    except Exception as e:
        print(f"✗ Translation failed: {e}")
        raise


def test_with_base64(model: Qwen3VLModel, image_path: str):
    """Test 3: Test base64 encoding/decoding workflow"""
    print("\n" + "=" * 50)
    print(f"TEST 3: Testing base64 workflow")
    print("=" * 50)
    
    try:
        # Encode image to base64
        with open(image_path, 'rb') as f:
            image_data = f.read()
        encoded = base64.b64encode(image_data).decode('utf-8')
        print(f"✓ Image encoded to base64 ({len(encoded)} characters)")
        
        # Decode and save to temp file
        import tempfile
        from PIL import Image
        import io
        
        decoded = base64.b64decode(encoded)
        image = Image.open(io.BytesIO(decoded))
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
            image.save(tmp_file.name, format="PNG")
            tmp_path = tmp_file.name
        
        print(f"✓ Image decoded and saved to temp file")
        
        # Translate
        result = model.translate(
            image_path=tmp_path,
            source_lang="auto",
            target_lang="en"
        )
        
        # Cleanup
        os.unlink(tmp_path)
        
        print(f"✓ Base64 workflow successful")
        print(f"Result: {result}")
        return result
        
    except Exception as e:
        print(f"✗ Base64 workflow failed: {e}")
        raise


def main():
    """Run all tests"""
    print("Screen Translator Backend Tests")
    print("================================\n")
    
    # Find test images
    test_dir = Path(__file__).parent / "data"
    test_images = list(test_dir.glob("*.jpg")) + list(test_dir.glob("*.png"))
    
    if not test_images:
        print(f"✗ No test images found in {test_dir}")
        return
    
    print(f"Found {len(test_images)} test image(s):")
    for img in test_images:
        print(f"  - {img.name}")
    print()
    
    try:
        # Test 1: Load model
        model = test_model_loading()
        
        # Test 2 & 3: Translate each test image
        for image_path in test_images:
            test_translation(model, str(image_path))
            test_with_base64(model, str(image_path))
        
        print("\n" + "=" * 50)
        print("ALL TESTS PASSED ✓")
        print("=" * 50)
        
    except Exception as e:
        print("\n" + "=" * 50)
        print("TESTS FAILED ✗")
        print("=" * 50)
        sys.exit(1)


if __name__ == "__main__":
    main()
