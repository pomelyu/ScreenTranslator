"""Desktop GUI application for screen translation"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from PIL import ImageTk
import traceback
from .capture import ScreenCapture
from .api_client import TranslatorAPIClient


class ScreenTranslatorApp:
    """Main GUI application"""
    
    def __init__(self, root):
        """Initialize the application"""
        self.root = root
        self.root.title("Screen Translator")
        self.root.geometry("600x500")
        
        # Initialize components
        self.capture = ScreenCapture()
        self.api_client = TranslatorAPIClient()
        self.current_image = None
        self.windows_list = []
        self.capture_mode = "fullscreen"  # or "window"
        
        # Create UI
        self._create_ui()
        
        # Check server health on startup
        self.root.after(100, self._check_server)
        
    def _create_ui(self):
        """Create the user interface"""
        # Title
        title_label = tk.Label(
            self.root,
            text="Screen Translator",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)
        
        # Status frame
        status_frame = tk.Frame(self.root)
        status_frame.pack(fill=tk.X, padx=20)
        
        tk.Label(status_frame, text="Server Status:").pack(side=tk.LEFT)
        self.status_label = tk.Label(
            status_frame,
            text="Checking...",
            fg="gray"
        )
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Capture mode frame
        mode_frame = tk.LabelFrame(self.root, text="Capture Mode", padx=10, pady=10)
        mode_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Capture mode selection
        mode_select_frame = tk.Frame(mode_frame)
        mode_select_frame.pack(fill=tk.X)
        
        tk.Label(mode_select_frame, text="Mode:").pack(side=tk.LEFT)
        self.mode_var = tk.StringVar(value="fullscreen")
        
        tk.Radiobutton(
            mode_select_frame,
            text="Full Screen",
            variable=self.mode_var,
            value="fullscreen",
            command=self._on_mode_change
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Radiobutton(
            mode_select_frame,
            text="Select Window",
            variable=self.mode_var,
            value="window",
            command=self._on_mode_change
        ).pack(side=tk.LEFT, padx=5)
        
        # Window selection frame (initially hidden)
        self.window_frame = tk.Frame(mode_frame)
        
        tk.Label(self.window_frame, text="Window:").pack(side=tk.LEFT)
        self.window_var = tk.StringVar()
        self.window_combo = ttk.Combobox(
            self.window_frame,
            textvariable=self.window_var,
            state="readonly",
            width=30
        )
        self.window_combo.pack(side=tk.LEFT, padx=5)
        
        self.refresh_btn = tk.Button(
            self.window_frame,
            text="🔄 Refresh",
            command=self._refresh_windows
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Capture button
        capture_frame = tk.Frame(self.root)
        capture_frame.pack(pady=20)
        
        self.capture_btn = tk.Button(
            capture_frame,
            text="📸 Capture Full Screen",
            command=self._on_capture,
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=10
        )
        self.capture_btn.pack()
        
        # Settings frame
        settings_frame = tk.LabelFrame(self.root, text="Settings", padx=10, pady=10)
        settings_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Target language
        lang_frame = tk.Frame(settings_frame)
        lang_frame.pack(fill=tk.X)
        
        tk.Label(lang_frame, text="Target Language:").pack(side=tk.LEFT)
        self.target_lang_var = tk.StringVar(value="Traditional Chinese")
        self.target_lang_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.target_lang_var,
            values=["Traditional Chinese", "Simplified Chinese", "English", "Japanese", "Korean"],
            state="readonly",
            width=20
        )
        self.target_lang_combo.pack(side=tk.LEFT, padx=10)
        
        # Result frame
        result_frame = tk.LabelFrame(self.root, text="Translation Result", padx=10, pady=10)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Result text area
        self.result_text = scrolledtext.ScrolledText(
            result_frame,
            wrap=tk.WORD,
            font=("Arial", 11),
            height=10
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # Metrics label
        self.metrics_label = tk.Label(
            result_frame,
            text="",
            font=("Arial", 9),
            fg="gray",
            anchor="w"
        )
        self.metrics_label.pack(fill=tk.X, pady=(5, 0))
        
        # Copy button
        copy_btn = tk.Button(
            result_frame,
            text="📋 Copy to Clipboard",
            command=self._copy_to_clipboard
        )
        copy_btn.pack(pady=5)
        
    def _on_mode_change(self):
        """Handle capture mode change"""
        mode = self.mode_var.get()
        if mode == "window":
            self.window_frame.pack(fill=tk.X, pady=(10, 0))
            self._refresh_windows()
        else:
            self.window_frame.pack_forget()
    
    def _refresh_windows(self):
        """Refresh the list of available windows"""
        self.windows_list = self.capture.get_windows()
        
        if self.windows_list:
            window_titles = [f"{w['title']}" for w in self.windows_list]
            self.window_combo['values'] = window_titles
            if window_titles:
                self.window_combo.current(0)
        else:
            self.window_combo['values'] = ["No windows found"]
            messagebox.showwarning(
                "No Windows",
                "No windows found. Make sure wmctrl is installed:\nsudo apt-get install wmctrl"
            )
        
    def _check_server(self):
        """Check if backend server is running"""
        if self.api_client.check_health():
            self.status_label.config(text="✓ Connected", fg="green")
            self.capture_btn.config(state=tk.NORMAL)
        else:
            self.status_label.config(text="✗ Server not available", fg="red")
            self.capture_btn.config(state=tk.DISABLED)
            messagebox.showwarning(
                "Server Not Available",
                "Backend server is not running.\nPlease start the server first:\n\npython run_server.py"
            )
    
    def _on_capture(self):
        """Handle capture button click"""
        # Disable button during capture
        self.capture_btn.config(state=tk.DISABLED, text="Capturing...")
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "Capturing screenshot...\n")
        
        # Run capture in thread to avoid blocking UI
        thread = threading.Thread(target=self._capture_and_translate)
        thread.daemon = True
        thread.start()
    
    def _capture_and_translate(self):
        """Capture screenshot and send to server"""
        try:
            mode = self.mode_var.get()
            
            if mode == "window":
                # Capture selected window
                if not self.windows_list:
                    raise Exception("No windows available. Please refresh the window list.")
                
                selected_index = self.window_combo.current()
                if selected_index < 0 or selected_index >= len(self.windows_list):
                    raise Exception("Please select a window to capture.")
                
                selected_window = self.windows_list[selected_index]
                window_id = selected_window['id']
                
                # Update UI
                self.root.after(0, lambda: self.result_text.insert(tk.END, f"Capturing window: {selected_window['title']}...\n"))
                
                # Capture window
                self.current_image = self.capture.capture_window(window_id)
                
                if self.current_image is None:
                    raise Exception("Failed to capture window. Make sure wmctrl is installed.")
            else:
                # Capture full screen
                # Minimize window briefly to capture clean screenshot
                self.root.withdraw()
                self.root.after(300, lambda: None)  # Small delay
                self.root.update()
                
                import time
                time.sleep(0.3)  # Wait for window to minimize
                
                # Capture screenshot
                self.current_image = self.capture.capture_fullscreen()
                
                # Restore window
                self.root.deiconify()
            
            # Update UI
            self.root.after(0, lambda: self.result_text.insert(tk.END, "Screenshot captured!\nTranslating...\n"))
            
            # Send to server
            target_lang = self.target_lang_var.get()
            result = self.api_client.translate_image(
                self.current_image,
                target_lang=target_lang
            )
            
            # Update UI with result
            self.root.after(0, lambda: self._display_result(result))
            
        except Exception as e:
            traceback.print_exc()
            error_msg = str(e)  # Capture error message before lambda
            self.root.after(0, lambda msg=error_msg: self._display_error(msg))
        finally:
            self.root.after(0, lambda: self.capture_btn.config(
                state=tk.NORMAL,
                text="📸 Capture Full Screen"
            ))
    
    def _display_result(self, result):
        """Display translation result"""
        self.result_text.delete(1.0, tk.END)
        
        translated_text = result.get('translated_text', '')
        self.result_text.insert(tk.END, translated_text)
        
        # Display metrics
        processing_time = result.get('processing_time', 0)
        metrics = result.get('metrics', {})
        
        metrics_str = f"Processing time: {processing_time:.2f}s"
        if metrics.get('e2e_time'):
            metrics_str += f" | Model: {metrics['e2e_time']:.2f}s"
        if metrics.get('time_to_first_token'):
            metrics_str += f" | TTFT: {metrics['time_to_first_token']:.2f}s"
        
        self.metrics_label.config(text=metrics_str)
    
    def _display_error(self, error_msg):
        """Display error message"""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"Error: {error_msg}")
        self.metrics_label.config(text="")
        messagebox.showerror("Translation Error", error_msg)
    
    def _copy_to_clipboard(self):
        """Copy result to clipboard"""
        text = self.result_text.get(1.0, tk.END).strip()
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            messagebox.showinfo("Copied", "Text copied to clipboard!")
        else:
            messagebox.showwarning("No Text", "No text to copy!")
    
    def run(self):
        """Start the application"""
        self.root.mainloop()
        
    def cleanup(self):
        """Cleanup resources"""
        self.api_client.close()


def main():
    """Entry point for the desktop application"""
    root = tk.Tk()
    app = ScreenTranslatorApp(root)
    
    try:
        app.run()
    finally:
        app.cleanup()


if __name__ == "__main__":
    main()
