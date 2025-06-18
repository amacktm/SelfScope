import json
import os
from datetime import datetime, timedelta
import logging

class JournalService:
    def __init__(self):
        self.data_dir = 'journal_entries'
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Ensure the journal entries directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def save_entry(self, date_str, entry_text):
        """Save a journal entry for a specific date"""
        try:
            entry_data = {
                'date': date_str,
                'text': entry_text,
                'created_at': datetime.now().isoformat(),
                'word_count': len(entry_text.split())
            }
            
            filename = os.path.join(self.data_dir, f"{date_str}.json")
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(entry_data, f, indent=2, ensure_ascii=False)
            
            logging.info(f"Saved journal entry for {date_str}")
            return entry_data
            
        except Exception as e:
            logging.error(f"Error saving entry: {str(e)}")
            raise
    
    def update_entry(self, date_str, entry_data):
        """Update an existing journal entry"""
        try:
            filename = os.path.join(self.data_dir, f"{date_str}.json")
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(entry_data, f, indent=2, ensure_ascii=False)
            
            logging.info(f"Updated journal entry for {date_str}")
            
        except Exception as e:
            logging.error(f"Error updating entry: {str(e)}")
            raise
    
    def get_entry_by_date(self, date_str):
        """Get a journal entry by date"""
        try:
            filename = os.path.join(self.data_dir, f"{date_str}.json")
            if not os.path.exists(filename):
                return None
            
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            logging.error(f"Error reading entry for {date_str}: {str(e)}")
            return None
    
    def get_recent_entries(self, count=5):
        """Get the most recent journal entries"""
        try:
            entries = []
            current_date = datetime.now()
            
            # Look back up to 30 days for entries
            for i in range(30):
                date_str = (current_date - timedelta(days=i)).strftime('%Y-%m-%d')
                entry = self.get_entry_by_date(date_str)
                if entry:
                    entries.append(entry)
                    if len(entries) >= count:
                        break
            
            return entries
            
        except Exception as e:
            logging.error(f"Error getting recent entries: {str(e)}")
            return []
    
    def get_all_entries(self):
        """Get all journal entries"""
        try:
            entries = []
            if not os.path.exists(self.data_dir):
                return entries
            
            for filename in os.listdir(self.data_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.data_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            entry = json.load(f)
                            entries.append(entry)
                    except Exception as e:
                        logging.warning(f"Error reading {filename}: {str(e)}")
                        continue
            
            # Sort by date (newest first)
            entries.sort(key=lambda x: x.get('date', ''), reverse=True)
            return entries
            
        except Exception as e:
            logging.error(f"Error getting all entries: {str(e)}")
            return []
    
    def get_entries_in_range(self, start_date, end_date):
        """Get entries within a date range"""
        try:
            all_entries = self.get_all_entries()
            filtered_entries = []
            
            for entry in all_entries:
                entry_date = entry.get('date', '')
                if start_date <= entry_date <= end_date:
                    filtered_entries.append(entry)
            
            return filtered_entries
            
        except Exception as e:
            logging.error(f"Error getting entries in range: {str(e)}")
            return []
