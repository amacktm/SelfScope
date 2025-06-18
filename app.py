import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from datetime import datetime, timedelta
from database_ai_service import DatabaseAIService
from database_journal_service import DatabaseJournalService
from pattern_analyzer import PatternAnalyzer
from config import Config

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = app.config['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = app.config['SQLALCHEMY_TRACK_MODIFICATIONS']

# Initialize SQLAlchemy
from models import db

db.init_app(app)

# Make datetime and AI status available in templates
@app.context_processor
def inject_context():
    return {
        'datetime': datetime,
        'ai_status': ai_service.get_status() if 'ai_service' in globals() else {'backend': 'Loading...', 'available': False}
    }

# Import models and create database tables
from models import JournalEntry, AIConfiguration, AnalyticsData

# Initialize services
ai_service = None
journal_service = None
pattern_analyzer = None

with app.app_context():
    db.create_all()
    # Initialize services within app context
    ai_service = DatabaseAIService()
    journal_service = DatabaseJournalService()
    pattern_analyzer = PatternAnalyzer()
    logging.info("Using Database-backed AI service")

@app.route('/')
def index():
    """Main journaling interface"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Get today's entries if they exist
    today_entries = journal_service.get_entries_by_date(today)
    
    # Get recent entries for sidebar
    recent_entries = journal_service.get_recent_entries(10)
    
    return render_template('index.html', 
                         today=today,
                         today_entries=today_entries,
                         recent_entries=recent_entries)

@app.route('/submit_entry', methods=['POST'])
def submit_entry():
    """Handle journal entry submission and AI response"""
    try:
        entry_text = request.form.get('entry_text', '').strip()
        insight_mode = request.form.get('insight_mode', 'reflective')
        
        if not entry_text:
            flash('Please write something in your journal entry.', 'error')
            return redirect(url_for('index'))
        
        # Save the journal entry with current timestamp
        entry_title = request.form.get('entry_title', '').strip()
        entry_data = journal_service.save_entry(entry_text, title=entry_title)
        
        # Only get AI response if not in "none" mode
        if insight_mode != 'none':
            ai_response = ai_service.analyze_entry(entry_text, insight_mode)
            
            # Update entry with AI response
            update_data = {
                'ai_response': ai_response,
                'insight_mode': insight_mode
            }
            journal_service.update_entry(entry_data['id'], update_data)
            flash('Your journal entry has been saved and analyzed!', 'success')
        else:
            flash('Your journal entry has been saved!', 'success')
        return redirect(url_for('index'))
        
    except Exception as e:
        logging.error(f"Error submitting entry: {str(e)}")
        flash('There was an error processing your entry. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/delete_entry/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    """Delete a journal entry"""
    try:
        from models import JournalEntry
        entry = JournalEntry.query.get_or_404(entry_id)
        
        # Store entry info for confirmation message
        entry_time = entry.datetime_str
        
        # Delete the entry
        db.session.delete(entry)
        db.session.commit()
        
        flash(f'Entry from {entry_time} has been deleted.', 'info')
        return redirect(url_for('index'))
        
    except Exception as e:
        logging.error(f"Error deleting entry {entry_id}: {str(e)}")
        flash('Error deleting entry. Please try again.', 'error')
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

@app.route('/ai-settings')
def ai_settings():
    """AI configuration settings page"""
    try:
        ai_status = ai_service.get_status()
        available_endpoints = ai_service.get_available_endpoints()
        current_config = ai_service.get_configuration()
        
        return render_template('ai_settings.html',
                             ai_status=ai_status,
                             available_endpoints=available_endpoints,
                             current_config=current_config)
        
    except Exception as e:
        logging.error(f"Error loading AI settings: {str(e)}")
        flash('There was an error loading AI settings.', 'error')
        return redirect(url_for('index'))

@app.route('/ai-settings', methods=['POST'])
def update_ai_settings():
    """Update AI configuration"""
    try:
        endpoint_type = request.form.get('endpoint_type', 'ollama')
        custom_url = request.form.get('custom_url', '').strip()
        model_name = request.form.get('model_name', '').strip()
        api_key = request.form.get('api_key', '').strip()
        
        # Update AI service configuration
        success = ai_service.update_configuration({
            'endpoint_type': endpoint_type,
            'custom_url': custom_url,
            'model_name': model_name,
            'api_key': api_key
        })
        
        if success:
            flash('AI settings updated successfully!', 'success')
        else:
            flash('Failed to update AI settings. Please check your configuration.', 'error')
            
        return redirect(url_for('ai_settings'))
        
    except Exception as e:
        logging.error(f"Error updating AI settings: {str(e)}")
        flash('There was an error updating AI settings.', 'error')
        return redirect(url_for('ai_settings'))

@app.route('/test-ai-connection', methods=['POST'])
def test_ai_connection():
    """Test AI connection endpoint"""
    try:
        test_result = ai_service.test_connection()
        return jsonify(test_result)
        
    except Exception as e:
        logging.error(f"Error testing AI connection: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
