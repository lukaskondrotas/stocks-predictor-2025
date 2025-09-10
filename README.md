# Stock Predictor 🚀📈

A Python-based CLI tool that analyzes stocks using financial metrics and sentiment analysis to provide investment recommendations.

## Features

- **Financial Analysis** (70% weight): Analyzes 6 key metrics including moving averages, momentum indicators, P/E ratios, and profitability
- **Sentiment Analysis** (30% weight): Scrapes news headlines and uses Claude AI for sentiment scoring
- **Smart Recommendations**: Provides STRONG BUY/BUY/WEAK BUY/HOLD/SELL recommendations with confidence scores
- **Detailed Reports**: Generates comprehensive analysis files with reasoning and risk disclaimers
- **Caching System**: Saves API costs by caching sentiment analysis results

## Quick Start

1. **Setup Environment**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Configure API Key**
```bash
cp .env.example .env
# Add your Claude API key to .env file
```

3. **Analyze a Stock**
```bash
python predict.py AAPL
```

## Usage Examples

```bash
# Full analysis with sentiment
python predict.py TSLA

# Skip sentiment analysis (faster, no API cost)  
python predict.py MSFT --no-sentiment

# Custom output directory
python predict.py NVDA --output-dir ./reports
```

## Sample Output

```
🎯 ANALYSIS RESULTS:
Ticker: AAPL
Overall Score: 79.92/100
Recommendation: STRONG BUY
Confidence: 79.0%
Financial Score: 92.75/100 (70% weight)
Sentiment Score: 45/100 (30% weight)
```

## Technical Details

- **Financial Data**: Yahoo Finance (via yfinance)
- **News Sources**: FinViz headlines, Yahoo Finance articles
- **AI Analysis**: Claude API for sentiment analysis
- **Metrics**: Moving averages, volume, momentum (RSI/MACD), P/E ratio, profit margins, ROE

## Cost Considerations

- Financial data is free (Yahoo Finance)
- News scraping is free 
- Claude API costs ~$0.01-0.02 per analysis
- Caching reduces repeat API calls

## Disclaimer

⚠️ **This tool is for informational purposes only and should not be considered financial advice.** Always consult with qualified financial advisors before making investment decisions.