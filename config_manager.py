"""
Configuration Manager for Service Monitor
"""
import json
from pathlib import Path

class ConfigManager:
    """Manages configuration for the service monitoring system"""
    def __init__(self):
        self.config_file = Path('service_config.json')
        self.load_config()

    def load_config(self):
        """Load configuration from file or create default"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "default_config": {
                    "email": [],
                    "whatsapp": [],
                    "whatsapp_groups": []
                },
                "services": {}
            }
            self.save_config()

    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def get_service_config(self, service_name):
        """
        Get configuration for a specific service
        
        Args:
            service_name (str): The name of the service
            
        Returns:
            dict: Configuration for the service or default if not found
        """
        # Use the original service name for matching
        lower_service_name = service_name.lower()

        # Try to find matching service configuration
        for config_name in self.config['services']:
            if lower_service_name == config_name.lower():
                return self.config['services'][config_name]
        
        # Return default configuration if no match found
        return self.config['default_config']