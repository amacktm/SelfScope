import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from datetime import datetime, timedelta
from ai_service import AIService
from journal_service import JournalService
from pattern_analyzer import PatternAnalyzer

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key-here")

# Initialize services
ai_service = AIService()
journal_service = JournalService()
pattern_analyzer = PatternAnalyzer()

@app.route('/')
def index():
    """Main journaling interface"""
    # Get recent entries for sidebar
    recent_entries = journal_service.get_recent_entries(5)
    
    # Get today's entry if it exists
    today_entry = journal_service.get_entry_by_date(datetime.now().strftime('%Y-%m-%d'))
    
    return render_template('index.html', 
                         recent_entries=recent_entries,
                         today_entry=today_entry)

@app.route('/submit_entry', methods=['POST'])
def submit_entry():
    """Handle journal entry submission and AI response"""
    try:
        entry_text = request.form.get('entry_text', '').strip()
        insight_mode = request.form.get('insight_mode', 'reflective')
        
        if not entry_text:
            flash('Please write something in your journal entry.', 'error')
            return redirect(url_for('index'))
        
        # Save the journal entry
        date_str = datetime.now().strftime('%Y-%m-%d')
        entry_data = journal_service.save_entry(date_str, entry_text)
        
        # Get AI response
        ai_response = ai_service.analyze_entry(entry_text, insight_mode)
        
        # Update entry with AI response
        entry_data['ai_response'] = ai_response
        journal_service.update_entry(date_str, entry_data)
        
        flash('Your journal entry has been saved and analyzed!', 'success')
        return redirect(url_for('index'))
        
    except Exception as e:
        logging.error(f"Error submitting entry: {str(e)}")
        flash('There was an error processing your entry. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Pattern analysis dashboard"""
    try:
        # Get entries for analysis
        entries = journal_service.get_all_entries()
        
        # Analyze patterns
        patterns = pattern_analyzer.analyze_patterns(entries)
        
        # Get sentiment trends
        sentiment_trends = pattern_analyzer.get_sentiment_trends(entries)
        
        # Get theme analysis
        theme_analysis = pattern_analyzer.get_theme_analysis(entries)
        
        return render_template('dashboard.html',
                             patterns=patterns,
                             sentiment_trends=sentiment_trends,
                             theme_analysis=theme_analysis,
                             total_entries=len(entries))
        
    except Exception as e:
        logging.error(f"Error loading dashboard: {str(e)}")
        flash('There was an error loading the dashboard.', 'error')
        return redirect(url_for('index'))

@app.route('/entry/<date>')
def view_entry(date):
    """View a specific journal entry"""
    try:
        entry = journal_service.get_entry_by_date(date)
        if not entry:
            flash('Entry not found.', 'error')
            return redirect(url_for('index'))
        
        return render_template('view_entry.html', entry=entry)
        
    except Exception as e:
        logging.error(f"Error viewing entry: {str(e)}")
        flash('There was an error loading the entry.', 'error')
        return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
