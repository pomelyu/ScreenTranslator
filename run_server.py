"""Entry point to run the FastAPI server"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from screen_translator.server.api import run_server

if __name__ == "__main__":
    run_server()
