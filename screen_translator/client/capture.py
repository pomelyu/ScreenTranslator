"""Screenshot capture module"""
import pyautogui
import subprocess
import tempfile
import os
from PIL import Image
from typing import Optional, Tuple, List, Dict
import sys
import mss
import mss.tools


class ScreenCapture:
    """Handle screenshot capture"""
    
    def __init__(self):
        """Initialize screen capture"""
        # Disable PyAutoGUI failsafe (move mouse to corner to abort)
        pyautogui.FAILSAFE = True
        self._platform = sys.platform
        
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
    
    def get_windows(self) -> List[Dict[str, any]]:
        """
        Get list of open windows
        
        Returns:
            List of dictionaries containing window info (id, title, geometry)
        """
        windows = []
        
        try:
            if self._platform.startswith('linux'):
                # Use wmctrl to list windows with geometry
                result = subprocess.run(
                    ['wmctrl', '-lG'],  # -G includes geometry
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split(None, 7)
                        if len(parts) >= 8:
                            window_id = parts[0]
                            x, y, width, height = map(int, parts[2:6])
                            window_title = parts[7]
                            # Filter out empty titles and desktop windows
                            if window_title and not window_title.startswith('Desktop'):
                                windows.append({
                                    'id': window_id,
                                    'title': window_title,
                                    'x': x,
                                    'y': y,
                                    'width': width,
                                    'height': height
                                })
            else:
                # Not supported on other platforms yet
                pass
                
        except (subprocess.CalledProcessError, FileNotFoundError):
            # wmctrl not available or failed
            pass
        
        return windows
    
    def capture_window(self, window_id: str) -> Optional[Image.Image]:
        """
        Capture a specific window by ID
        
        Args:
            window_id: Window ID from get_windows()
            
        Returns:
            PIL Image of the window, or None if failed
        """
        try:
            if self._platform.startswith('linux'):
                # Use ImageMagick's import command to capture the window
                # This is more reliable than mss for capturing X11 windows
                import tempfile
                import os
                
                # Create a temporary file for the screenshot
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                    tmp_path = tmp_file.name
                
                try:
                    # Use import command to capture window by ID
                    subprocess.run(
                        ['import', '-window', window_id, tmp_path],
                        capture_output=True,
                        text=True,
                        check=True,
                        timeout=5
                    )
                    
                    # Read the captured image
                    image = Image.open(tmp_path)
                    # Convert to RGB if needed
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    
                    return image
                finally:
                    # Clean up temporary file
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
            else:
                # Not supported on other platforms
                raise NotImplementedError("Window capture only supported on Linux")
                
        except (subprocess.CalledProcessError, FileNotFoundError, Exception) as e:
            print(f"Window capture failed: {str(e)}")
            # Failed to capture window
            return None
