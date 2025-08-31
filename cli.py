#!/usr/bin/env python3
"""
Command Line Interface for X Profile Analysis
"""

import argparse
import sys
import os
from datetime import datetime
import json

# Import our analysis modules
from X_profile_data import X_tweets, X_profile_analytics
from content_agent import ContentAnalysisAgent
from langchain_agent import LangChainContentAgent

def print_banner():
    """Print the application banner"""
    print("=" * 60)
    print("🐦 X PROFILE ANALYSIS TOOL")
    print("   Powered by LangChain & OpenAI")
    print("=" * 60)

def get_profile_analysis(username: str, max_tweets: int = 20, 
                        use_langchain: bool = True, save_results: bool = False, 
                        create_visualizations: bool = False):
    """Main function to analyze a Twitter profile"""
    
    print(f"🎯 Analyzing @{username}")
    print("-" * 40)
    
    try:
        # Step 1: Initialize data client
        print("🔧 Initializing Twitter client...")
        tweets_client = X_tweets()
        
        # Step 2: Fetch data
        print(f"📥 Fetching {max_tweets} tweets...")
        tweets = tweets_client.get_users_tweets(username, max_tweets=max_tweets)
        
        if not tweets:
            print("❌ No tweets found. Check username or API limits.")
            return None
        
        print(f"✅ Data fetched: {len(tweets)} tweets")
        
        # Step 3: Process data
        print("🔄 Processing data...")
        analyzer = X_profile_analytics(tweets)
        tweets_df = analyzer.df
        
        # Add content categories
        content_agent = ContentAnalysisAgent()
        content_categories = []
        for text in tweets_df['text']:
            category = content_agent.categorize_tweet(text)
            content_categories.append(category)
        tweets_df["content_category"] = content_categories
        
        # Step 4: Run analysis
        results = {}
        
        if use_langchain:
            print("🤖 Running enhanced LangChain analysis...")
            try:
                langchain_agent = LangChainContentAgent()
                results['langchain'] = langchain_agent.analyze_content_with_langchain(
                    tweets_df, username
                )
                
                if "error" not in results['langchain']:
                    print("✅ Enhanced analysis completed!")
                else:
                    print(f"⚠️  Enhanced analysis failed: {results['langchain']['error']}")
            except Exception as e:
                print(f"⚠️  Enhanced analysis error: {e}")
                print("🔄 Continuing with standard analysis...")
        
        # Always run original analysis as backup
        print("🔍 Running standard content analysis...")
        results['standard'] = content_agent.analyze_content_strategy(
            tweets_df, username
        )
        print("✅ Standard analysis completed!")
        
        # Step 5: Display results
        display_results(results, username, use_langchain)
        
        # Step 6: Visualizations available in web app
        if create_visualizations:
            print("📊 Visualizations are available in the Streamlit web app!")
            print("🌐 Run: streamlit run streamlit_app.py")
            print("💡 The web app includes interactive Plotly charts")
        
        # Step 7: Save results if requested
        if save_results:
            save_analysis_results(results, username)
        
        return results
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return None

def display_results(results: dict, username: str, show_langchain: bool = True):
    """Display analysis results in a formatted way"""
    
    print("\n" + "🎯 ANALYSIS RESULTS".center(60, "="))
    print(f"Profile: @{username}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Show LangChain results if available
    if show_langchain and 'langchain' in results and 'error' not in results['langchain']:
        langchain_data = results['langchain']
        
        print("\n🚀 LANGCHAIN ANALYSIS")
        print("-" * 30)
        
        # Show theme analyses
        if 'theme_analyses' in langchain_data:
            for question, analysis in langchain_data['theme_analyses'].items():
                print(f"\n📊 {question}")
                print("─" * 50)
                # Truncate long analyses for CLI display
                display_text = analysis[:400] + "..." if len(analysis) > 400 else analysis
                print(display_text)
        
        # Show recommendations
        if 'recommendations' in langchain_data:
            print(f"\n💡 RECOMMENDATIONS")
            print("─" * 50)
            recommendations = langchain_data['recommendations']
            display_recommendations = recommendations[:600] + "..." if len(recommendations) > 600 else recommendations
            print(display_recommendations)
    
    # Show standard analysis
    if 'standard' in results:
        print(f"\n🔍 STANDARD ANALYSIS")
        print("-" * 30)
        standard_analysis = results['standard']['analysis']
        display_analysis = standard_analysis[:500] + "..." if len(standard_analysis) > 500 else standard_analysis
        print(display_analysis)
        
        if results['standard'].get('reply_summary'):
            print(f"\n💬 REPLY ANALYSIS")
            print("-" * 30)
            reply_summary = results['standard']['reply_summary']
            display_replies = reply_summary[:300] + "..." if len(reply_summary) > 300 else reply_summary
            print(display_replies)

def save_analysis_results(results: dict, username: str):
    """Save analysis results to a JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"analysis_{username}_{timestamp}.json"
    
    try:
        # Create results directory if it doesn't exist
        os.makedirs("results", exist_ok=True)
        filepath = os.path.join("results", filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n💾 Results saved to: {filepath}")
        
    except Exception as e:
        print(f"⚠️  Failed to save results: {e}")

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Analyze Twitter/X profiles with AI-powered insights",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py elonmusk                    # Analyze @elonmusk with default settings
  python cli.py elonmusk -t 50 -r 20       # Fetch 50 tweets and 20 replies
  python cli.py elonmusk --no-langchain    # Use only standard analysis
  python cli.py elonmusk --save             # Save results to file
        """
    )
    
    parser.add_argument(
        "username",
        help="Twitter username to analyze (without @)"
    )
    
    parser.add_argument(
        "-t", "--tweets",
        type=int,
        default=20,
        help="Maximum number of tweets to fetch (default: 20)"
    )
    

    
    parser.add_argument(
        "--no-langchain",
        action="store_true",
        help="Skip LangChain analysis, use only standard analysis"
    )
    
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save analysis results to JSON file"
    )
    
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Create visualization charts and graphs"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="X Profile Analysis Tool v1.0"
    )
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Validate username
    username = args.username.replace("@", "").strip()
    if not username:
        print("❌ Please provide a valid username")
        sys.exit(1)
    
    # Check for API keys
    if not os.getenv("TWITTER_BEARER_TOKEN"):
        print("❌ TWITTER_BEARER_TOKEN not found in environment variables")
        print("💡 Please add your Twitter API Bearer Token to your .env file")
        sys.exit(1)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment variables") 
        print("💡 Please add your OpenAI API Key to your .env file")
        sys.exit(1)
    
    # Run analysis
    results = get_profile_analysis(
        username=username,
        max_tweets=args.tweets,
        use_langchain=not args.no_langchain,
        save_results=args.save,
        create_visualizations=args.visualize
    )
    
    if results:
        print(f"\n🎉 Analysis complete for @{username}!")
        print("💡 Use --save flag to save results to file")
        print("🔄 Run with --help for more options")
    else:
        print(f"\n❌ Analysis failed for @{username}")
        sys.exit(1)

if __name__ == "__main__":
    main()
