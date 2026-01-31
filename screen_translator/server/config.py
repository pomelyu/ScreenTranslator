"""Configuration for the backend server"""
import os
import yaml
from typing import Optional
import dataclasses
from pathlib import Path

@dataclasses.dataclass
class Config:
    """Server configuration"""
    
    # Model settings
    MODEL_NAME: str = os.getenv("MODEL_NAME", "Qwen/Qwen2-VL-2B-Instruct")
    GPU_MEMORY_UTILIZATION: float = float(os.getenv("GPU_MEMORY_UTILIZATION", "0.70"))
    MAX_MODEL_LEN: int = int(os.getenv("MAX_MODEL_LEN", "8196"))
    TENSOR_PARALLEL_SIZE: Optional[int] = None  # Auto-detect GPU count
    
    # Server settings
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # vLLM settings
    MAX_TOKENS: int = 1024
    TEMPERATURE: float = 0.7
    
    # Translation settings
    DEFAULT_SOURCE_LANG: str = "auto"
    DEFAULT_TARGET_LANG: str = "en"

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
            # Get the field type for validation
            field_type = None
            for field in dataclasses.fields(self):
                if field.name == key:
                    field_type = field.type
                    break
            
            # Type conversion/validation
            if field_type and value is not None:
                # Handle Optional types
                if hasattr(field_type, '__origin__') and field_type.__origin__ is type(Optional):
                    # Optional type, get the actual type
                    actual_type = field_type.__args__[0]
                    if not isinstance(value, actual_type):
                        try:
                            value = actual_type(value)
                        except (ValueError, TypeError) as e:
                            raise ValueError(f"Cannot convert {key}={value} to {actual_type.__name__}: {e}")
                elif not isinstance(value, field_type):
                    # Try to convert to the expected type
                    try:
                        value = field_type(value)
                    except (ValueError, TypeError) as e:
                        raise ValueError(f"Cannot convert {key}={value} to {field_type.__name__}: {e}")
            
            # Set the attribute
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
