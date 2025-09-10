# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Stock Predictor is a Python-based CLI tool that analyzes stocks using financial metrics (70%) and sentiment analysis (30%) to provide investment recommendations. It scrapes news from FinViz and uses Claude API for sentiment analysis.

## Development Setup

1. Create virtual environment: `python3 -m venv venv`
2. Activate environment: `source venv/bin/activate` 
3. Install dependencies: `pip install -r requirements.txt`
4. Set up environment: Copy `.env.example` to `.env` and add your Claude API key

## Common Commands

### Basic Usage
- Analyze stock: `python predict.py TICKER`
- Skip sentiment analysis: `python predict.py TICKER --no-sentiment`
- Custom output directory: `python predict.py TICKER --output-dir ./results`

### Development Commands
- Install dependencies: `pip install -r requirements.txt`
- Run with virtual environment: `source venv/bin/activate && python predict.py TICKER`

## Architecture

### Core Components

**Main Script**: `predict.py` - CLI interface and orchestration
**Financial Metrics**: `src/financial_metrics.py` - Calculates 6 key metrics using yfinance
- Moving averages (20d/50d)
- Volume analysis  
- Momentum indicators (RSI/MACD)
- P/E ratio analysis
- Profit margins
- Return on equity

**News Scraping**: `src/news_scraper.py` - Scrapes FinViz headlines and Yahoo Finance articles
**Sentiment Analysis**: `src/sentiment_analyzer.py` - Uses Claude API with caching system
**Scoring System**: `src/scoring_system.py` - Combines metrics (70%) + sentiment (30%) for final recommendation

### Data Flow

1. Fetch financial data via yfinance
2. Scrape news headlines from FinViz 
3. Analyze sentiment using Claude API (cached)
4. Calculate weighted score and generate recommendation
5. Output detailed analysis to text file

### Output

Generated analysis files contain:
- Investment recommendation (STRONG BUY/BUY/WEAK BUY/HOLD/WEAK SELL/SELL/STRONG SELL)
- Overall score (/100) and confidence level
- Detailed breakdown of financial metrics
- Sentiment analysis with reasoning
- Investment summary and risk disclaimer