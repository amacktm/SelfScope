"""
Database models for SelfScope
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()

class JournalEntry(db.Model):
    """Journal entry model"""
    __tablename__ = 'journal_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True, index=True)
    text = db.Column(db.Text, nullable=False)
    word_count = db.Column(db.Integer, default=0)
    ai_response = db.Column(db.Text)  # JSON string
    insight_mode = db.Column(db.String(50), default='reflective')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<JournalEntry {self.date}>'
    
    @property
    def ai_response_dict(self):
        """Get AI response as dictionary"""
        if self.ai_response:
            try:
                return json.loads(self.ai_response)
            except json.JSONDecodeError:
                return {}
        return {}
    
    @ai_response_dict.setter
    def ai_response_dict(self, value):
        """Set AI response from dictionary"""
        if value:
            self.ai_response = json.dumps(value)
        else:
            self.ai_response = None

class AIConfiguration(db.Model):
    """AI configuration settings"""
    __tablename__ = 'ai_configurations'
    
    id = db.Column(db.Integer, primary_key=True)
    endpoint_type = db.Column(db.String(50), nullable=False, default='rule_based')
    ollama_url = db.Column(db.String(255), default='http://localhost:11434')
    lm_studio_url = db.Column(db.String(255), default='http://localhost:1234/v1')
    custom_url = db.Column(db.String(255))
    model_name = db.Column(db.String(255))
    api_key = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<AIConfiguration {self.endpoint_type}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'endpoint_type': self.endpoint_type,
            'ollama_url': self.ollama_url,
            'lm_studio_url': self.lm_studio_url,
            'custom_url': self.custom_url,
            'model_name': self.model_name,
            'api_key': self.api_key,
            'is_active': self.is_active
        }

class AnalyticsData(db.Model):
    """Store analytics and pattern data"""
    __tablename__ = 'analytics_data'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, index=True)
    emotion_data = db.Column(db.Text)  # JSON string
    theme_data = db.Column(db.Text)   # JSON string
    sentiment_score = db.Column(db.Float)
    writing_streak = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AnalyticsData {self.date}>'
    
    @property
    def emotions(self):
        """Get emotions as dictionary"""
        if self.emotion_data:
            try:
                return json.loads(self.emotion_data)
            except json.JSONDecodeError:
                return {}
        return {}
    
    @emotions.setter
    def emotions(self, value):
        """Set emotions from dictionary"""
        if value:
            self.emotion_data = json.dumps(value)
        else:
            self.emotion_data = None
    
    @property
    def themes(self):
        """Get themes as dictionary"""
        if self.theme_data:
            try:
                return json.loads(self.theme_data)
            except json.JSONDecodeError:
                return {}
        return {}
    
    @themes.setter
    def themes(self, value):
        """Set themes from dictionary"""
        if value:
            self.theme_data = json.dumps(value)
        else:
            self.theme_data = None