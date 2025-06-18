import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import logging

class PatternAnalyzer:
    def __init__(self):
        self.emotion_keywords = {
            'joy': ['happy', 'joy', 'excited', 'elated', 'cheerful', 'delighted', 'thrilled'],
            'sadness': ['sad', 'depressed', 'down', 'melancholy', 'blue', 'gloomy', 'sorrowful'],
            'anger': ['angry', 'mad', 'furious', 'irritated', 'annoyed', 'frustrated', 'livid'],
            'fear': ['afraid', 'scared', 'anxious', 'worried', 'nervous', 'fearful', 'terrified'],
            'love': ['love', 'affection', 'adore', 'cherish', 'devoted', 'fond', 'caring'],
            'gratitude': ['grateful', 'thankful', 'blessed', 'appreciative', 'thankful'],
            'hope': ['hopeful', 'optimistic', 'confident', 'positive', 'encouraged'],
            'stress': ['stressed', 'overwhelmed', 'pressure', 'burden', 'strain', 'tension']
        }
        
        self.theme_keywords = {
            'relationships': ['friend', 'family', 'partner', 'relationship', 'love', 'conflict', 'connection'],
            'work': ['work', 'job', 'career', 'boss', 'colleague', 'project', 'meeting', 'deadline'],
            'growth': ['learn', 'grow', 'develop', 'improve', 'progress', 'change', 'evolve'],
            'health': ['health', 'exercise', 'diet', 'sleep', 'tired', 'energy', 'wellness'],
            'goals': ['goal', 'dream', 'ambition', 'plan', 'future', 'aspiration', 'vision'],
            'creativity': ['create', 'art', 'music', 'write', 'creative', 'inspiration', 'imagine'],
            'spirituality': ['faith', 'spiritual', 'meditation', 'prayer', 'meaning', 'purpose'],
            'nature': ['nature', 'outdoors', 'walk', 'garden', 'trees', 'weather', 'seasons']
        }
    
    def analyze_patterns(self, entries):
        """Analyze patterns across journal entries"""
        try:
            if not entries:
                return {
                    'total_entries': 0,
                    'total_words': 0,
                    'avg_words_per_entry': 0,
                    'most_common_emotions': [],
                    'most_common_themes': [],
                    'writing_frequency': {}
                }
            
            total_words = sum(entry.get('word_count', 0) for entry in entries)
            avg_words = total_words / len(entries) if entries else 0
            
            # Analyze emotions and themes
            emotion_counts = self._analyze_emotions(entries)
            theme_counts = self._analyze_themes(entries)
            
            # Analyze writing frequency
            frequency_analysis = self._analyze_writing_frequency(entries)
            
            return {
                'total_entries': len(entries),
                'total_words': total_words,
                'avg_words_per_entry': round(avg_words, 1),
                'most_common_emotions': emotion_counts.most_common(5),
                'most_common_themes': theme_counts.most_common(5),
                'writing_frequency': frequency_analysis
            }
            
        except Exception as e:
            logging.error(f"Error analyzing patterns: {str(e)}")
            return {}
    
    def get_sentiment_trends(self, entries):
        """Get sentiment trends over time"""
        try:
            sentiment_data = []
            
            for entry in entries:
                # Simple sentiment analysis based on keywords
                text = entry.get('text', '').lower()
                sentiment_score = self._calculate_sentiment_score(text)
                
                sentiment_data.append({
                    'date': entry.get('date', ''),
                    'sentiment': sentiment_score,
                    'word_count': entry.get('word_count', 0)
                })
            
            # Sort by date
            sentiment_data.sort(key=lambda x: x['date'])
            
            return sentiment_data
            
        except Exception as e:
            logging.error(f"Error getting sentiment trends: {str(e)}")
            return []
    
    def get_theme_analysis(self, entries):
        """Get detailed theme analysis"""
        try:
            theme_evolution = defaultdict(list)
            
            for entry in entries:
                text = entry.get('text', '').lower()
                date = entry.get('date', '')
                
                # Count themes in this entry
                for theme, keywords in self.theme_keywords.items():
                    count = sum(1 for keyword in keywords if keyword in text)
                    if count > 0:
                        theme_evolution[theme].append({
                            'date': date,
                            'count': count
                        })
            
            # Convert to format suitable for charting
            theme_data = {}
            for theme, data_points in theme_evolution.items():
                # Sort by date
                data_points.sort(key=lambda x: x['date'])
                theme_data[theme] = data_points
            
            return theme_data
            
        except Exception as e:
            logging.error(f"Error getting theme analysis: {str(e)}")
            return {}
    
    def _analyze_emotions(self, entries):
        """Analyze emotional content across entries"""
        emotion_counts = Counter()
        
        for entry in entries:
            text = entry.get('text', '').lower()
            for emotion, keywords in self.emotion_keywords.items():
                count = sum(1 for keyword in keywords if keyword in text)
                if count > 0:
                    emotion_counts[emotion] += count
        
        return emotion_counts
    
    def _analyze_themes(self, entries):
        """Analyze thematic content across entries"""
        theme_counts = Counter()
        
        for entry in entries:
            text = entry.get('text', '').lower()
            for theme, keywords in self.theme_keywords.items():
                count = sum(1 for keyword in keywords if keyword in text)
                if count > 0:
                    theme_counts[theme] += count
        
        return theme_counts
    
    def _analyze_writing_frequency(self, entries):
        """Analyze writing frequency patterns"""
        try:
            dates = [entry.get('date', '') for entry in entries if entry.get('date')]
            if not dates:
                return {}
            
            # Convert to datetime objects
            date_objects = []
            for date_str in dates:
                try:
                    date_objects.append(datetime.strptime(date_str, '%Y-%m-%d'))
                except ValueError:
                    continue
            
            if not date_objects:
                return {}
            
            # Analyze by day of week
            weekday_counts = Counter(date.strftime('%A') for date in date_objects)
            
            # Analyze streaks
            date_objects.sort()
            current_streak = 1
            max_streak = 1
            
            for i in range(1, len(date_objects)):
                if (date_objects[i] - date_objects[i-1]).days == 1:
                    current_streak += 1
                    max_streak = max(max_streak, current_streak)
                else:
                    current_streak = 1
            
            return {
                'by_weekday': dict(weekday_counts),
                'max_streak': max_streak,
                'total_days': len(set(date_objects))
            }
            
        except Exception as e:
            logging.error(f"Error analyzing writing frequency: {str(e)}")
            return {}
    
    def _calculate_sentiment_score(self, text):
        """Calculate a simple sentiment score"""
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 
                         'love', 'happy', 'joy', 'success', 'accomplished', 'proud']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'hate', 'sad', 'angry', 
                         'frustrated', 'disappointed', 'failed', 'worried', 'anxious']
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        # Normalize to -1 to 1 scale
        total_words = len(text.split())
        if total_words == 0:
            return 0
        
        sentiment = (positive_count - negative_count) / total_words * 10
        return max(-1, min(1, sentiment))
