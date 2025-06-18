# SelfScope - Local AI Journaling Companion

A Flask-based journaling application that provides philosophical and psychological insights using local AI models.

## Features

- **Daily Journaling**: Write and save journal entries with automatic word counting
- **AI Analysis**: Get insights in three modes:
  - **Reflective Guide**: Gentle, supportive insights
  - **Psychological Insight**: Jungian & depth psychology analysis
  - **Philosopher**: Existential & meaning-focused perspectives
- **Pattern Analysis**: Track emotional trends, themes, and writing habits
- **Local-First**: All data stored locally, no cloud dependencies
- **Privacy-Focused**: Your journal entries never leave your system

## Local AI Setup

SelfScope supports multiple local AI backends:

### Option 1: Ollama (Recommended)

1. Install Ollama from https://ollama.ai/
2. Pull a model (recommended models):
   ```bash
   ollama pull llama2
   ollama pull mistral
   ollama pull codellama
   ```
3. Start Ollama server:
   ```bash
   ollama serve
   ```
4. SelfScope will automatically detect and use Ollama

### Option 2: Rule-Based Analysis (Fallback)

If no local AI is available, SelfScope uses intelligent rule-based analysis that:
- Detects emotions using keyword matching
- Identifies themes and patterns
- Provides contextual insights based on detected content
- Generates reflective questions

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```
4. Open http://localhost:5000 in your browser

## Usage

1. **Write**: Enter your thoughts in the journal textarea
2. **Choose Mode**: Select your preferred AI analysis mode
3. **Submit**: Get AI-powered insights and reflections
4. **Analyze**: Visit the dashboard to see patterns and trends

## Configuration

- Journal entries are stored in `journal_entries/` directory
- No external API keys required
- All processing happens locally

## Privacy

- All data stays on your local machine
- No network requests except to local AI services
- Journal entries are stored as JSON files
- No telemetry or tracking

## Development

The application consists of:
- `app.py` - Main Flask application
- `local_ai_service.py` - Local AI integration and rule-based analysis  
- `journal_service.py` - Journal entry management
- `pattern_analyzer.py` - Pattern and trend analysis
- `templates/` - HTML templates
- `static/` - CSS, JavaScript, and assets

## Contributing

Feel free to submit issues and enhancement requests!