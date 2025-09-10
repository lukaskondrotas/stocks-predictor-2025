import yfinance as yf
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import MACD
import warnings
warnings.filterwarnings('ignore')

class FinancialMetricsCalculator:
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.stock = yf.Ticker(ticker)
        self.info = None
        self.hist_data = None
        
    def fetch_data(self):
        """Fetch stock data and info"""
        try:
            self.info = self.stock.info
            self.hist_data = self.stock.history(period="1y")
            
            if self.hist_data.empty or not self.info:
                raise ValueError(f"No data found for ticker {self.ticker}")
                
        except Exception as e:
            raise ValueError(f"Failed to fetch data for {self.ticker}: {str(e)}")
    
    def calculate_moving_averages(self):
        """Calculate 20-day and 50-day moving averages"""
        if self.hist_data is None:
            return None, None
            
        ma_20 = self.hist_data['Close'].rolling(window=20).mean().iloc[-1]
        ma_50 = self.hist_data['Close'].rolling(window=50).mean().iloc[-1]
        current_price = self.hist_data['Close'].iloc[-1]
        
        # Score based on price position relative to MAs
        ma_score = 0
        if current_price > ma_20:
            ma_score += 50
        if current_price > ma_50:
            ma_score += 50
        if ma_20 > ma_50:  # Uptrend
            ma_score += 20
            
        return ma_score, {'ma_20': ma_20, 'ma_50': ma_50, 'current': current_price}
    
    def calculate_volume_metrics(self):
        """Calculate volume-based indicators"""
        if self.hist_data is None:
            return None, None
            
        avg_volume_20 = self.hist_data['Volume'].rolling(window=20).mean().iloc[-1]
        current_volume = self.hist_data['Volume'].iloc[-1]
        
        volume_ratio = current_volume / avg_volume_20
        
        # Score based on volume activity
        if volume_ratio > 1.5:
            volume_score = 100
        elif volume_ratio > 1.2:
            volume_score = 75
        elif volume_ratio > 0.8:
            volume_score = 50
        else:
            volume_score = 25
            
        return volume_score, {'volume_ratio': volume_ratio, 'avg_volume': avg_volume_20}
    
    def calculate_momentum_indicators(self):
        """Calculate RSI and MACD"""
        if self.hist_data is None:
            return None, None
            
        rsi = RSIIndicator(self.hist_data['Close']).rsi().iloc[-1]
        macd_indicator = MACD(self.hist_data['Close'])
        macd_line = macd_indicator.macd().iloc[-1]
        macd_signal = macd_indicator.macd_signal().iloc[-1]
        
        # RSI scoring (30-70 is ideal range)
        if 30 <= rsi <= 70:
            rsi_score = 100
        elif 20 <= rsi < 30 or 70 < rsi <= 80:
            rsi_score = 75
        else:
            rsi_score = 25
            
        # MACD scoring
        macd_score = 100 if macd_line > macd_signal else 25
        
        momentum_score = (rsi_score + macd_score) / 2
        
        return momentum_score, {'rsi': rsi, 'macd_line': macd_line, 'macd_signal': macd_signal}
    
    def calculate_pe_ratio(self):
        """Calculate P/E ratio score"""
        if not self.info:
            return None, None
            
        pe_ratio = self.info.get('trailingPE')
        if not pe_ratio or pe_ratio <= 0:
            return 50, {'pe_ratio': 'N/A'}
        
        # Industry average PE is around 15-25 for most sectors
        if 10 <= pe_ratio <= 20:
            pe_score = 100
        elif 5 <= pe_ratio < 10 or 20 < pe_ratio <= 30:
            pe_score = 75
        elif pe_ratio < 5 or 30 < pe_ratio <= 50:
            pe_score = 50
        else:
            pe_score = 25
            
        return pe_score, {'pe_ratio': pe_ratio}
    
    def calculate_profit_margins(self):
        """Calculate profit margin score"""
        if not self.info:
            return None, None
            
        profit_margin = self.info.get('profitMargins')
        if not profit_margin:
            return 50, {'profit_margin': 'N/A'}
        
        profit_margin_pct = profit_margin * 100
        
        if profit_margin_pct > 20:
            margin_score = 100
        elif profit_margin_pct > 10:
            margin_score = 75
        elif profit_margin_pct > 5:
            margin_score = 50
        else:
            margin_score = 25
            
        return margin_score, {'profit_margin_pct': profit_margin_pct}
    
    def calculate_roe(self):
        """Calculate Return on Equity score"""
        if not self.info:
            return None, None
            
        roe = self.info.get('returnOnEquity')
        if not roe:
            return 50, {'roe': 'N/A'}
        
        roe_pct = roe * 100
        
        if roe_pct > 15:
            roe_score = 100
        elif roe_pct > 10:
            roe_score = 75
        elif roe_pct > 5:
            roe_score = 50
        else:
            roe_score = 25
            
        return roe_score, {'roe_pct': roe_pct}
    
    def calculate_all_metrics(self):
        """Calculate all financial metrics and return overall score"""
        self.fetch_data()
        
        # Calculate individual metrics
        ma_score, ma_data = self.calculate_moving_averages()
        volume_score, volume_data = self.calculate_volume_metrics()
        momentum_score, momentum_data = self.calculate_momentum_indicators()
        pe_score, pe_data = self.calculate_pe_ratio()
        margin_score, margin_data = self.calculate_profit_margins()
        roe_score, roe_data = self.calculate_roe()
        
        # Weights for each metric
        weights = {
            'moving_averages': 0.20,
            'volume': 0.15,
            'momentum': 0.20,
            'pe_ratio': 0.15,
            'profit_margins': 0.15,
            'roe': 0.15
        }
        
        # Calculate weighted average
        total_score = (
            ma_score * weights['moving_averages'] +
            volume_score * weights['volume'] +
            momentum_score * weights['momentum'] +
            pe_score * weights['pe_ratio'] +
            margin_score * weights['profit_margins'] +
            roe_score * weights['roe']
        )
        
        return {
            'overall_score': round(total_score, 2),
            'individual_scores': {
                'moving_averages': ma_score,
                'volume': volume_score,
                'momentum': momentum_score,
                'pe_ratio': pe_score,
                'profit_margins': margin_score,
                'roe': roe_score
            },
            'metrics_data': {
                'moving_averages': ma_data,
                'volume': volume_data,
                'momentum': momentum_data,
                'pe_ratio': pe_data,
                'profit_margins': margin_data,
                'roe': roe_data
            }
        }