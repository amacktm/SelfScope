import json
import logging
import requests
import re
from collections import Counter
from datetime import datetime

class LocalAIService:
    def __init__(self):
        self.config = {
            'endpoint_type': 'ollama',  # ollama, lm_studio, openai_compatible
            'ollama_url': "http://localhost:11434",
            'lm_studio_url': "http://localhost:1234/v1",
            'custom_url': "",
            'model_name': "",
            'api_key': ""
        }
        self.available_models = []
        self.current_endpoint = None
        self.check_available_services()
        
    def check_available_services(self):
        """Check all available AI services and set the best one"""
        # Try LM Studio first
        if self.check_lm_studio_connection():
            self.config['endpoint_type'] = 'lm_studio'
            self.current_endpoint = self.config['lm_studio_url']
            logging.info("Using LM Studio for AI analysis")
        # Fall back to Ollama
        elif self.check_ollama_connection():
            self.config['endpoint_type'] = 'ollama'
            self.current_endpoint = self.config['ollama_url']
            logging.info("Using Ollama for AI analysis")
        else:
            self.config['endpoint_type'] = 'rule_based'
            self.current_endpoint = None
            logging.info("Using rule-based analysis")
    
    def check_lm_studio_connection(self):
        """Check if LM Studio is available and get available models"""
        try:
            response = requests.get(f"{self.config['lm_studio_url']}/models", timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                self.available_models = [model['id'] for model in models_data.get('data', [])]
                if self.available_models:
                    logging.info(f"LM Studio connected. Available models: {self.available_models}")
                    return True
        except Exception as e:
            logging.debug(f"LM Studio not available: {str(e)}")
        return False
        
    def check_ollama_connection(self):
        """Check if Ollama is available and get available models"""
        try:
            response = requests.get(f"{self.config['ollama_url']}/api/tags", timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                self.available_models = [model['name'] for model in models_data.get('models', [])]
                logging.info(f"Ollama connected. Available models: {self.available_models}")
                return True
        except Exception as e:
            logging.debug(f"Ollama not available: {str(e)}")
        return False
    
    def get_status(self):
        """Get current AI service status"""
        if self.config['endpoint_type'] == 'lm_studio' and self.available_models:
            return {
                'backend': f'LM Studio ({self.available_models[0]})',
                'available': True,
                'models': self.available_models,
                'endpoint': self.current_endpoint
            }
        elif self.config['endpoint_type'] == 'ollama' and self.available_models:
            return {
                'backend': f'Ollama ({self.available_models[0]})',
                'available': True,
                'models': self.available_models,
                'endpoint': self.current_endpoint
            }
        else:
            return {
                'backend': 'Rule-based Analysis',
                'available': True,
                'models': [],
                'endpoint': None
            }
    
    def get_available_endpoints(self):
        """Get list of available AI endpoints"""
        endpoints = [
            {
                'type': 'lm_studio',
                'name': 'LM Studio',
                'url': self.config['lm_studio_url'],
                'available': self.config['endpoint_type'] == 'lm_studio'
            },
            {
                'type': 'ollama',
                'name': 'Ollama',
                'url': self.config['ollama_url'],
                'available': self.config['endpoint_type'] == 'ollama'
            },
            {
                'type': 'rule_based',
                'name': 'Rule-based Analysis',
                'url': 'Local',
                'available': True
            }
        ]
        return endpoints
    
    def get_configuration(self):
        """Get current configuration"""
        return self.config.copy()
    
    def update_configuration(self, new_config):
        """Update AI service configuration"""
        try:
            # Update configuration
            for key, value in new_config.items():
                if key in self.config:
                    self.config[key] = value
            
            # Reset and recheck services
            self.available_models = []
            self.current_endpoint = None
            
            if new_config.get('endpoint_type') == 'lm_studio':
                success = self.check_lm_studio_connection()
                if success:
                    self.config['endpoint_type'] = 'lm_studio'
                    self.current_endpoint = self.config['lm_studio_url']
            elif new_config.get('endpoint_type') == 'ollama':
                success = self.check_ollama_connection()
                if success:
                    self.config['endpoint_type'] = 'ollama'
                    self.current_endpoint = self.config['ollama_url']
            elif new_config.get('endpoint_type') == 'openai_compatible':
                success = self.check_openai_compatible_connection(new_config.get('custom_url', ''))
                if success:
                    self.config['endpoint_type'] = 'openai_compatible'
                    self.current_endpoint = new_config.get('custom_url', '')
            else:
                # Fall back to rule-based
                self.config['endpoint_type'] = 'rule_based'
                success = True
            
            return success
            
        except Exception as e:
            logging.error(f"Error updating configuration: {str(e)}")
            return False
    
    def check_openai_compatible_connection(self, url):
        """Check OpenAI-compatible API connection"""
        try:
            if not url:
                return False
            response = requests.get(f"{url}/models", timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                self.available_models = [model['id'] for model in models_data.get('data', [])]
                logging.info(f"OpenAI-compatible API connected. Available models: {self.available_models}")
                return True
        except Exception as e:
            logging.debug(f"OpenAI-compatible API not available: {str(e)}")
        return False
    
    def test_connection(self):
        """Test current AI connection"""
        try:
            if self.config['endpoint_type'] == 'lm_studio':
                success = self.check_lm_studio_connection()
                return {
                    'success': success,
                    'message': f"LM Studio {'connected' if success else 'not available'}",
                    'models': self.available_models if success else []
                }
            elif self.config['endpoint_type'] == 'ollama':
                success = self.check_ollama_connection()
                return {
                    'success': success,
                    'message': f"Ollama {'connected' if success else 'not available'}",
                    'models': self.available_models if success else []
                }
            elif self.config['endpoint_type'] == 'openai_compatible':
                success = self.check_openai_compatible_connection(self.config['custom_url'])
                return {
                    'success': success,
                    'message': f"Custom API {'connected' if success else 'not available'}",
                    'models': self.available_models if success else []
                }
            else:
                return {
                    'success': True,
                    'message': "Rule-based analysis is always available",
                    'models': []
                }
        except Exception as e:
            return {
                'success': False,
                'message': f"Connection test failed: {str(e)}",
                'models': []
            }
    
    def analyze_entry(self, entry_text, mode='reflective'):
        """Analyze journal entry using local AI or rule-based analysis"""
        # Try current AI service if available
        if self.available_models:
            try:
                if self.config['endpoint_type'] == 'lm_studio':
                    return self._analyze_with_lm_studio(entry_text, mode)
                elif self.config['endpoint_type'] == 'ollama':
                    return self._analyze_with_ollama(entry_text, mode)
                elif self.config['endpoint_type'] == 'openai_compatible':
                    return self._analyze_with_openai_compatible(entry_text, mode)
            except Exception as e:
                logging.warning(f"AI analysis failed: {str(e)}")
        
        # Fallback to rule-based analysis
        return self._analyze_with_rules(entry_text, mode)
    
    def _analyze_with_lm_studio(self, entry_text, mode):
        """Use LM Studio for AI analysis"""
        if not self.available_models:
            raise Exception("No models available")
            
        model = self.config.get('model_name') or self.available_models[0]
        system_prompt = self._get_system_prompt(mode)
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Journal Entry:\n{entry_text}"}
            ],
            "temperature": 0.7,
            "max_tokens": 800,
            "stream": False
        }
        
        response = requests.post(f"{self.config['lm_studio_url']}/chat/completions", 
                               json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '{}')
            
            try:
                parsed_result = json.loads(content)
                parsed_result['mode'] = mode
                return parsed_result
            except json.JSONDecodeError:
                # If JSON parsing fails, create structured response from text
                return self._parse_unstructured_response(content, mode)
        
        raise Exception(f"LM Studio request failed: {response.status_code}")
    
    def _analyze_with_openai_compatible(self, entry_text, mode):
        """Use OpenAI-compatible API for analysis"""
        if not self.available_models:
            raise Exception("No models available")
            
        model = self.config.get('model_name') or self.available_models[0]
        system_prompt = self._get_system_prompt(mode)
        
        headers = {}
        if self.config.get('api_key'):
            headers['Authorization'] = f"Bearer {self.config['api_key']}"
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Journal Entry:\n{entry_text}"}
            ],
            "temperature": 0.7,
            "max_tokens": 800,
            "stream": False
        }
        
        response = requests.post(f"{self.config['custom_url']}/chat/completions", 
                               json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '{}')
            
            try:
                parsed_result = json.loads(content)
                parsed_result['mode'] = mode
                return parsed_result
            except json.JSONDecodeError:
                return self._parse_unstructured_response(content, mode)
        
        raise Exception(f"API request failed: {response.status_code}")
    
    def _analyze_with_ollama(self, entry_text, mode):
        """Use Ollama for AI analysis"""
        model = self.available_models[0]  # Use first available model
        
        system_prompt = self._get_system_prompt(mode)
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Journal Entry:\n{entry_text}"}
            ],
            "stream": False,
            "format": "json"
        }
        
        response = requests.post(f"{self.config['ollama_url']}/api/chat", json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('message', {}).get('content', '{}')
            
            try:
                parsed_result = json.loads(content)
                parsed_result['mode'] = mode
                return parsed_result
            except json.JSONDecodeError:
                # If JSON parsing fails, create structured response from text
                return self._parse_unstructured_response(content, mode)
        
        raise Exception(f"Ollama request failed: {response.status_code}")
    
    def _analyze_with_rules(self, entry_text, mode):
        """Rule-based analysis when AI is not available"""
        word_count = len(entry_text.split())
        
        # Emotion detection
        emotions = self._detect_emotions(entry_text)
        dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0] if emotions else 'neutral'
        
        # Theme detection
        themes = self._detect_themes(entry_text)
        dominant_theme = max(themes.items(), key=lambda x: x[1])[0] if themes else 'reflection'
        
        # Sentiment analysis
        sentiment = self._calculate_sentiment(entry_text)
        
        # Generate insights based on mode
        insight = self._generate_insight(entry_text, mode, dominant_emotion, dominant_theme, sentiment)
        reflection = self._generate_reflection(entry_text, mode, dominant_emotion, themes)
        question = self._generate_question(mode, dominant_emotion, dominant_theme)
        archetype = self._suggest_archetype(mode, dominant_emotion, dominant_theme)
        
        return {
            'insight': insight,
            'reflection': reflection,
            'question': question,
            'archetype': archetype,
            'mode': mode,
            'local_analysis': True
        }
    
    def _detect_emotions(self, text):
        """Detect emotions using keyword matching"""
        emotion_keywords = {
            'joy': ['happy', 'joy', 'excited', 'elated', 'cheerful', 'delighted', 'thrilled', 'glad', 'content'],
            'sadness': ['sad', 'depressed', 'down', 'melancholy', 'blue', 'gloomy', 'sorrowful', 'upset', 'disappointed'],
            'anger': ['angry', 'mad', 'furious', 'irritated', 'annoyed', 'frustrated', 'livid', 'outraged'],
            'fear': ['afraid', 'scared', 'anxious', 'worried', 'nervous', 'fearful', 'terrified', 'concerned'],
            'love': ['love', 'affection', 'adore', 'cherish', 'devoted', 'fond', 'caring', 'tender'],
            'gratitude': ['grateful', 'thankful', 'blessed', 'appreciative', 'indebted'],
            'hope': ['hopeful', 'optimistic', 'confident', 'positive', 'encouraged', 'inspired'],
            'stress': ['stressed', 'overwhelmed', 'pressure', 'burden', 'strain', 'tension', 'exhausted']
        }
        
        text_lower = text.lower()
        emotions = {}
        
        for emotion, keywords in emotion_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            if count > 0:
                emotions[emotion] = count
                
        return emotions
    
    def _detect_themes(self, text):
        """Detect themes using keyword matching"""
        theme_keywords = {
            'relationships': ['friend', 'family', 'partner', 'relationship', 'love', 'conflict', 'connection', 'dating'],
            'work': ['work', 'job', 'career', 'boss', 'colleague', 'project', 'meeting', 'deadline', 'office'],
            'growth': ['learn', 'grow', 'develop', 'improve', 'progress', 'change', 'evolve', 'better'],
            'health': ['health', 'exercise', 'diet', 'sleep', 'tired', 'energy', 'wellness', 'fitness'],
            'goals': ['goal', 'dream', 'ambition', 'plan', 'future', 'aspiration', 'vision', 'achieve'],
            'creativity': ['create', 'art', 'music', 'write', 'creative', 'inspiration', 'imagine', 'design'],
            'spirituality': ['faith', 'spiritual', 'meditation', 'prayer', 'meaning', 'purpose', 'soul'],
            'nature': ['nature', 'outdoors', 'walk', 'garden', 'trees', 'weather', 'seasons', 'hiking']
        }
        
        text_lower = text.lower()
        themes = {}
        
        for theme, keywords in theme_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            if count > 0:
                themes[theme] = count
                
        return themes
    
    def _calculate_sentiment(self, text):
        """Calculate simple sentiment score"""
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 
                         'love', 'happy', 'joy', 'success', 'accomplished', 'proud', 'grateful']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'hate', 'sad', 'angry', 
                         'frustrated', 'disappointed', 'failed', 'worried', 'anxious', 'stressed']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _generate_insight(self, text, mode, emotion, theme, sentiment):
        """Generate insight based on analysis"""
        insights = {
            'reflective': {
                'positive': [
                    f"Your entry radiates {emotion}, suggesting you're in a good place emotionally right now.",
                    f"There's a clear sense of {theme} coming through, which seems to be nurturing your well-being.",
                    "Your positive outlook shines through your words, indicating personal growth and self-awareness."
                ],
                'negative': [
                    f"I notice some {emotion} in your writing, which takes courage to acknowledge and express.",
                    f"Your struggles with {theme} are valid, and recognizing them is the first step toward healing.",
                    "Even in difficulty, your willingness to write shows resilience and hope for change."
                ],
                'neutral': [
                    f"Your reflection on {theme} shows thoughtful self-examination.",
                    "There's a contemplative quality to your writing that suggests deep inner work.",
                    "Your balanced perspective indicates emotional maturity and self-awareness."
                ]
            },
            'psychological': {
                'positive': [
                    f"The {emotion} you express may reflect an integration of positive experiences into your psyche.",
                    f"Your focus on {theme} suggests healthy psychological development in this area.",
                    "This emotional state indicates good ego strength and psychological resilience."
                ],
                'negative': [
                    f"The {emotion} you're experiencing might be your psyche's way of processing unresolved material.",
                    f"Your struggles with {theme} could represent an opportunity for psychological growth and integration.",
                    "These challenging emotions often signal that important psychological work is emerging."
                ],
                'neutral': [
                    f"Your balanced reflection on {theme} shows healthy psychological functioning.",
                    "This contemplative state suggests good self-observation skills and emotional intelligence.",
                    "Your measured emotional tone indicates psychological stability and self-awareness."
                ]
            },
            'philosopher': {
                'positive': [
                    f"Your {emotion} reflects what existentialists call 'authentic being' - living true to yourself.",
                    f"The way you engage with {theme} demonstrates an examined life, which Socrates valued above all.",
                    "Your positive perspective suggests you're creating meaning rather than just seeking it."
                ],
                'negative': [
                    f"Your {emotion} echoes what Kierkegaard called 'the dizziness of freedom' - the weight of choice.",
                    f"The struggle with {theme} you describe is what gives life its depth and authenticity.",
                    "This difficult experience may be what Nietzsche meant by 'what does not kill me makes me stronger.'"
                ],
                'neutral': [
                    f"Your thoughtful approach to {theme} reflects the philosophical virtue of contemplation.",
                    "This balanced perspective suggests you're practicing what the Stoics called 'living according to nature.'",
                    "Your reflective stance embodies what Aristotle described as the contemplative life."
                ]
            }
        }
        
        mode_insights = insights.get(mode, insights['reflective'])
        sentiment_insights = mode_insights.get(sentiment, mode_insights['neutral'])
        
        return sentiment_insights[hash(text) % len(sentiment_insights)]
    
    def _generate_reflection(self, text, mode, emotion, themes):
        """Generate reflection based on analysis"""
        if not themes:
            return "Your writing reveals a rich inner life that deserves continued exploration and attention."
            
        top_themes = sorted(themes.items(), key=lambda x: x[1], reverse=True)[:2]
        theme_names = [theme for theme, _ in top_themes]
        
        if len(theme_names) == 1:
            return f"The recurring focus on {theme_names[0]} in your writing suggests this area holds significant meaning for you right now."
        else:
            return f"The intersection of {theme_names[0]} and {theme_names[1]} in your thoughts suggests these areas are interconnected in your current life experience."
    
    def _generate_question(self, mode, emotion, theme):
        """Generate reflective question"""
        questions = {
            'reflective': {
                'relationships': "What would it look like to bring more authenticity to your relationships?",
                'work': "How might you align your work more closely with your personal values?",
                'growth': "What would you say to someone else going through a similar growth experience?",
                'health': "How does taking care of your body reflect taking care of your whole self?",
                'goals': "What would pursuing this goal teach you about yourself?",
                'creativity': "What is your creativity trying to express that words alone cannot?",
                'spirituality': "How do your spiritual beliefs show up in your daily actions?",
                'nature': "What does nature teach you about your own rhythms and needs?"
            },
            'psychological': {
                'relationships': "What unconscious patterns might be playing out in your relationships?",
                'work': "How might your work challenges reflect deeper psychological themes?",
                'growth': "What part of yourself is ready to emerge through this growth?",
                'health': "How does your relationship with your body mirror your relationship with yourself?",
                'goals': "What deeper psychological need might this goal be addressing?",
                'creativity': "What aspects of your unconscious are seeking expression through creativity?",
                'spirituality': "How do your spiritual experiences connect to your psychological development?",
                'nature': "What archetypes or instincts does nature awaken in you?"
            },
            'philosopher': {
                'relationships': "How do you maintain your authentic self while being in relationship with others?",
                'work': "What would it mean to approach your work as a form of philosophical practice?",
                'growth': "How does accepting uncertainty become a pathway to wisdom?",
                'health': "What does it mean to be a good guardian of the life you've been given?",
                'goals': "How do you distinguish between authentic desires and socially imposed expectations?",
                'creativity': "What truth is trying to emerge through your creative expression?",
                'spirituality': "How do you find meaning in the face of life's fundamental uncertainties?",
                'nature': "What does the natural world teach us about living and dying well?"
            }
        }
        
        mode_questions = questions.get(mode, questions['reflective'])
        return mode_questions.get(theme, "What would living more authentically look like for you right now?")
    
    def _suggest_archetype(self, mode, emotion, theme):
        """Suggest relevant archetype or concept"""
        if mode != 'psychological':
            return ""
            
        archetypes = {
            'relationships': "The Lover archetype - exploring connection, intimacy, and the balance between self and other",
            'work': "The Magician archetype - transforming ideas into reality and finding your unique contribution",
            'growth': "The Hero's Journey - facing challenges that transform you into who you're meant to become",
            'health': "The Caregiver archetype - learning to nurture yourself as you would nurture others",
            'goals': "The Seeker archetype - pursuing what calls to your soul rather than external expectations",
            'creativity': "The Creator archetype - bringing something new into being through your unique vision",
            'spirituality': "The Sage archetype - seeking wisdom and deeper understanding of life's mysteries",
            'nature': "The Innocent archetype - reconnecting with wonder and your natural rhythms"
        }
        
        return archetypes.get(theme, "The Explorer archetype - courageously investigating your inner landscape")
    
    def _get_system_prompt(self, mode):
        """Get system prompt for AI analysis"""
        base_prompt = """You are an AI journaling companion. Analyze the user's journal entry and provide meaningful insights in JSON format.

        Respond with this exact JSON structure:
        {
            "insight": "A thoughtful interpretation or observation",
            "reflection": "A deeper reflection on patterns or themes", 
            "question": "A meaningful question to promote self-discovery",
            "archetype": "Optional relevant psychological concept"
        }

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
    
    def _parse_unstructured_response(self, content, mode):
        """Parse unstructured AI response into expected format"""
        return {
            'insight': content[:200] + "..." if len(content) > 200 else content,
            'reflection': "This response reflects deep contemplation and self-awareness.",
            'question': "What resonates most strongly with you from this reflection?",
            'archetype': "",
            'mode': mode,
            'unstructured': True
        }
    
    def analyze_sentiment(self, text):
        """Analyze sentiment of text"""
        sentiment = self._calculate_sentiment(text)
        
        rating_map = {
            'positive': 4,
            'neutral': 3,
            'negative': 2
        }
        
        return {
            'rating': rating_map.get(sentiment, 3),
            'confidence': 0.75  # Rule-based confidence
        }