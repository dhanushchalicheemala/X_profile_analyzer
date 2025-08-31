import os
import pandas as pd
from datetime import datetime
from collections import Counter
import re
from openai import OpenAI
from dotenv import load_dotenv
import json
from typing import List, Dict, Any

# Simplified approach without complex LangChain dependencies
# Using OpenAI directly for now
try:
    from langchain_core.documents import Document
    from langchain_openai import OpenAIEmbeddings, ChatOpenAI
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import FAISS
    LANGCHAIN_AVAILABLE = True
except ImportError:
    print("⚠️  LangChain dependencies not fully available. Using simplified analysis.")
    LANGCHAIN_AVAILABLE = False

load_dotenv()

class LangChainContentAgent:
    def __init__(self):
        global LANGCHAIN_AVAILABLE
        
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in your .env file")
        
        self.client = OpenAI(api_key=self.openai_api_key)
        self.name = "Enhanced Content Analysis Agent"
        self.langchain_enabled = LANGCHAIN_AVAILABLE
        
        if self.langchain_enabled:
            try:
                # Initialize LangChain components
                self.llm = ChatOpenAI(
                    temperature=0.7,
                    model_name="gpt-4o-mini",
                    openai_api_key=self.openai_api_key
                )
                
                self.embeddings = OpenAIEmbeddings(openai_api_key=self.openai_api_key)
                
                # Text splitter for document processing
                self.text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200,
                    length_function=len
                )
                print(f"✅ {self.name} initialized with full LangChain support!")
            except Exception as e:
                print(f"⚠️  LangChain initialization failed: {e}")
                print("🔄 Falling back to enhanced OpenAI analysis...")
                self.langchain_enabled = False
        
        if not self.langchain_enabled:
            print(f"✅ {self.name} initialized with enhanced OpenAI analysis!")

    def create_document_store(self, tweets_df: pd.DataFrame):
        """Create a FAISS vector store from tweets and replies"""
        documents = []
        
        # Process tweets
        for idx, row in tweets_df.iterrows():
            doc = Document(
                page_content=row['text'],
                metadata={
                    'type': 'tweet',
                    'engagement': row['engagement'],
                    'likes': row['likes'],
                    'retweets': row['retweets'],
                    'replies': row['replies'],
                    'created_at': str(row['created_at']),
                    'content_category': row.get('content_category', 'Unknown'),
                    'word_count': row['word_count'],
                    'has_hashtags': row['has_hashtags'],
                    'has_links': row['has_links'],
                    'is_thread': row['is_thread']
                }
            )
            documents.append(doc)
        

        
        # Split documents and create vector store
        split_docs = self.text_splitter.split_documents(documents)
        
        if not split_docs:
            raise ValueError("No documents to process")
        
        vectorstore = FAISS.from_documents(split_docs, self.embeddings)
        
        print(f"✅ Created vector store with {len(split_docs)} document chunks")
        return vectorstore

    def analyze_content_themes(self, vectorstore, username: str) -> Dict[str, Any]:
        """Use LangChain to analyze content themes and patterns"""
        
        # Create a retrieval QA chain
        retriever = vectorstore.as_retriever(search_kwargs={"k": 10})
        
        theme_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""
            Based on the following Twitter content from @{username}:
            
            {context}
            
            Question: {question}
            
            Please provide a detailed analysis focusing on specific examples from the content.
            """
        )
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": theme_prompt}
        )
        
        # Analyze different aspects
        analyses = {}
        
        questions = [
            "What are the main themes and topics in this content?",
            "What content gets the highest engagement and why?",
            "What writing styles and formats are most effective?",
            "What are the common hook lines and opening strategies used?"
        ]
        
        for question in questions:
            try:
                result = qa_chain.run(question)
                analyses[question] = result
                print(f"✅ Analyzed: {question[:50]}...")
            except Exception as e:
                print(f"❌ Error analyzing '{question}': {e}")
                analyses[question] = f"Analysis failed: {e}"
        
        return analyses

    def generate_content_recommendations(self, vectorstore, analyses: Dict[str, Any], username: str) -> str:
        """Generate specific content recommendations using LangChain"""
        
        # Create a summarization chain for recommendations
        recommendation_prompt = PromptTemplate(
            input_variables=["analysis_results", "username"],
            template="""
            Based on the comprehensive content analysis for @{username}:
            
            ANALYSIS RESULTS:
            {analysis_results}
            
            Please provide specific, actionable content recommendations including:
            
            1. **IMMEDIATE ACTIONS** (Next 7 days)
            - Specific content types to create
            - Optimal posting times and formats
            - Reply strategies to improve engagement
            
            2. **CONTENT STRATEGY** (Next 30 days)
            - Theme focus areas
            - Content calendar suggestions
            - Community building tactics
            
            3. **LONG-TERM GROWTH** (3-6 months)
            - Brand positioning improvements
            - Audience expansion strategies
            - Content differentiation opportunities
            
            Be specific and reference actual patterns from their content analysis.
            """
        )
        
        recommendation_chain = LLMChain(
            llm=self.llm,
            prompt=recommendation_prompt
        )
        
        # Combine all analyses
        combined_analysis = "\n\n".join([f"**{q}**\n{a}" for q, a in analyses.items()])
        
        try:
            recommendations = recommendation_chain.run(
                analysis_results=combined_analysis,
                username=username
            )
            return recommendations
        except Exception as e:
            return f"Error generating recommendations: {e}"

    def analyze_content_with_langchain(self, tweets_df: pd.DataFrame, username: str) -> Dict[str, Any]:
        """Enhanced content analysis with or without LangChain"""
        print(f"🚀 Starting enhanced analysis for @{username}")
        
        try:
            if self.langchain_enabled:
                return self._langchain_analysis(tweets_df, username)
            else:
                return self._enhanced_openai_analysis(tweets_df, username)
                
        except Exception as e:
            print(f"❌ Enhanced analysis failed: {e}")
            return {
                "agent": self.name,
                "username": username,
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def _enhanced_openai_analysis(self, tweets_df: pd.DataFrame, username: str) -> Dict[str, Any]:
        """Enhanced OpenAI analysis without LangChain"""
        print("🔍 Running enhanced OpenAI analysis...")
        
        # Prepare comprehensive data
        tweet_texts = tweets_df['text'].tolist()
        engagement_data = tweets_df[['text', 'engagement', 'likes', 'retweets', 'replies']].to_dict('records')
        
        # Multi-step analysis
        analyses = {}
        
        # 1. Theme Analysis
        theme_prompt = f"""
        Analyze the following tweets from @{username} and identify the main themes and topics:
        
        Tweets: {tweet_texts[:10]}  # Limit for API efficiency
        
        Provide a detailed analysis of:
        1. Main themes and topics
        2. Content patterns and styles
        3. Audience engagement insights
        4. Writing style characteristics
        """
        
        analyses["themes"] = self._call_openai(theme_prompt)
        
        # 2. Engagement Analysis
        engagement_prompt = f"""
        Analyze the engagement patterns for @{username} based on this data:
        
        {json.dumps(engagement_data[:5], indent=2)}
        
        Identify:
        1. What content gets the highest engagement and why
        2. Patterns in successful content
        3. Optimization opportunities
        """
        
        analyses["engagement"] = self._call_openai(engagement_prompt)
        
        # 3. Strategic Recommendations
        strategy_prompt = f"""
        Based on @{username}'s content analysis, provide strategic recommendations:
        
        Content Summary: {analyses['themes'][:500]}...
        Engagement Insights: {analyses['engagement'][:500]}...
        
        Provide specific, actionable recommendations for:
        1. Content strategy improvements
        2. Engagement optimization
        3. Audience growth tactics
        """
        
        recommendations = self._call_openai(strategy_prompt)
        
        return {
            "agent": self.name,
            "username": username,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "theme_analyses": analyses,
            "recommendations": recommendations,
            "document_count": len(tweets_df),
            "analysis_type": "Enhanced OpenAI"
        }
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API with error handling"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert social media strategist and content analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Analysis error: {e}"

    def search_similar_content(self, vectorstore, query: str, k: int = 5):
        """Search for similar content in the vector store"""
        try:
            similar_docs = vectorstore.similarity_search(query, k=k)
            return similar_docs
        except Exception as e:
            print(f"❌ Error searching similar content: {e}")
            return []

    def analyze_engagement_patterns(self, vectorstore) -> Dict[str, Any]:
        """Analyze engagement patterns using vector similarity"""
        
        # Find high-engagement content
        high_engagement_query = "viral tweet with many likes retweets high engagement popular"
        high_engagement_docs = self.search_similar_content(vectorstore, high_engagement_query, k=5)
        
        # Find thread content
        thread_query = "thread multiple tweets connected series"
        thread_docs = self.search_similar_content(vectorstore, thread_query, k=3)
        
        # Find reply patterns
        reply_query = "reply response comment interaction community"
        reply_docs = self.search_similar_content(vectorstore, reply_query, k=5)
        
        return {
            "high_engagement_content": [doc.page_content for doc in high_engagement_docs],
            "thread_content": [doc.page_content for doc in thread_docs],
            "reply_patterns": [doc.page_content for doc in reply_docs]
        }

# Test the agent
if __name__ == "__main__":
    print("🧪 Testing LangChain Content Analysis Agent...")
    agent = LangChainContentAgent()
