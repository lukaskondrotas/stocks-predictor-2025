from typing import Dict, Tuple
import datetime

class StockScoringSystem:
    def __init__(self):
        self.financial_weight = 0.70
        self.sentiment_weight = 0.30
        
    def calculate_overall_score(self, financial_data: Dict, sentiment_data: Dict) -> Dict:
        """Calculate overall stock score combining financial metrics and sentiment"""
        
        financial_score = financial_data.get('overall_score', 50)
        sentiment_score = sentiment_data.get('sentiment_score', 50)
        
        # Calculate weighted score
        overall_score = (
            financial_score * self.financial_weight + 
            sentiment_score * self.sentiment_weight
        )
        
        # Determine recommendation
        recommendation = self._get_recommendation(overall_score)
        confidence = self._calculate_confidence(financial_data, sentiment_data)
        
        return {
            'overall_score': round(overall_score, 2),
            'recommendation': recommendation['action'],
            'recommendation_reasoning': recommendation['reasoning'],
            'confidence': confidence,
            'financial_score': financial_score,
            'sentiment_score': sentiment_score,
            'analysis_breakdown': {
                'financial_weight': self.financial_weight,
                'sentiment_weight': self.sentiment_weight,
                'financial_contribution': round(financial_score * self.financial_weight, 2),
                'sentiment_contribution': round(sentiment_score * self.sentiment_weight, 2)
            }
        }
    
    def _get_recommendation(self, score: float) -> Dict[str, str]:
        """Determine buy/hold/sell recommendation based on score"""
        
        if score >= 75:
            return {
                'action': 'STRONG BUY',
                'reasoning': 'Strong financial fundamentals and positive market sentiment indicate excellent investment opportunity.'
            }
        elif score >= 65:
            return {
                'action': 'BUY',
                'reasoning': 'Good financial performance with positive outlook suggests favorable investment potential.'
            }
        elif score >= 55:
            return {
                'action': 'WEAK BUY',
                'reasoning': 'Moderate financial strength with decent sentiment indicates potential upside with some caution.'
            }
        elif score >= 45:
            return {
                'action': 'HOLD',
                'reasoning': 'Mixed financial indicators and neutral sentiment suggest maintaining current position.'
            }
        elif score >= 35:
            return {
                'action': 'WEAK SELL',
                'reasoning': 'Below-average financial performance with concerning sentiment indicates potential downside risk.'
            }
        elif score >= 25:
            return {
                'action': 'SELL',
                'reasoning': 'Poor financial fundamentals and negative sentiment suggest significant downside risk.'
            }
        else:
            return {
                'action': 'STRONG SELL',
                'reasoning': 'Weak financial position and very negative sentiment indicate high probability of losses.'
            }
    
    def _calculate_confidence(self, financial_data: Dict, sentiment_data: Dict) -> float:
        """Calculate confidence level in the recommendation"""
        
        # Base confidence starts at 50%
        confidence = 50
        
        # Boost confidence based on data quality and consistency
        
        # Financial data completeness
        individual_scores = financial_data.get('individual_scores', {})
        available_metrics = sum(1 for score in individual_scores.values() if score is not None)
        total_metrics = len(individual_scores)
        
        if total_metrics > 0:
            data_completeness = available_metrics / total_metrics
            confidence += data_completeness * 20  # Up to 20 points for complete data
        
        # Sentiment confidence
        sentiment_confidence = sentiment_data.get('confidence', 50)
        confidence += (sentiment_confidence - 50) * 0.3  # Scale sentiment confidence impact
        
        # Consistency check - if financial and sentiment align, boost confidence
        financial_score = financial_data.get('overall_score', 50)
        sentiment_score = sentiment_data.get('sentiment_score', 50)
        
        score_difference = abs(financial_score - sentiment_score)
        if score_difference < 20:  # If scores are within 20 points, they're aligned
            confidence += 10
        elif score_difference > 40:  # If scores are very different, reduce confidence
            confidence -= 15
        
        # Cap confidence between 0 and 100
        return max(0, min(100, round(confidence, 1)))
    
    def generate_detailed_analysis(self, ticker: str, financial_data: Dict, 
                                 sentiment_data: Dict, news_data: Dict) -> str:
        """Generate detailed analysis text for output file"""
        
        overall_result = self.calculate_overall_score(financial_data, sentiment_data)
        
        analysis_text = f"""
STOCK ANALYSIS REPORT FOR {ticker.upper()}
Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

===============================================
RECOMMENDATION: {overall_result['recommendation']}
OVERALL SCORE: {overall_result['overall_score']}/100
CONFIDENCE: {overall_result['confidence']:.1f}%
===============================================

EXECUTIVE SUMMARY:
{overall_result['recommendation_reasoning']}

DETAILED ANALYSIS:

📊 FINANCIAL METRICS ANALYSIS (Weight: 70%)
Overall Financial Score: {overall_result['financial_score']}/100

Individual Metric Scores:
"""
        
        # Add individual financial metrics
        individual_scores = financial_data.get('individual_scores', {})
        metrics_data = financial_data.get('metrics_data', {})
        
        metric_names = {
            'moving_averages': 'Moving Averages (20d/50d)',
            'volume': 'Volume Analysis', 
            'momentum': 'Momentum Indicators (RSI/MACD)',
            'pe_ratio': 'Price-to-Earnings Ratio',
            'profit_margins': 'Profit Margins',
            'roe': 'Return on Equity'
        }
        
        for key, score in individual_scores.items():
            name = metric_names.get(key, key)
            data = metrics_data.get(key, {})
            analysis_text += f"• {name}: {score}/100\n"
            
            # Add specific data points
            if key == 'moving_averages' and data:
                analysis_text += f"  Current: ${data.get('current', 'N/A'):.2f}, MA20: ${data.get('ma_20', 'N/A'):.2f}, MA50: ${data.get('ma_50', 'N/A'):.2f}\n"
            elif key == 'volume' and data:
                analysis_text += f"  Volume Ratio: {data.get('volume_ratio', 'N/A'):.2f}x average\n"
            elif key == 'momentum' and data:
                analysis_text += f"  RSI: {data.get('rsi', 'N/A'):.1f}, MACD: {data.get('macd_line', 'N/A'):.3f}\n"
            elif key == 'pe_ratio' and data:
                analysis_text += f"  P/E Ratio: {data.get('pe_ratio', 'N/A')}\n"
            elif key == 'profit_margins' and data:
                analysis_text += f"  Profit Margin: {data.get('profit_margin_pct', 'N/A'):.1f}%\n"
            elif key == 'roe' and data:
                analysis_text += f"  ROE: {data.get('roe_pct', 'N/A'):.1f}%\n"
            
            analysis_text += "\n"
        
        # Add sentiment analysis
        analysis_text += f"""
📰 SENTIMENT ANALYSIS (Weight: 30%)
Sentiment Score: {overall_result['sentiment_score']}/100
Sentiment Label: {sentiment_data.get('sentiment_label', 'NEUTRAL')}
Sentiment Confidence: {sentiment_data.get('confidence', 'N/A')}%

Sentiment Reasoning:
{sentiment_data.get('reasoning', 'No reasoning available')}

News Sources Analyzed:
• FinViz Headlines: {len(news_data.get('finviz_headlines', []))} items
• Yahoo Finance Articles: {len(news_data.get('yahoo_articles', []))} items
Total News Items: {news_data.get('total_items', 0)}

"""
        
        # Add score breakdown
        breakdown = overall_result['analysis_breakdown']
        analysis_text += f"""
📈 SCORE BREAKDOWN:
Financial Contribution: {breakdown['financial_contribution']}/70 ({breakdown['financial_weight']*100}% weight)
Sentiment Contribution: {breakdown['sentiment_contribution']}/30 ({breakdown['sentiment_weight']*100}% weight)
Total Score: {overall_result['overall_score']}/100

"""
        
        # Add investment recommendation
        action = overall_result['recommendation']
        if 'BUY' in action:
            analysis_text += """
💡 INVESTMENT RECOMMENDATION:
This stock shows positive investment potential. Consider the following:
• Monitor key financial metrics for continued strength
• Watch for any changes in market sentiment
• Consider position sizing based on your risk tolerance
• Set appropriate stop-loss levels

"""
        elif action == 'HOLD':
            analysis_text += """
💡 INVESTMENT RECOMMENDATION:
This stock shows mixed signals. Consider the following:
• Monitor for clearer directional signals
• Review quarterly earnings for fundamental changes
• Watch market sentiment trends
• Consider reducing position if outlook deteriorates

"""
        else:  # SELL
            analysis_text += """
💡 INVESTMENT RECOMMENDATION:
This stock shows concerning signals. Consider the following:
• Review position size and risk exposure
• Monitor for any positive catalysts
• Consider reducing or closing position
• Look for better investment opportunities

"""
        
        analysis_text += f"""
⚠️  RISK DISCLAIMER:
This analysis is for informational purposes only and should not be considered as financial advice.
Past performance does not guarantee future results. Always consult with a qualified financial
advisor before making investment decisions.

Analysis Confidence: {overall_result['confidence']:.1f}%
Report generated using automated financial analysis tools.
"""
        
        return analysis_text