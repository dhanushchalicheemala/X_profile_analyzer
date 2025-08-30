#!/usr/bin/env python3
"""
Test the Content Analysis Agent with real data
"""

# Import your existing classes
import sys
import os
import pandas as pd
from content_agent import ContentAnalysisAgent

# Import from your notebook (we'll extract the classes)
exec(open('X_profile_data.py').read())

def test_content_agent():
    """Test content agent with real Twitter data"""
    
    print("🧪 TESTING CONTENT ANALYSIS AGENT")
    print("=" * 40)
    
    # Step 1: Test agent initialization
    try:
        agent = ContentAnalysisAgent()
        print("✅ Agent initialized successfully")
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        return False
    
    # Step 2: Get real Twitter data (using your existing code)
    try:
        # You'll need to extract these classes from your notebook
        from X_profile_data import X_tweets, X_profile_analytics
        
        tweets_client = X_tweets()
        username = "im_roy_lee"
        
        print(f"📥 Fetching tweets for @{username}...")
        tweets = tweets_client.get_users_tweets(username, max_tweets=20)
        
        if not tweets:
            print("❌ No tweets fetched")
            return False
        
        print(f"✅ Fetched {len(tweets)} tweets")
        
    except Exception as e:
        print(f"❌ Data fetching failed: {e}")
        return False
    
    # Step 3: Convert to DataFrame
    try:
        analyzer = X_profile_analytics(tweets)
        tweets_df = analyzer.df
        print(f"✅ Converted to DataFrame: {len(tweets_df)} rows")
        
    except Exception as e:
        print(f"❌ DataFrame conversion failed: {e}")
        return False
    
    # Step 4: Run AI analysis
    try:
        print("🤖 Running AI content analysis...")
        results = agent.analyze_content_strategy(tweets_df, username)
        
        print("\n🎯 AI ANALYSIS RESULTS")
        print("=" * 30)
        print(results["analysis"])
        
        print("\n✅ Content agent test successful!")
        return True
        
    except Exception as e: 
        print(f"❌ AI analysis failed: {e}")
        return False

if __name__ == "__main__":
    test_content_agent()
