"""Screenshot capture module"""
import pyautogui
from PIL import Image
from typing import Optional, Tuple


class ScreenCapture:
    """Handle screenshot capture"""
    
    def __init__(self):
        """Initialize screen capture"""
        # Disable PyAutoGUI failsafe (move mouse to corner to abort)
        pyautogui.FAILSAFE = True
        
    def capture_fullscreen(self) -> Image.Image:
        """
        Capture full screen
        
        Returns:
            PIL Image of the screenshot
        """
        screenshot = pyautogui.screenshot()
        return screenshot
    
    def capture_region(self, x: int, y: int, width: int, height: int) -> Image.Image:
        """
        Capture a specific region of the screen
        
        Args:
            x: X coordinate of top-left corner
            y: Y coordinate of top-left corner
            width: Width of region
            height: Height of region
            
        Returns:
            PIL Image of the captured region
        """
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        return screenshot
    
    def get_screen_size(self) -> Tuple[int, int]:
        """
        Get screen dimensions
        
        Returns:
            Tuple of (width, height)
        """
        return pyautogui.size()
