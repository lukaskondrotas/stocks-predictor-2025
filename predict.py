#!/usr/bin/env python3

import sys
import argparse
import os
from pathlib import Path

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from financial_metrics import FinancialMetricsCalculator
from news_scraper import NewsScraper
from sentiment_analyzer import SentimentAnalyzer
from scoring_system import StockScoringSystem

def main():
    parser = argparse.ArgumentParser(
        description='Stock Predictor - Analyze stocks using financial metrics and sentiment analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python predict.py AAPL
  python predict.py TSLA
  python predict.py MSFT

The analysis will be saved to {ticker}_analysis.txt
        """
    )
    
    parser.add_argument('ticker', 
                       help='Stock ticker symbol (e.g., AAPL, TSLA, MSFT)',
                       type=str)
    
    parser.add_argument('--no-sentiment', 
                       action='store_true',
                       help='Skip sentiment analysis (financial metrics only)')
    
    parser.add_argument('--output-dir',
                       default='.',
                       help='Output directory for analysis file (default: current directory)')
    
    args = parser.parse_args()
    
    ticker = args.ticker.upper()
    
    print(f"🔍 Starting analysis for {ticker}...")
    print("=" * 50)
    
    try:
        # Initialize components
        financial_calculator = FinancialMetricsCalculator(ticker)
        news_scraper = NewsScraper()
        sentiment_analyzer = SentimentAnalyzer()
        scoring_system = StockScoringSystem()
        
        # Step 1: Calculate financial metrics
        print("📊 Calculating financial metrics...")
        financial_data = financial_calculator.calculate_all_metrics()
        print(f"   ✅ Financial analysis complete - Score: {financial_data['overall_score']}/100")
        
        # Step 2: Scrape news data
        print("📰 Scraping news data...")
        news_data = news_scraper.scrape_all_news(ticker)
        print(f"   ✅ News scraping complete - Found {news_data['total_items']} items")
        
        # Step 3: Analyze sentiment (unless skipped)
        if args.no_sentiment:
            print("⏭️  Skipping sentiment analysis...")
            sentiment_data = {
                'sentiment_score': 50,
                'sentiment_label': 'NEUTRAL',
                'confidence': 0,
                'reasoning': 'Sentiment analysis was skipped'
            }
        else:
            print("🤖 Analyzing sentiment with Claude API...")
            sentiment_data = sentiment_analyzer.analyze_sentiment(ticker, news_data)
            print(f"   ✅ Sentiment analysis complete - {sentiment_data['sentiment_label']} ({sentiment_data['sentiment_score']}/100)")
        
        # Step 4: Generate overall score and recommendation
        print("📈 Generating final recommendation...")
        overall_result = scoring_system.calculate_overall_score(financial_data, sentiment_data)
        
        print("\n" + "=" * 50)
        print("🎯 ANALYSIS RESULTS:")
        print("=" * 50)
        print(f"Ticker: {ticker}")
        print(f"Overall Score: {overall_result['overall_score']}/100")
        print(f"Recommendation: {overall_result['recommendation']}")
        print(f"Confidence: {overall_result['confidence']:.1f}%")
        print(f"Financial Score: {overall_result['financial_score']}/100 (70% weight)")
        print(f"Sentiment Score: {overall_result['sentiment_score']}/100 (30% weight)")
        
        # Step 5: Generate detailed report
        print("\n📝 Generating detailed report...")
        detailed_analysis = scoring_system.generate_detailed_analysis(
            ticker, financial_data, sentiment_data, news_data
        )
        
        # Step 6: Save to file
        output_dir = Path(args.output_dir)
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / f"{ticker}_analysis.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(detailed_analysis)
        
        print(f"   ✅ Detailed analysis saved to: {output_file}")
        
        # Step 7: Display summary
        print("\n" + "=" * 50)
        print("📋 INVESTMENT SUMMARY:")
        print("=" * 50)
        print(f"📍 {overall_result['recommendation']}")
        print(f"💯 Score: {overall_result['overall_score']}/100")
        print(f"🎯 Confidence: {overall_result['confidence']:.1f}%")
        print(f"💡 {overall_result['recommendation_reasoning']}")
        
        if overall_result['confidence'] < 60:
            print("\n⚠️  LOW CONFIDENCE WARNING:")
            print("   The analysis has lower confidence due to limited or conflicting data.")
            print("   Consider additional research before making investment decisions.")
        
        print(f"\n📄 Full analysis report: {output_file}")
        print("\n✨ Analysis complete!")
        
        return 0
        
    except ValueError as e:
        print(f"❌ Error: {str(e)}")
        return 1
    except KeyboardInterrupt:
        print("\n🛑 Analysis interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        print("Please check your internet connection and API credentials.")
        return 1

if __name__ == "__main__":
    sys.exit(main())