# 🐦 X Profile Analysis Tool

An intelligent Twitter/X profile analyzer powered by LangChain, OpenAI, and advanced analytics. Analyze any public Twitter profile to get comprehensive insights about content strategy, engagement patterns, reply behavior, and actionable recommendations.

## ✨ Features

### 🔍 **Comprehensive Analysis**
- **Content Strategy Analysis**: AI-powered insights into content performance
- **Engagement Analytics**: Detailed metrics on likes, retweets, replies, and overall engagement
- **Reply Behavior Analysis**: Understanding how users engage with their community
- **Hook Line Extraction**: Identify successful opening strategies and writing patterns
- **Topic & Theme Analysis**: Advanced clustering and categorization of content

### 🤖 **AI-Powered Insights**
- **LangChain Integration**: Advanced document processing and semantic analysis
- **OpenAI GPT-4**: Strategic recommendations and content optimization
- **Vector Search**: Similarity-based content analysis and pattern recognition
- **Embeddings-Based Clustering**: Intelligent topic grouping and theme identification

### 📊 **Rich Visualizations**
- **Interactive Dashboards**: Plotly-powered interactive charts
- **Engagement Trends**: Time-series analysis of performance patterns
- **Content Performance**: Visual breakdown by content type and features
- **Reply Analysis Charts**: Behavior patterns and engagement metrics

### 🛠️ **Easy to Use**
- **Command Line Interface**: Simple CLI for quick analysis
- **Batch Processing**: Analyze multiple profiles efficiently
- **Export Options**: Save results as JSON, images, and HTML dashboards
- **Configurable Parameters**: Customize tweet counts, analysis depth, and output formats

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd X_profile_analysis

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Setup

Create a `.env` file with your API keys:

```bash
# Twitter API
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Basic Usage

```bash
# Analyze a profile with default settings
python cli.py elonmusk

# Analyze with custom parameters
python cli.py elonmusk -t 50 -r 20 --visualize --save

# Use only standard analysis (skip LangChain)
python cli.py elonmusk --no-langchain
```

## 📖 Detailed Usage

### Command Line Options

```bash
python cli.py [username] [options]

Arguments:
  username              Twitter username to analyze (without @)

Options:
  -t, --tweets INT      Maximum tweets to fetch (default: 20)
  -r, --replies INT     Maximum replies to fetch (default: 15)
  --no-langchain        Skip LangChain analysis, use only standard analysis
  --save               Save analysis results to JSON file
  --visualize          Create visualization charts and graphs
  --help               Show help message
  --version            Show version information
```

### Example Commands

```bash
# Basic analysis
python cli.py garyvee

# Comprehensive analysis with visualizations
python cli.py garyvee --visualize --save

# Large dataset analysis
python cli.py garyvee -t 100 -r 50 --visualize

# Quick analysis without LangChain
python cli.py garyvee --no-langchain
```

## 🧪 Testing

### Test Individual Components

```bash
# Test the basic content agent
python test_content_agent.py

# Test the LangChain agent
python test_langchain_agent.py

# Test visualizations
python visualizer.py
```

### Test with Real Data

The test files will analyze `@im_roy_lee` by default. You can modify the username in the test files to analyze different profiles.

## 📁 Project Structure

```
X_profile_analysis/
├── streamlit_app.py          # 🌐 Main Streamlit web application
├── cli.py                    # 🖥️ Command-line interface
├── X_profile_data.py         # 🐦 Twitter API integration and data processing
├── content_agent.py          # 🤖 Standard AI content analysis
├── langchain_agent.py        # 🚀 Enhanced LangChain analysis
├── requirements.txt          # 📦 Python dependencies
├── README.md                 # 📚 Project documentation
├── USAGE_GUIDE.md           # 📖 Detailed usage instructions
├── env.example              # 🔐 API keys template
├── .env                     # 🔐 Your API keys (create from example)
└── results/                # 💾 Analysis output directory
    ├── analysis_*.json     # Saved analysis results
    └── tweets_*.csv        # Tweet data exports
```

## 🔧 Configuration

### API Requirements

1. **Twitter API v2**: Get a Bearer Token from [Twitter Developer Portal](https://developer.twitter.com/)
2. **OpenAI API**: Get an API key from [OpenAI Platform](https://platform.openai.com/)

### Environment Variables

1. Copy the example file:
```bash
cp env.example .env
```

2. Edit `.env` and add your actual API keys:
```bash
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here
OPENAI_API_KEY=your_openai_api_key_here
```

## 📊 Output Examples

### 1. Analysis Results
- Comprehensive AI-generated insights
- Content strategy recommendations
- Engagement optimization tips
- Reply behavior analysis

### 2. Visualizations
- **Engagement Overview**: Time-series charts and distribution plots
- **Content Analysis**: Performance by type, word count impact, feature analysis
- **Interactive Dashboard**: Multi-panel Plotly dashboard
- **Reply Analysis**: Behavior patterns and engagement metrics

### 3. Saved Data
- JSON files with complete analysis results
- PNG images of static charts
- HTML files with interactive dashboards

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

1. **API Rate Limits**: The tool includes automatic rate limiting and retry logic
2. **Missing Dependencies**: Run `pip install -r requirements.txt`
3. **API Key Errors**: Ensure your `.env` file is properly configured
4. **No Data Found**: Check if the username exists and has public tweets

### Getting Help

- Check the [Issues](https://github.com/your-repo/issues) page
- Review the test files for usage examples
- Ensure all API keys are valid and have proper permissions

## 🔮 Future Enhancements

- [ ] Sentiment analysis with VADER or TextBlob
- [ ] Competitive analysis features
- [ ] Web interface with Streamlit/Flask
- [ ] Batch processing for multiple profiles
- [ ] Advanced NLP features with spaCy
- [ ] Real-time monitoring capabilities
- [ ] Export to PDF reports

---

**Made with ❤️ by the Dhanush chalicheemala**

