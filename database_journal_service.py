"""
Database-backed journal service using SQLite
"""
import logging
from datetime import datetime, timedelta, date
from models import db, JournalEntry, AnalyticsData
from sqlalchemy.exc import IntegrityError

class DatabaseJournalService:
    def __init__(self):
        pass
    
    def save_entry(self, entry_text, title=None, timestamp=None):
        """Save a new journal entry with timestamp"""
        try:
            if timestamp is None:
                timestamp = datetime.utcnow()
            elif isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)
                
            word_count = len(entry_text.split())
            
            # Create new entry (always create new, never update)
            new_entry = JournalEntry(
                timestamp=timestamp,
                text=entry_text,
                word_count=word_count,
                title=title
            )
            db.session.add(new_entry)
            db.session.commit()
            
            entry_data = {
                'id': new_entry.id,
                'timestamp': new_entry.timestamp.isoformat(),
                'date': new_entry.date_str,
                'time': new_entry.time_str,
                'text': entry_text,
                'word_count': word_count,
                'title': title,
                'created_at': new_entry.created_at.isoformat(),
                'updated_at': new_entry.updated_at.isoformat()
            }
            
            logging.info(f"Saved journal entry at {new_entry.datetime_str}")
            return entry_data
            
        except Exception as e:
            logging.error(f"Error saving entry: {str(e)}")
            db.session.rollback()
            raise
    
    def update_entry(self, entry_id, entry_data):
        """Update an existing journal entry by ID"""
        try:
            entry = JournalEntry.query.get(entry_id)
            
            if entry:
                # Update fields from entry_data
                if 'text' in entry_data:
                    entry.text = entry_data['text']
                    entry.word_count = len(entry_data['text'].split())
                
                if 'ai_response' in entry_data:
                    entry.ai_response_dict = entry_data['ai_response']
                
                if 'insight_mode' in entry_data:
                    entry.insight_mode = entry_data['insight_mode']
                
                if 'title' in entry_data:
                    entry.title = entry_data['title']
                
                entry.updated_at = datetime.utcnow()
                db.session.commit()
                
                logging.info(f"Updated journal entry {entry_id}")
            else:
                logging.warning(f"No entry found with ID {entry_id} to update")
                
        except Exception as e:
            logging.error(f"Error updating entry: {str(e)}")
            db.session.rollback()
            raise
    
    def get_entries_by_date(self, date_str):
        """Get all journal entries for a specific date"""
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            entries = JournalEntry.query.filter(
                db.func.date(JournalEntry.timestamp) == target_date
            ).order_by(JournalEntry.timestamp.desc()).all()
            
            result = []
            for entry in entries:
                result.append({
                    'id': entry.id,
                    'timestamp': entry.timestamp.isoformat(),
                    'date': entry.date_str,
                    'time': entry.time_str,
                    'text': entry.text,
                    'word_count': entry.word_count,
                    'title': entry.title,
                    'ai_response': entry.ai_response_dict,
                    'insight_mode': entry.insight_mode,
                    'created_at': entry.created_at.isoformat(),
                    'updated_at': entry.updated_at.isoformat()
                })
            
            return result
                
        except Exception as e:
            logging.error(f"Error reading entries for {date_str}: {str(e)}")
            return []
    
    def get_recent_entries(self, count=10):
        """Get the most recent journal entries"""
        try:
            entries = JournalEntry.query.order_by(JournalEntry.timestamp.desc()).limit(count).all()
            
            result = []
            for entry in entries:
                result.append({
                    'id': entry.id,
                    'timestamp': entry.timestamp.isoformat(),
                    'date': entry.date_str,
                    'time': entry.time_str,
                    'text': entry.text,
                    'word_count': entry.word_count,
                    'title': entry.title,
                    'ai_response': entry.ai_response_dict,
                    'insight_mode': entry.insight_mode,
                    'created_at': entry.created_at.isoformat()
                })
            
            return result
            
        except Exception as e:
            logging.error(f"Error getting recent entries: {str(e)}")
            return []
    
    def get_all_entries(self):
        """Get all journal entries"""
        try:
            entries = JournalEntry.query.order_by(JournalEntry.date.desc()).all()
            
            result = []
            for entry in entries:
                result.append({
                    'date': entry.date.strftime('%Y-%m-%d'),
                    'text': entry.text,
                    'word_count': entry.word_count,
                    'ai_response': entry.ai_response_dict,
                    'insight_mode': entry.insight_mode,
                    'created_at': entry.created_at.isoformat()
                })
            
            return result
            
        except Exception as e:
            logging.error(f"Error getting all entries: {str(e)}")
            return []
    
    def get_entries_in_range(self, start_date, end_date):
        """Get entries within a date range"""
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            entries = JournalEntry.query.filter(
                JournalEntry.date >= start,
                JournalEntry.date <= end
            ).order_by(JournalEntry.date.desc()).all()
            
            result = []
            for entry in entries:
                result.append({
                    'date': entry.date.strftime('%Y-%m-%d'),
                    'text': entry.text,
                    'word_count': entry.word_count,
                    'ai_response': entry.ai_response_dict,
                    'insight_mode': entry.insight_mode,
                    'created_at': entry.created_at.isoformat()
                })
            
            return result
            
        except Exception as e:
            logging.error(f"Error getting entries in range: {str(e)}")
            return []
    
    def get_entry_stats(self):
        """Get statistics about journal entries"""
        try:
            total_entries = JournalEntry.query.count()
            total_words = db.session.query(db.func.sum(JournalEntry.word_count)).scalar() or 0
            avg_words = total_words / total_entries if total_entries > 0 else 0
            
            # Get date range
            first_entry = JournalEntry.query.order_by(JournalEntry.date.asc()).first()
            last_entry = JournalEntry.query.order_by(JournalEntry.date.desc()).first()
            
            return {
                'total_entries': total_entries,
                'total_words': total_words,
                'avg_words_per_entry': round(avg_words, 1),
                'first_entry_date': first_entry.date.strftime('%Y-%m-%d') if first_entry else None,
                'last_entry_date': last_entry.date.strftime('%Y-%m-%d') if last_entry else None
            }
            
        except Exception as e:
            logging.error(f"Error getting entry stats: {str(e)}")
            return {
                'total_entries': 0,
                'total_words': 0,
                'avg_words_per_entry': 0,
                'first_entry_date': None,
                'last_entry_date': None
            }
    
    def store_analytics_data(self, date_str, emotion_data, theme_data, sentiment_score):
        """Store analytics data for a specific date"""
        try:
            entry_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Check if analytics data already exists
            existing_data = AnalyticsData.query.filter_by(date=entry_date).first()
            
            if existing_data:
                existing_data.emotions = emotion_data
                existing_data.themes = theme_data
                existing_data.sentiment_score = sentiment_score
            else:
                analytics_data = AnalyticsData(
                    date=entry_date,
                    sentiment_score=sentiment_score
                )
                analytics_data.emotions = emotion_data
                analytics_data.themes = theme_data
                db.session.add(analytics_data)
            
            db.session.commit()
            logging.info(f"Stored analytics data for {date_str}")
            
        except Exception as e:
            logging.error(f"Error storing analytics data: {str(e)}")
            db.session.rollback()
            raise