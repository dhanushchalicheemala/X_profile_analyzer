import os
import pandas as pd
from datetime import datetime
from collections import Counter
import re
from openai import OpenAI
from dotenv import load_dotenv
import json
load_dotenv()

class ContentAnalysisAgent:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"),base_url="https://api.openai.com/v1")
        self.name ="Content Analysis Agent"
        print(f"{self.name} is ready!")

        
    def analyze_content_strategy(self,tweets_df: pd.DataFrame,username: str) -> dict:
        """Funtion to anlyze content strategy"""
        print(f"{self.name} is anlyzing content strategy of @{username}")

        content_data = self.prepare_content_data(tweets_df)

        prompt = self.create_analysis_prompt(content_data,username)

        ai_insights = self.gen_ai_analysis(prompt)

        results = {
            "agent" : self.name,
            "username" : username,
            "analysis" : ai_insights,
            "data_summary" : content_data,
            "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        print(f"Analysis completed of {self.name} for @{username}")

        return results

    def prepare_content_data(self,df: pd.DataFrame) -> str:
        """Function to prepare content data"""

        content_categories =[]
        for text in df['text']:
            category = self.categorize_tweet(text)
            content_categories.append(category)

        df["content_category"] = content_categories


        category_performance = df.groupby('content_category').agg({
            'engagement': ['mean', 'count', 'max'],
            'likes': 'mean',
            'replies': 'mean',
            'retweets': 'mean'
        }).round(1)
        
        # Get top performing tweets by category
        top_tweets_by_category = {}
        for category in df['content_category'].unique():
            category_tweets = df[df['content_category'] == category]
            if len(category_tweets) > 0:
                top_tweet = category_tweets.loc[category_tweets['engagement'].idxmax()]
                top_tweets_by_category[category] = {
                    'text': top_tweet['text'][:100] + '...',
                    'engagement': int(top_tweet['engagement'])
                }
        
        summary = f"""
                    CONTENT ANALYSIS DATA:

                    Total tweets analyzed: {len(df)}
                    Analysis period: {df['created_at'].min()} to {df['created_at'].max()}

                    CONTENT CATEGORY PERFORMANCE:
                    {category_performance.to_string()}

                    TOP PERFORMING TWEET BY CATEGORY:
                    {json.dumps(top_tweets_by_category, indent=2)}

                    OVERALL METRICS:
                    - Average engagement: {df['engagement'].mean():.1f}
                    - Median engagement: {df['engagement'].median():.1f}
                    - Best performing tweet: {df['engagement'].max():,}
                    - Engagement consistency: {df['engagement'].std() / df['engagement'].mean():.2f}
                """
        return summary

    def categorize_tweet(self, text: str) -> str:
        """Categorize tweet by content type"""
        text_lower = text.lower()
        
        # Define keyword patterns for each category
        educational_patterns = ['how to', 'guide', 'tutorial', 'learn', 'tip', 'advice', 'here\'s', 'steps']
        personal_patterns = ['i ', 'my ', 'me ', 'personal', 'story', 'experience', 'feeling', 'today']
        promotional_patterns = ['buy', 'sale', 'course', 'product', 'launch', 'offer', 'discount', 'link in bio']
        opinion_patterns = ['think', 'believe', 'opinion', 'hot take', 'unpopular', 'controversial']
        news_patterns = ['breaking', 'just announced', 'update', 'news', 'happening now']
        
        # Check patterns
        if any(pattern in text_lower for pattern in educational_patterns):
            return 'Educational'
        elif any(pattern in text_lower for pattern in personal_patterns):
            return 'Personal'
        elif any(pattern in text_lower for pattern in promotional_patterns):
            return 'Promotional'
        elif any(pattern in text_lower for pattern in opinion_patterns):
            return 'Opinion/Commentary'
        elif any(pattern in text_lower for pattern in news_patterns):
            return 'News/Updates'
        else:
            return 'General'

    def create_analysis_prompt(self, content_data: str, username: str) -> str:
        """Create the AI analysis prompt"""
        
        return f"""
            You are an expert Twitter content strategist analyzing @{username}'s content performance.

            CONTENT PERFORMANCE DATA:
            {content_data}

            Please provide a comprehensive content strategy analysis including:

            1. **CONTENT TYPE EFFECTIVENESS**
            - Which content categories perform best and why
            - Audience preferences and engagement patterns
            - Content gaps and missed opportunities

            2. **CONTENT OPTIMIZATION INSIGHTS**
            - What makes their best content work
            - Specific elements that drive engagement
            - Writing style and format analysis

            3. **STRATEGIC RECOMMENDATIONS**
            - Immediate content adjustments (next 7 days)
            - Content calendar suggestions
            - Specific content ideas based on what works

            4. **COMPETITIVE POSITIONING**
            - How their content strategy compares to successful creators
            - Unique angles they should leverage
            - Areas for differentiation

            Be specific, actionable, and focus on insights that can immediately improve their content performance.
            """
    
    def gen_ai_analysis(self, prompt: str) -> str:
        """Get AI analysis from OpenAI (or Grok when available)"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Use gpt-4 for better analysis
                messages=[
                    {"role": "system", "content": "You are an expert Twitter content strategist with deep understanding of viral content patterns and audience psychology."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ AI Analysis Error: {e}")
            return f"Error getting AI analysis: {e}"

# Test the agent
if __name__ == "__main__":
    print("🧪 Testing Content Analysis Agent...")
    agent = ContentAnalysisAgent()