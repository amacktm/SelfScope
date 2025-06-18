// Main JavaScript functionality for SelfScope

document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-save functionality (save to localStorage)
    const textarea = document.getElementById('entry_text');
    if (textarea) {
        // Load saved draft
        const savedDraft = localStorage.getItem('journal_draft');
        if (savedDraft && textarea.value.trim() === '') {
            textarea.value = savedDraft;
            updateWordCount();
        }

        // Save draft on input
        textarea.addEventListener('input', function() {
            localStorage.setItem('journal_draft', textarea.value);
        });

        // Clear draft on successful submission
        const form = document.getElementById('journalForm');
        if (form) {
            form.addEventListener('submit', function() {
                // Clear draft after a short delay to ensure form submission
                setTimeout(() => {
                    localStorage.removeItem('journal_draft');
                }, 1000);
            });
        }
    }

    // Smooth scrolling for in-page links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Enhanced form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl+Enter or Cmd+Enter to submit journal form
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const journalForm = document.getElementById('journalForm');
            if (journalForm && document.activeElement === textarea) {
                e.preventDefault();
                journalForm.dispatchEvent(new Event('submit'));
            }
        }
        
        // Escape to clear textarea
        if (e.key === 'Escape' && document.activeElement === textarea) {
            if (confirm('Clear your current entry? This cannot be undone.')) {
                textarea.value = '';
                localStorage.removeItem('journal_draft');
                updateWordCount();
            }
        }
    });

    // Reading time estimation
    function estimateReadingTime(text) {
        const wordsPerMinute = 200;
        const words = text.trim().split(/\s+/).length;
        const minutes = Math.ceil(words / wordsPerMinute);
        return minutes;
    }

    // Dynamic word count and reading time
    function updateWordCount() {
        const wordCountSpan = document.getElementById('wordCount');
        if (wordCountSpan && textarea) {
            const text = textarea.value.trim();
            const wordCount = text === '' ? 0 : text.split(/\s+/).length;
            const readingTime = estimateReadingTime(text);
            
            wordCountSpan.textContent = wordCount;
            
            // Add reading time if substantial content
            if (wordCount > 50) {
                wordCountSpan.innerHTML = `${wordCount} words <span class="text-muted">• ~${readingTime} min read</span>`;
            }
        }
    }

    // Character limit warning
    if (textarea) {
        const maxRecommendedLength = 2000;
        textarea.addEventListener('input', function() {
            const length = textarea.value.length;
            if (length > maxRecommendedLength) {
                const warning = document.getElementById('lengthWarning') || createLengthWarning();
                warning.style.display = 'block';
                warning.textContent = `Your entry is quite long (${length} characters). Consider breaking it into multiple entries for better AI analysis.`;
            } else {
                const warning = document.getElementById('lengthWarning');
                if (warning) {
                    warning.style.display = 'none';
                }
            }
        });
    }

    function createLengthWarning() {
        const warning = document.createElement('div');
        warning.id = 'lengthWarning';
        warning.className = 'alert alert-warning mt-2';
        warning.style.display = 'none';
        textarea.parentNode.appendChild(warning);
        return warning;
    }

    // Motivational prompts for empty entries
    const motivationalPrompts = [
        "How are you feeling right now?",
        "What made you smile today?",
        "What's been on your mind lately?",
        "Describe your current mood in three words.",
        "What would you tell a friend going through what you're experiencing?",
        "What are you grateful for today?",
        "What challenge are you facing, and how might you approach it?",
        "What did you learn about yourself recently?",
        "What would make tomorrow a good day?",
        "If you could change one thing about today, what would it be?"
    ];

    // Show random prompt if textarea is focused but empty
    if (textarea) {
        textarea.addEventListener('focus', function() {
            if (textarea.value.trim() === '') {
                setTimeout(() => {
                    if (textarea.value.trim() === '' && document.activeElement === textarea) {
                        const randomPrompt = motivationalPrompts[Math.floor(Math.random() * motivationalPrompts.length)];
                        showPromptTooltip(randomPrompt);
                    }
                }, 2000);
            }
        });
    }

    function showPromptTooltip(prompt) {
        const tooltip = document.createElement('div');
        tooltip.className = 'alert alert-info alert-dismissible fade show mt-2';
        tooltip.innerHTML = `
            <small><strong>Journal Prompt:</strong> ${prompt}</small>
            <button type="button" class="btn-close btn-close-sm" data-bs-dismiss="alert"></button>
        `;
        textarea.parentNode.insertBefore(tooltip, textarea.nextSibling);
        
        // Auto-dismiss after 10 seconds
        setTimeout(() => {
            if (tooltip.parentNode) {
                tooltip.remove();
            }
        }, 10000);
    }

    // Analytics tracking (privacy-conscious, local only)
    function trackLocalAnalytics(action, data = {}) {
        const analytics = JSON.parse(localStorage.getItem('selfscope_analytics') || '{}');
        const today = new Date().toISOString().split('T')[0];
        
        if (!analytics[today]) {
            analytics[today] = {};
        }
        
        if (!analytics[today][action]) {
            analytics[today][action] = 0;
        }
        
        analytics[today][action]++;
        
        // Store additional data
        if (Object.keys(data).length > 0) {
            analytics[today][`${action}_data`] = data;
        }
        
        localStorage.setItem('selfscope_analytics', JSON.stringify(analytics));
    }

    // Track journal interactions
    if (textarea) {
        let typingTimer;
        let hasStartedTyping = false;
        
        textarea.addEventListener('input', function() {
            if (!hasStartedTyping) {
                trackLocalAnalytics('started_writing');
                hasStartedTyping = true;
            }
            
            clearTimeout(typingTimer);
            typingTimer = setTimeout(() => {
                trackLocalAnalytics('writing_session', {
                    word_count: textarea.value.trim().split(/\s+/).length
                });
            }, 3000);
        });
    }

    // Track insight mode preferences
    const insightModeInputs = document.querySelectorAll('input[name="insight_mode"]');
    insightModeInputs.forEach(input => {
        input.addEventListener('change', function() {
            trackLocalAnalytics('selected_insight_mode', {
                mode: this.value
            });
        });
    });

    // Initialize charts with better responsive options
    Chart.defaults.responsive = true;
    Chart.defaults.maintainAspectRatio = false;

    // Add loading states for better UX
    const submitButton = document.getElementById('submitBtn');
    if (submitButton) {
        const originalSubmitHandler = submitButton.onclick;
        submitButton.addEventListener('click', function(e) {
            const form = this.closest('form');
            if (form && form.checkValidity()) {
                showLoadingState();
            }
        });
    }

    function showLoadingState() {
        const loadingOverlay = document.createElement('div');
        loadingOverlay.id = 'loadingOverlay';
        loadingOverlay.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center';
        loadingOverlay.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
        loadingOverlay.style.zIndex = '9999';
        loadingOverlay.innerHTML = `
            <div class="card">
                <div class="card-body text-center">
                    <div class="spinner-border text-primary mb-3" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <h5>Analyzing your entry...</h5>
                    <p class="text-muted mb-0">Our AI is reading and reflecting on your thoughts</p>
                </div>
            </div>
        `;
        document.body.appendChild(loadingOverlay);
    }

    // Clean up any existing loading overlays
    const existingOverlay = document.getElementById('loadingOverlay');
    if (existingOverlay) {
        existingOverlay.remove();
    }

    // Add print styles
    const printStyles = document.createElement('style');
    printStyles.textContent = `
        @media print {
            .navbar, .btn, #loadingOverlay { display: none !important; }
            .card { border: 1px solid #000; box-shadow: none; }
            .card-body { padding: 20px; }
            body { font-size: 12px; line-height: 1.4; }
        }
    `;
    document.head.appendChild(printStyles);

    console.log('SelfScope initialized successfully');
});

// Utility functions
window.SelfScope = {
    // Export journal data
    exportData: function() {
        const entries = [];
        // This would typically fetch from server, but for now just notify
        alert('Export functionality will be available in a future update.');
    },
    
    // Clear all local data
    clearLocalData: function() {
        if (confirm('This will clear all your local drafts and preferences. Continue?')) {
            localStorage.removeItem('journal_draft');
            localStorage.removeItem('selfscope_analytics');
            localStorage.removeItem('selfscope_preferences');
            alert('Local data cleared successfully.');
        }
    },
    
    // Get local analytics
    getAnalytics: function() {
        return JSON.parse(localStorage.getItem('selfscope_analytics') || '{}');
    }
};
