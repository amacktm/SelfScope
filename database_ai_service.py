"""
Database-backed AI configuration service
"""
import logging
from models import db, AIConfiguration
from local_ai_service import LocalAIService

class DatabaseAIService:
    def __init__(self):
        self.local_ai = LocalAIService()
        self.load_configuration()
    
    def load_configuration(self):
        """Load AI configuration from database"""
        try:
            config = AIConfiguration.query.filter_by(is_active=True).first()
            if config:
                # Apply database configuration to local AI service
                self.local_ai.config.update(config.to_dict())
                self.local_ai.check_available_services()
                logging.info(f"Loaded AI configuration: {config.endpoint_type}")
            else:
                # Create default configuration
                self.create_default_configuration()
        except Exception as e:
            logging.error(f"Error loading AI configuration: {str(e)}")
            self.create_default_configuration()
    
    def create_default_configuration(self):
        """Create default AI configuration"""
        try:
            default_config = AIConfiguration(
                endpoint_type='rule_based',
                ollama_url='http://localhost:11434',
                lm_studio_url='http://localhost:1234/v1',
                is_active=True
            )
            db.session.add(default_config)
            db.session.commit()
            logging.info("Created default AI configuration")
        except Exception as e:
            logging.error(f"Error creating default configuration: {str(e)}")
            db.session.rollback()
    
    def save_configuration(self, config_data):
        """Save AI configuration to database"""
        try:
            # Deactivate current configuration
            AIConfiguration.query.update({AIConfiguration.is_active: False})
            
            # Create new configuration
            new_config = AIConfiguration(
                endpoint_type=config_data.get('endpoint_type', 'rule_based'),
                ollama_url=config_data.get('ollama_url', 'http://localhost:11434'),
                lm_studio_url=config_data.get('lm_studio_url', 'http://localhost:1234/v1'),
                custom_url=config_data.get('custom_url', ''),
                model_name=config_data.get('model_name', ''),
                api_key=config_data.get('api_key', ''),
                is_active=True
            )
            
            db.session.add(new_config)
            db.session.commit()
            
            # Apply new configuration
            self.local_ai.config.update(config_data)
            self.local_ai.check_available_services()
            
            logging.info(f"Saved AI configuration: {config_data.get('endpoint_type')}")
            return True
            
        except Exception as e:
            logging.error(f"Error saving AI configuration: {str(e)}")
            db.session.rollback()
            return False
    
    def get_status(self):
        """Get current AI service status"""
        return self.local_ai.get_status()
    
    def get_available_endpoints(self):
        """Get list of available AI endpoints"""
        return self.local_ai.get_available_endpoints()
    
    def get_configuration(self):
        """Get current configuration"""
        return self.local_ai.get_configuration()
    
    def update_configuration(self, new_config):
        """Update AI service configuration"""
        success = self.local_ai.update_configuration(new_config)
        if success:
            self.save_configuration(new_config)
        return success
    
    def test_connection(self):
        """Test current AI connection"""
        return self.local_ai.test_connection()
    
    def analyze_entry(self, entry_text, mode='reflective'):
        """Analyze journal entry using configured AI service"""
        return self.local_ai.analyze_entry(entry_text, mode)
    
    def analyze_sentiment(self, text):
        """Analyze sentiment of text"""
        return self.local_ai.analyze_sentiment(text)