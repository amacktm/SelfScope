import json
import os
import logging
from openai import OpenAI

class AIService:
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            logging.warning("OPENAI_API_KEY not found in environment variables")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)
    
    def analyze_entry(self, entry_text, mode='reflective'):
        """Analyze journal entry and provide insights based on selected mode"""
        if not self.client:
            return {
                'insight': 'AI service is not available. Please check your API key configuration.',
                'reflection': '',
                'question': '',
                'archetype': '',
                'mode': mode
            }
        
        try:
            system_prompt = self._get_system_prompt(mode)
            
            response = self.client.chat.completions.create(
                # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
                # do not change this unless explicitly requested by the user
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Journal Entry:\n{entry_text}"}
                ],
                response_format={"type": "json_object"},
                max_tokens=800,
                temperature=0.7
            )
            
            result = json.loads(response.choices[0].message.content)
            result['mode'] = mode
            return result
            
        except Exception as e:
            logging.error(f"Error analyzing entry with AI: {str(e)}")
            return {
                'insight': 'Unable to generate AI insights at this time. Please try again later.',
                'reflection': '',
                'question': '',
                'archetype': '',
                'mode': mode
            }
    
    def _get_system_prompt(self, mode):
        """Get system prompt based on insight mode"""
        base_prompt = """You are an AI journaling companion trained in psychology and philosophy. 
        Analyze the user's journal entry and provide meaningful insights.
        
        Respond in JSON format with these fields:
        - "insight": A thoughtful interpretation or observation
        - "reflection": A deeper reflection on patterns or themes
        - "question": A meaningful question to promote self-discovery
        - "archetype": Optional relevant psychological archetype or concept
        
        Be compassionate, thought-provoking, and avoid surface-level responses."""
        
        if mode == 'philosopher':
            return base_prompt + """
            
            Focus on existential themes, meaning-making, and philosophical perspectives.
            Draw from existentialism, stoicism, and other philosophical traditions.
            Ask questions about purpose, authenticity, and life's deeper meanings.
            """
            
        elif mode == 'psychological':
            return base_prompt + """
            
            Focus on psychological patterns, cognitive processes, and emotional dynamics.
            Draw from Jungian psychology, cognitive behavioral insights, and depth psychology.
            Identify unconscious patterns, defense mechanisms, and growth opportunities.
            Reference relevant archetypes, shadow work, or psychological concepts when appropriate.
            """
            
        else:  # reflective mode (default)
            return base_prompt + """
            
            Focus on gentle guidance, self-reflection, and personal growth.
            Offer supportive insights that encourage deeper self-awareness.
            Ask questions that promote introspection and positive change.
            Be warm, understanding, and encouraging.
            """
    
    def analyze_sentiment(self, text):
        """Analyze sentiment of text"""
        if not self.client:
            return {'rating': 3, 'confidence': 0.5}
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a sentiment analysis expert. "
                        + "Analyze the sentiment of the text and provide a rating "
                        + "from 1 to 5 stars (1=very negative, 5=very positive) and a confidence score between 0 and 1. "
                        + "Respond with JSON in this format: "
                        + "{'rating': number, 'confidence': number}",
                    },
                    {"role": "user", "content": text},
                ],
                response_format={"type": "json_object"},
            )
            result = json.loads(response.choices[0].message.content)
            return {
                "rating": max(1, min(5, round(result["rating"]))),
                "confidence": max(0, min(1, result["confidence"])),
            }
        except Exception as e:
            logging.error(f"Error analyzing sentiment: {str(e)}")
            return {'rating': 3, 'confidence': 0.5}
