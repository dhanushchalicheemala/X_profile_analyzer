#!/usr/bin/env python3
"""
Streamlit Web Application for X Profile Analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime
import time
import os

# Import our analysis modules
from X_profile_data import X_tweets, X_profile_analytics
from content_agent import ContentAnalysisAgent
from langchain_agent import LangChainContentAgent

# Page configuration
st.set_page_config(
    page_title="X Profile Analysis Tool",
    page_icon="🐦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1DA1F2;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 0.75rem;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 0.75rem;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def check_api_keys():
    """Check if required API keys are available"""
    twitter_key = os.getenv("TWITTER_BEARER_TOKEN")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    return {
        "twitter": twitter_key is not None,
        "openai": openai_key is not None
    }

def create_engagement_chart(tweets_df):
    """Create engagement visualization"""
    if tweets_df.empty:
        return None
    
    # Engagement over time
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Engagement Over Time', 'Content Type Performance', 
                       'Engagement Distribution', 'Posting Hour Analysis'),
        specs=[[{"type": "scatter"}, {"type": "bar"}],
               [{"type": "histogram"}, {"type": "bar"}]]
    )
    
    # 1. Engagement over time
    tweets_sorted = tweets_df.sort_values('created_at')
    fig.add_trace(
        go.Scatter(
            x=tweets_sorted['created_at'],
            y=tweets_sorted['engagement'],
            mode='lines+markers',
            name='Engagement',
            line=dict(color='#1DA1F2')
        ),
        row=1, col=1
    )
    
    # 2. Content type performance
    if 'content_category' in tweets_df.columns:
        content_perf = tweets_df.groupby('content_category')['engagement'].mean().sort_values()
        fig.add_trace(
            go.Bar(
                x=content_perf.values,
                y=content_perf.index,
                orientation='h',
                name='Avg Engagement',
                marker_color='lightcoral'
            ),
            row=1, col=2
        )
    
    # 3. Engagement distribution
    fig.add_trace(
        go.Histogram(
            x=tweets_df['engagement'],
            nbinsx=20,
            name='Distribution',
            marker_color='lightgreen'
        ),
        row=2, col=1
    )
    
    # 4. Posting hour analysis
    tweets_df['hour'] = pd.to_datetime(tweets_df['created_at']).dt.hour
    hourly_engagement = tweets_df.groupby('hour')['engagement'].mean()
    fig.add_trace(
        go.Bar(
            x=hourly_engagement.index,
            y=hourly_engagement.values,
            name='Hourly Avg',
            marker_color='orange'
        ),
        row=2, col=2
    )
    
    fig.update_layout(
        height=800,
        showlegend=False,
        title_text="Engagement Analytics Dashboard"
    )
    
    return fig

def display_metrics(tweets_df):
    """Display key metrics"""
    if tweets_df.empty:
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Tweets",
            value=len(tweets_df)
        )
    
    with col2:
        st.metric(
            label="Avg Engagement",
            value=f"{tweets_df['engagement'].mean():.1f}"
        )
    
    with col3:
        st.metric(
            label="Best Tweet",
            value=f"{tweets_df['engagement'].max():,}"
        )
    
    with col4:
        consistency = tweets_df['engagement'].std() / tweets_df['engagement'].mean()
        st.metric(
            label="Consistency",
            value=f"{consistency:.2f}",
            help="Lower values indicate more consistent engagement"
        )

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🐦 X Profile Analysis Tool</h1>', unsafe_allow_html=True)
    st.markdown("**Powered by AI | Analyze any public Twitter/X profile**")
    
    # Sidebar
    st.sidebar.title("⚙️ Configuration")
    
    # API Key Check
    api_status = check_api_keys()
    
    if not api_status["twitter"] or not api_status["openai"]:
        st.sidebar.error("❌ Missing API Keys")
        if not api_status["twitter"]:
            st.sidebar.write("• Twitter Bearer Token required")
        if not api_status["openai"]:
            st.sidebar.write("• OpenAI API Key required")
        
        st.sidebar.info("💡 Add your API keys to the .env file")
        st.stop()
    else:
        st.sidebar.success("✅ API Keys Configured")
    
    # Analysis Settings in Sidebar
    st.sidebar.subheader("📊 Analysis Settings")
    
    max_tweets = st.sidebar.slider(
        "Number of Tweets",
        min_value=5,
        max_value=50,
        value=20,
        help="More tweets = better analysis but slower processing"
    )
    
    analysis_type = st.sidebar.selectbox(
        "Analysis Type",
        ["Standard Analysis", "Enhanced Analysis", "Both"],
        help="Enhanced analysis uses advanced AI techniques"
    )
    
    # Main Content - Username Input and Analyze Button
    st.subheader("🔍 Analyze Twitter Profile")
    
    # Username input and analyze button side by side
    col1, col2 = st.columns([3, 1])
    
    with col1:
        username = st.text_input(
            "Enter Twitter Username (without @)",
            placeholder="elonmusk",
            help="Enter the Twitter username you want to analyze",
            label_visibility="collapsed"
        )
    
    with col2:
        st.write("")  # Add some spacing
        analyze_button = st.button("🔍 Analyze Profile", type="primary", use_container_width=True)
    
    # Show demo content if no username entered
    if not username:
        st.info("👆 Enter a Twitter username above to start analysis")
        
        # Demo section
        st.subheader("🎯 What This Tool Does")
        st.markdown("""
        - **Real-time Analysis**: Fetch and analyze tweets instantly
        - **AI Insights**: GPT-4 powered strategic recommendations
        - **Visual Dashboard**: Interactive charts and metrics
        - **Export Options**: Download results as JSON
        - **Rate Limit Handling**: Automatic API protection
        """)
        
        return
    
    # Only proceed if username is entered and button is clicked
    if not analyze_button:
        st.info("👆 Click 'Analyze Profile' to start the analysis")
        return
    
    # Analysis Section - This runs when the analyze button is clicked
    if analyze_button and username:
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Initialize
            status_text.text("🔧 Initializing Twitter client...")
            progress_bar.progress(10)
            
            tweets_client = X_tweets()
            
            # Step 2: Fetch data
            status_text.text(f"📥 Fetching {max_tweets} tweets from @{username}...")
            progress_bar.progress(30)
            
            tweets = tweets_client.get_users_tweets(username, max_tweets=max_tweets)
            
            if not tweets:
                st.error("❌ No tweets found. Check username or try again later.")
                progress_bar.empty()
                status_text.empty()
                return
            
            # Step 3: Process data
            status_text.text("🔄 Processing tweet data...")
            progress_bar.progress(50)
            
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
            progress_bar.progress(70)
            
            results = {}
            
            if analysis_type in ["Enhanced Analysis", "Both"]:
                status_text.text("🤖 Running enhanced AI analysis...")
                try:
                    langchain_agent = LangChainContentAgent()
                    results['enhanced'] = langchain_agent.analyze_content_with_langchain(tweets_df, username)
                except Exception as e:
                    st.warning(f"⚠️ Enhanced analysis failed: {e}")
            
            if analysis_type in ["Standard Analysis", "Both"]:
                status_text.text("🔍 Running standard content analysis...")
                results['standard'] = content_agent.analyze_content_strategy(tweets_df, username)
            
            progress_bar.progress(100)
            status_text.text("✅ Analysis complete!")
            
            # Display Results
            st.success(f"🎉 Successfully analyzed @{username}!")
            
            # Metrics
            st.subheader("📊 Key Metrics")
            display_metrics(tweets_df)
            
            # Visualizations
            st.subheader("📈 Engagement Analytics")
            chart = create_engagement_chart(tweets_df)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
            
            # Analysis Results
            st.subheader("🤖 AI Analysis Results")
            
            # Tabs for different analyses
            if len(results) > 1:
                tab1, tab2 = st.tabs(["Standard Analysis", "Enhanced Analysis"])
                
                with tab1:
                    if 'standard' in results:
                        st.markdown(results['standard']['analysis'])
                
                with tab2:
                    if 'enhanced' in results:
                        if 'theme_analyses' in results['enhanced']:
                            for question, analysis in results['enhanced']['theme_analyses'].items():
                                st.subheader(f"📋 {question}")
                                st.write(analysis)
                        
                        if 'recommendations' in results['enhanced']:
                            st.subheader("💡 Strategic Recommendations")
                            st.write(results['enhanced']['recommendations'])
            else:
                # Single analysis
                analysis_key = list(results.keys())[0]
                analysis_data = results[analysis_key]
                
                if analysis_key == 'enhanced':
                    if 'theme_analyses' in analysis_data:
                        for question, analysis in analysis_data['theme_analyses'].items():
                            st.subheader(f"📋 {question}")
                            st.write(analysis)
                    
                    if 'recommendations' in analysis_data:
                        st.subheader("💡 Strategic Recommendations")
                        st.write(analysis_data['recommendations'])
                else:
                    st.markdown(analysis_data['analysis'])
            
            # Data Export
            st.subheader("💾 Export Data")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # JSON download
                json_data = {
                    "username": username,
                    "timestamp": datetime.now().isoformat(),
                    "tweet_count": len(tweets_df),
                    "analysis_results": results
                }
                
                st.download_button(
                    label="📥 Download Analysis (JSON)",
                    data=json.dumps(json_data, indent=2, default=str),
                    file_name=f"analysis_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            
            with col2:
                # CSV download
                csv_data = tweets_df.to_csv(index=False)
                st.download_button(
                    label="📊 Download Tweet Data (CSV)",
                    data=csv_data,
                    file_name=f"tweets_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            # Clear progress
            progress_bar.empty()
            status_text.empty()
            
        except Exception as e:
            st.error(f"❌ Analysis failed: {str(e)}")
            st.info("💡 This might be due to API rate limits. Please try again in a few minutes.")
            
            # Clear progress
            progress_bar.empty()
            status_text.empty()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Made with ❤️ using Streamlit**")
    st.sidebar.markdown("🔧 [GitHub Repository](#)")

if __name__ == "__main__":
    main()
