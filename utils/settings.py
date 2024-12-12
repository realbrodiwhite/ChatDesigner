import os
import json
import jsonschema
from pathlib import Path

class Settings:
    """Settings manager for the FreeCAD AI Chat addon."""
    
    def __init__(self):
        self.addon_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_dir = os.path.join(self.addon_path, "config")
        self.default_settings_path = os.path.join(self.config_dir, "default_settings.json")
        self.user_settings_path = os.path.join(self.config_dir, "user_settings.json")
        
        # Load settings
        self.settings = self._load_settings()
        
    def _load_settings(self):
        """Load settings from files, creating user settings if needed."""
        # Load default settings
        with open(self.default_settings_path, 'r') as f:
            default_settings = json.load(f)
            
        # Create user settings if they don't exist
        if not os.path.exists(self.user_settings_path):
            with open(self.user_settings_path, 'w') as f:
                json.dump(default_settings, f, indent=4)
            return default_settings
            
        # Load and merge user settings
        with open(self.user_settings_path, 'r') as f:
            user_settings = json.load(f)
            
        # Merge with defaults (to ensure new settings are included)
        merged = self._merge_settings(default_settings, user_settings)
        return merged
        
    def _merge_settings(self, default, user):
        """Recursively merge user settings with defaults."""
        merged = default.copy()
        
        for key, value in user.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_settings(merged[key], value)
            else:
                merged[key] = value
                
        return merged
        
    def save(self):
        """Save current settings to user settings file."""
        os.makedirs(os.path.dirname(self.user_settings_path), exist_ok=True)
        with open(self.user_settings_path, 'w') as f:
            json.dump(self.settings, f, indent=4)
            
    def get(self, *keys):
        """Get a setting value using dot notation."""
        value = self.settings
        for key in keys:
            value = value[key]
        return value
        
    def set(self, value, *keys):
        """Set a setting value using dot notation."""
        target = self.settings
        for key in keys[:-1]:
            target = target[key]
        target[keys[-1]] = value
        self.save()
        
    def reset(self):
        """Reset settings to default."""
        if os.path.exists(self.user_settings_path):
            os.remove(self.user_settings_path)
        self.settings = self._load_settings()
        
    def get_ai_backend_config(self):
        """Get current AI backend configuration."""
        backend = self.get("ai_backend", "active_backend")
        return self.get("ai_backend", backend)
        
    def get_ui_config(self):
        """Get UI configuration."""
        return self.get("ui")
        
    def get_history_config(self):
        """Get history configuration."""
        return self.get("history")

# Create global settings instance
settings = Settings()
