import yaml
from pathlib import Path
from typing import Dict, Any

class Config:
    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """Load configuration from config.yaml file."""
        config_path = Path(__file__).parent.parent.parent / 'config.yaml'
        try:
            with open(config_path, 'r') as file:
                self._config = yaml.safe_load(file)
        except Exception as e:
            raise Exception(f"Error loading config file: {str(e)}")

    @property
    def models(self) -> Dict[str, Any]:
        """Get AI models configuration."""
        return self._config.get('models', {})

    @property
    def ui(self) -> Dict[str, Any]:
        """Get UI configuration."""
        return self._config.get('ui', {})

    @property
    def scoring(self) -> Dict[str, Any]:
        """Get scoring configuration."""
        return self._config.get('scoring', {})

    @property
    def file_types(self) -> Dict[str, Any]:
        """Get file types configuration."""
        return self._config.get('file_types', {})

    @property
    def scraping(self) -> Dict[str, Any]:
        """Get web scraping configuration."""
        return self._config.get('scraping', {})

    def get_model_config(self, model_name: str) -> Dict[str, Any]:
        """Get configuration for a specific model."""
        return self.models.get(model_name, {})

    def get_mime_type(self, file_ext: str) -> str:
        """Get mime type for a file extension."""
        return self.file_types.get('mime_types', {}).get(file_ext)

    def is_allowed_file_type(self, file_ext: str) -> bool:
        """Check if file type is allowed."""
        return file_ext in self.file_types.get('allowed', [])

    def get_score_color(self, score: float) -> str:
        """Get color based on score thresholds."""
        thresholds = self.scoring.get('thresholds', {})
        colors = self.scoring.get('colors', {})
        
        if score >= thresholds.get('high', 7):
            return colors.get('high', 'green')
        elif score >= thresholds.get('medium', 5):
            return colors.get('medium', 'orange')
        return colors.get('low', 'red')

# Create a singleton instance
config = Config()
