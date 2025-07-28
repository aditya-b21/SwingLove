import json
import logging
import os
from google import genai
from google.genai import types

class GeminiStockAnalyzer:
    def __init__(self):
        """Initialize Gemini client for stock analysis"""
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        if not self.client:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    def generate_stock_insights(self, stock_data):
        """Generate comprehensive stock insights using Gemini"""
        try:
            # Prepare stock data summary for analysis
            stock_summary = self._prepare_stock_summary(stock_data)
            
            prompt = f"""
            As a professional financial analyst, analyze the following stock data and provide comprehensive insights:

            {stock_summary}

            Please provide:
            1. 3-5 key insights about the company's financial health
            2. Investment recommendation (Buy/Hold/Sell) with reasoning
            3. Risk assessment and key concerns
            4. Growth potential analysis
            5. Comparison with industry standards

            Format your response as a structured analysis that an investor can easily understand.
            """

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            if response.text:
                return self._parse_gemini_response(response.text)
            else:
                return self._get_fallback_analysis()

        except Exception as e:
            print(f"Gemini analysis failed: {e}")
            return self._get_fallback_analysis()
    
    def _prepare_stock_summary(self, stock_data):
        """Prepare stock data summary for Gemini analysis"""
        summary = f"""
        Company: {stock_data.get('company_name', 'N/A')}
        Symbol: {stock_data.get('symbol', 'N/A')}
        Sector: {stock_data.get('sector', 'N/A')}
        Industry: {stock_data.get('industry', 'N/A')}
        
        Current Price: ₹{stock_data.get('current_price', 0):,.2f}
        Market Cap: ₹{stock_data.get('market_cap', 0):,}
        
        Key Ratios:
        - P/E Ratio: {stock_data.get('pe_ratio', 'N/A')}
        - P/B Ratio: {stock_data.get('pb_ratio', 'N/A')}
        - ROE: {stock_data.get('roe', 'N/A')}%
        - ROC: {stock_data.get('roce', 'N/A')}%
        - Debt/Equity: {stock_data.get('debt_to_equity', 'N/A')}
        - Current Ratio: {stock_data.get('current_ratio', 'N/A')}
        
        Financial Performance:
        - Revenue Growth: {stock_data.get('revenue_growth', 'N/A')}%
        - Earnings Growth: {stock_data.get('earnings_growth', 'N/A')}%
        - Profit Margin: {stock_data.get('profit_margins', 'N/A')}%
        - Operating Margin: {stock_data.get('operating_margins', 'N/A')}%
        
        Stock Performance:
        - 52W High: ₹{stock_data.get('fifty_two_week_high', 0):,.2f}
        - 52W Low: ₹{stock_data.get('fifty_two_week_low', 0):,.2f}
        - Dividend Yield: {stock_data.get('dividend_yield', 'N/A')}%
        
        Shareholding:
        - Promoter Holding: {stock_data.get('promoter_holding', 'N/A')}%
        - FII Holding: {stock_data.get('fii_holding', 'N/A')}%
        - DII Holding: {stock_data.get('dii_holding', 'N/A')}%
        """
        return summary
    
    def _parse_gemini_response(self, response_text):
        """Parse Gemini response into structured format"""
        try:
            # Split response into sections
            lines = response_text.strip().split('\n')
            insights = []
            recommendation = "Hold"
            risks = []
            
            current_section = None
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Identify sections
                if "insight" in line.lower() or "key point" in line.lower():
                    current_section = "insights"
                elif "recommendation" in line.lower() or "invest" in line.lower():
                    current_section = "recommendation"
                elif "risk" in line.lower() or "concern" in line.lower():
                    current_section = "risks"
                elif line.startswith('-') or line.startswith('•') or line.startswith('*'):
                    # Extract bullet points
                    clean_line = line.lstrip('- •*').strip()
                    if current_section == "insights" and len(insights) < 5:
                        insights.append(clean_line)
                    elif current_section == "risks" and len(risks) < 3:
                        risks.append(clean_line)
                elif current_section == "recommendation":
                    # Extract recommendation
                    if "buy" in line.lower():
                        recommendation = "Buy"
                    elif "sell" in line.lower():
                        recommendation = "Sell"
                    elif "hold" in line.lower():
                        recommendation = "Hold"
            
            # If parsing didn't work well, extract key sentences
            if len(insights) < 3:
                sentences = response_text.split('. ')
                insights = []
                for sentence in sentences:
                    if len(sentence) > 50 and len(sentence) < 200:
                        insights.append(sentence.strip())
                        if len(insights) >= 5:
                            break
            
            return {
                'insights': insights[:5] if insights else ["Analysis completed successfully"],
                'recommendation': recommendation,
                'risks': risks[:3] if risks else ["Market volatility risk"],
                'analysis_text': response_text
            }
            
        except Exception as e:
            print(f"Error parsing Gemini response: {e}")
            return self._get_fallback_analysis()
    
    def _get_fallback_analysis(self):
        """Provide fallback analysis if Gemini fails"""
        return {
            'insights': [
                "Financial data analysis completed",
                "Stock performance metrics calculated",
                "Market position evaluated"
            ],
            'recommendation': "Hold",
            'risks': ["Market volatility risk"],
            'analysis_text': "AI analysis temporarily unavailable. Please check the financial metrics above for detailed information."
        }