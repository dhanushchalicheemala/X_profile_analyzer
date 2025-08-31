#!/usr/bin/env python3
"""
Extracted classes from test.ipynb for use in Python scripts
"""

import tweepy 
import os
from dotenv import load_dotenv
import pandas as pd
import json
from collections import Counter
import re
from datetime import datetime
import time

load_dotenv()

class X_tweets:
    def __init__(self):
        self.bearer_token = os.environ.get("TWITTER_BEARER_TOKEN")
        if not self.bearer_token:
            print("❌ Please add your Bearer Token to the .env file")
            return
        
        self.client = tweepy.Client(bearer_token=self.bearer_token)
        self.last_request_time = 0
        self.min_delay = 5  # 5 seconds between requests
        print("✅ Bearer token loaded with rate limiting")

    def _rate_limited_request(self):
        """Ensure minimum delay between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_delay:
            sleep_time = self.min_delay - time_since_last
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    def get_user_info(self, username):
        """get basic details of the user"""
        self._rate_limited_request()
        
        try:
            user = self.client.get_user(
                username=username,
                user_fields=["public_metrics", "description", "created_at"]
            )
            return user.data
        except tweepy.TooManyRequests:
            print("⏰ Rate limit hit! Waiting 15 minutes...")
            time.sleep(900)
            return self.get_user_info(username)
        except Exception as e:
            print(f"❌ Error fetching user info: {e}")
            return None
    
    def get_users_tweets(self, username, max_tweets=10):
        """fetch tweets from username"""
        self._rate_limited_request()
        
        try:
            user = self.client.get_user(username=username)
            time.sleep(3)
            
            tweets = self.client.get_users_tweets(
                user.data.id,
                max_results=max_tweets,
                tweet_fields=["created_at", "text", "public_metrics", "context_annotations"],
                exclude=["retweets"]  # Include replies now
            )
            return tweets.data if tweets.data else []
        except tweepy.TooManyRequests:
            print("⏰ Rate limit hit on tweets! Waiting 15 minutes...")
            time.sleep(900)
            return self.get_users_tweets(username, max_tweets)
        except Exception as e:
            print(f"❌ Error fetching tweets: {e}")
            return []



class X_profile_analytics:
    def __init__(self, tweets):
        self.tweets = tweets
        self.df = self.tweets_to_dataframe()
        self.username = ""
        
    def tweets_to_dataframe(self):
        """Convert tweets to comprehensive DataFrame"""
        data = []
        for tweet in self.tweets:
            engagement = (tweet.public_metrics['like_count'] + 
                         tweet.public_metrics['retweet_count'] + 
                         tweet.public_metrics['reply_count'] + 
                         tweet.public_metrics['quote_count'])
            
            text = tweet.text
            word_count = len(text.split())
            has_hashtags = '#' in text
            has_mentions = '@' in text
            has_links = 'http' in text or 'https' in text
            is_thread = text.startswith('1/') or '1/' in text[:10]
            
            created_at = tweet.created_at
            hour = created_at.hour
            day_of_week = created_at.strftime('%A')
            
            data.append({
                'text': text,
                'created_at': created_at,
                'hour': hour,
                'day_of_week': day_of_week,
                'likes': tweet.public_metrics['like_count'],
                'retweets': tweet.public_metrics['retweet_count'],
                'replies': tweet.public_metrics['reply_count'],
                'quotes': tweet.public_metrics['quote_count'],
                'engagement': engagement,
                'word_count': word_count,
                'has_hashtags': has_hashtags,
                'has_mentions': has_mentions,
                'has_links': has_links,
                'is_thread': is_thread,
                'engagement_rate': engagement / max(tweet.public_metrics['like_count'], 1)
            })
        
        df = pd.DataFrame(data)
        df['created_at'] = pd.to_datetime(df['created_at'])
        return df



print("✅ X profile data is ready!")