import dataclasses
import yaml
from pathlib import Path
from typing import Optional

@dataclasses.dataclass
class ScreenTranslatorConfig():
    capture_mode: str = "window"  # or "fullscreen"
    backend: str = "gemini" # or "vllm"
    prompt: str = """
        Translate dialog text in this image to ${TARGET_LANG}. 
        Output the result in the format: translated text(original text). 
        For example: 當然，未來也是(もちろん、将来も…). Only output the dialog and translated results.
    """

    # For gemini backend
    gemini_model: str = "gemini-2.5-flash-image"
    gemini_key: str = ""
    
    def load_yaml(self, file_path: str):
        """
        Load configuration from YAML file
        
        Args:
            file_path: Path to YAML configuration file
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If YAML contains invalid keys
            yaml.YAMLError: If YAML parsing fails
        """
        yaml_path = Path(file_path)
        
        if not yaml_path.exists():
            raise FileNotFoundError(f"Config file not found: {file_path}")
        
        # Load YAML file
        with open(yaml_path, 'r') as f:
            try:
                config_data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise yaml.YAMLError(f"Failed to parse YAML config: {e}")
        
        if not config_data:
            return  # Empty file, nothing to update
        
        if not isinstance(config_data, dict):
            raise ValueError("YAML config must be a dictionary")
        
        # Get valid field names from dataclass
        valid_fields = {f.name for f in dataclasses.fields(self)}
        
        # Check for invalid keys
        invalid_keys = set(config_data.keys()) - valid_fields
        if invalid_keys:
            raise ValueError(
                f"Invalid configuration keys: {', '.join(sorted(invalid_keys))}\n"
                f"Valid keys are: {', '.join(sorted(valid_fields))}"
            )
        
        # Update dataclass fields with values from YAML
        for key, value in config_data.items():
            if value is not None:
                setattr(self, key, value)
    
    def save_yaml(self, file_path: str):
        """
        Save current configuration to YAML file
        
        Args:
            file_path: Path where to save the YAML configuration
        """
        config_dict = dataclasses.asdict(self)
        
        yaml_path = Path(file_path)
        yaml_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(yaml_path, 'w') as f:
            yaml.safe_dump(config_dict, f, default_flow_style=False, sort_keys=False)
