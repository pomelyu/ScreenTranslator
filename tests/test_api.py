"""Test FastAPI endpoints"""
import base64
import json
import time
import requests
from pathlib import Path

API_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("=" * 60)
    print("TEST: Health Check")
    print("=" * 60)
    
    response = requests.get(f"{API_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_translate(image_path: str, target_lang: str = "en"):
    """Test translate endpoint"""
    print("=" * 60)
    print(f"TEST: Translate {Path(image_path).name}")
    print("=" * 60)
    
    # Read and encode image
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    image_b64 = base64.b64encode(image_data).decode('utf-8')
    print(f"Image size: {len(image_data)} bytes")
    print(f"Base64 size: {len(image_b64)} characters")
    
    # Send request
    payload = {
        "image": image_b64,
        "source_lang": "auto",
        "target_lang": target_lang
    }
    
    print(f"Sending request to {API_URL}/translate...")
    start_time = time.time()
    
    response = requests.post(
        f"{API_URL}/translate",
        json=payload,
        timeout=120  # 2 minute timeout
    )
    
    elapsed = time.time() - start_time
    
    print(f"Status Code: {response.status_code}")
    print(f"Latency: {elapsed:.2f} seconds")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ Translation successful!")
        print(f"Translated text: {result['translated_text']}")
        print(f"Detected language: {result.get('detected_lang', 'N/A')}")
        print(f"Server processing time: {result.get('processing_time', 0):.3f}s")
        
        # Display vLLM metrics if available
        if result.get('metrics'):
            print(f"\nvLLM Metrics:")
            metrics = result['metrics']
            if metrics.get('e2e_time'):
                print(f"  - E2E time: {metrics['e2e_time']:.3f}s")
            if metrics.get('time_to_first_token'):
                print(f"  - Time to first token: {metrics['time_to_first_token']:.3f}s")
            if metrics.get('time_per_output_token'):
                print(f"  - Time per output token: {metrics['time_per_output_token']:.4f}s")
            if metrics.get('time_in_queue'):
                print(f"  - Time in queue: {metrics['time_in_queue']:.3f}s")
        print(f"Server processing time: {result.get('processing_time', 'N/A'):.2f} seconds")
    else:
        print(f"\n✗ Translation failed!")
        print(f"Error: {response.text}")
    
    print()
    return response

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("FastAPI Server Tests")
    print("=" * 60 + "\n")
    
    # Test 1: Health check
    try:
        test_health()
    except Exception as e:
        print(f"✗ Health check failed: {e}\n")
        return
    
    # Test 2: Translate test images
    test_dir = Path("tests/data")
    test_images = sorted(test_dir.glob("*.jpg"))
    
    print(f"Found {len(test_images)} test image(s)\n")
    
    for image_path in test_images:
        try:
            test_translate(str(image_path))
        except Exception as e:
            print(f"✗ Translation failed: {e}\n")
    
    print("=" * 60)
    print("Phase 1 Tests Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
