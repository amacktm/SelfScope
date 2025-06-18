#!/usr/bin/env python3
"""
Add realistic test data to SelfScope for demonstration
"""
import os
import sys
from datetime import datetime, timedelta
from flask import Flask
from app import app, journal_service, ai_service

test_entries = [
    {
        "date": "2025-06-17",
        "text": """Today was one of those days where everything felt like an uphill battle. Started the morning rushing to catch the bus, only to realize I'd forgotten my laptop charger at home. The presentation at work went okay, but I could feel my anxiety creeping in when the client asked those tough questions about the budget projections.

I've been thinking a lot about my career lately. Sometimes I wonder if I'm on the right path or just going through the motions. There's this part of me that wants to take bigger risks, maybe start that side project I've been talking about for months. But then the practical voice kicks in - bills, responsibilities, the comfort of a steady paycheck.

Had lunch with Sarah today. She always has this way of putting things in perspective. We talked about how change is scary but staying stuck is scarier. She reminded me of when I was terrified to move to this city three years ago, and now I can't imagine being anywhere else.

Tonight I'm going to work on that business plan I started. Even if it's just for 30 minutes. Small steps count, right?"""
    },
    {
        "date": "2025-06-16", 
        "text": """What a beautiful Sunday morning! Woke up naturally around 7 AM feeling completely refreshed. There's something magical about weekends when you don't set an alarm - your body just knows when it's ready.

Spent the morning in the garden, finally planting those herbs I bought weeks ago. The smell of fresh basil and rosemary on my hands brought back memories of helping my grandmother in her garden when I was little. She always said that growing your own food was like investing in happiness.

Called mom this afternoon. She sounded good, excited about her retirement plans. It's funny how our relationship has evolved over the years. We used to clash so much when I was younger, but now our conversations feel more like talks between friends. She's planning to take painting classes - something she's wanted to do for decades but never had the time.

Feeling grateful for quiet moments like these. The world moves so fast, but days like today remind me that peace exists in the simple things. Made a big batch of vegetable soup for the week. There's something deeply satisfying about preparing meals that will nourish you for days to come."""
    },
    {
        "date": "2025-06-15",
        "text": """Ugh, everything went wrong today. Woke up late because my phone didn't charge properly overnight. Spilled coffee on my favorite shirt right before an important meeting. The meeting itself was a disaster - I was unprepared and it showed.

My manager pulled me aside afterward. She was professional about it, but I could see the disappointment in her eyes. I've been struggling to focus lately, and it's starting to affect my work. I keep making careless mistakes, forgetting deadlines, showing up mentally but not really present.

I think I need to be honest with myself about what's going on. This isn't just about work stress. I've been feeling disconnected from everything lately - friends, hobbies, even things I used to enjoy. When was the last time I read a book for pleasure? Or went for a walk just because?

Maybe I should talk to someone professional about this. There's no shame in getting help when you need it. I've been telling myself I can handle everything on my own, but clearly that's not working out so well.

Going to bed early tonight and trying to reset for tomorrow. One day at a time."""
    },
    {
        "date": "2025-06-14",
        "text": """Had the most interesting conversation with a stranger on the train today. She was reading the same book I finished last week, and we ended up talking for the entire 40-minute ride about life, dreams, and the courage it takes to pursue what really matters.

She told me about how she left her corporate job last year to become a freelance photographer. The fear was overwhelming at first - no steady income, no benefits, no clear path forward. But she said the alternative - staying in a job that was slowly killing her spirit - was scarier than the unknown.

It made me think about my own situation. I've been playing it safe for so long that I've forgotten what it feels like to be truly excited about something. When did I become so risk-averse? When did security become more important than growth?

The woman gave me her card before she got off at her stop. She said if I ever wanted to talk more about making big life changes, she'd be happy to share her experience. I might actually take her up on that.

Sometimes the universe puts exactly the right person in your path at exactly the right moment. Today felt like one of those times."""
    },
    {
        "date": "2025-06-13",
        "text": """Celebrated my friend Marcus's birthday tonight. The whole gang was there - people I've known since college, some newer friends from work, his family. There's something special about being surrounded by your chosen family, watching someone you care about be genuinely happy.

The highlight was when Marcus gave a little speech about gratitude. He talked about how turning 30 made him realize that life isn't about collecting achievements or checking boxes. It's about the people who show up for you, who laugh at your terrible jokes, who remember your birthday and make you feel seen.

We played charades until 2 AM, laughing so hard my cheeks hurt. I haven't felt that carefree in months. Sometimes you forget how good it feels to just be silly with people who accept you exactly as you are.

Walking home under the stars, I felt this overwhelming sense of appreciation for my friends. We're all figuring it out as we go, but at least we're figuring it out together. Life is so much better when you don't try to do it alone.

Need to be better about prioritizing these relationships. Work will always be there, but these moments - these people - they're what make everything else worthwhile."""
    },
    {
        "date": "2025-06-12",
        "text": """Therapy session today was intense. Dr. Chen helped me connect some dots I've been avoiding for weeks. We talked about my perfectionism and how it's actually a form of self-sabotage. I set impossibly high standards, then when I inevitably fall short, I use it as evidence that I'm not good enough.

It's exhausting being this hard on myself all the time. She asked me what I would say to a friend who was going through the same struggles I am. The answer came easily - I'd be compassionate, understanding, encouraging. So why can't I extend that same kindness to myself?

We worked on some practical strategies for catching negative self-talk before it spirals. Writing things down seems to help me get some distance from the thoughts. When I see them on paper, they often look less threatening, less absolute.

Homework for this week is to practice self-compassion. When I notice myself being critical, I'm supposed to pause and ask: "What would I tell a good friend in this situation?" It sounds simple, but I know it's going to be challenging.

Change is slow, but I'm starting to believe it's possible. Some days I feel like I'm taking two steps forward and one step back, but at least I'm moving."""
    }
]

def add_test_data():
    """Add test journal entries with AI analysis"""
    with app.app_context():
        print("Adding test journal entries...")
        
        for entry_data in test_entries:
            try:
                # Save the journal entry
                saved_entry = journal_service.save_entry(entry_data["date"], entry_data["text"])
                print(f"✓ Added entry for {entry_data['date']}")
                
                # Generate AI analysis for the entry
                ai_response = ai_service.analyze_entry(entry_data["text"], mode='reflective')
                
                # Update the entry with AI response
                update_data = {
                    "ai_response": ai_response
                }
                journal_service.update_entry(entry_data["date"], update_data)
                print(f"✓ Added AI analysis for {entry_data['date']}")
                
                # Store analytics data
                if ai_response and 'emotions' in ai_response:
                    emotion_data = ai_response.get('emotions', {})
                    theme_data = ai_response.get('themes', {})
                    sentiment_score = ai_response.get('sentiment_score', 0.5)
                    
                    journal_service.store_analytics_data(
                        entry_data["date"], 
                        emotion_data, 
                        theme_data, 
                        sentiment_score
                    )
                    print(f"✓ Added analytics data for {entry_data['date']}")
                
            except Exception as e:
                print(f"✗ Error adding entry for {entry_data['date']}: {str(e)}")
        
        print(f"\nTest data setup complete! You now have {len(test_entries)} sample journal entries.")
        print("Visit http://localhost:5000 to see the journaling interface.")
        print("Visit http://localhost:5000/dashboard to see pattern analysis.")

if __name__ == "__main__":
    add_test_data()