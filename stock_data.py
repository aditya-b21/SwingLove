import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import os

class StockDataFetcher:
    def __init__(self):
        self.session = requests.Session()
        # Add headers to avoid blocking
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_indian_symbol(self, symbol):
        """Convert symbol to Indian stock market format"""
        symbol = symbol.upper().strip()
        
        # If already has .NS or .BO, return as is
        if symbol.endswith('.NS') or symbol.endswith('.BO'):
            return symbol
        
        # Common Indian stock symbols
        indian_symbols = {
            'TCS': 'TCS.NS',
            'INFY': 'INFY.NS',
            'INFOSYS': 'INFY.NS',
            'RELIANCE': 'RELIANCE.NS',
            'HDFCBANK': 'HDFCBANK.NS',
            'HDFC': 'HDFCBANK.NS',
            'ITC': 'ITC.NS',
            'SBIN': 'SBIN.NS',
            'SBI': 'SBIN.NS',
            'BHARTIARTL': 'BHARTIARTL.NS',
            'AIRTEL': 'BHARTIARTL.NS',
            'ICICIBANK': 'ICICIBANK.NS',
            'ICICI': 'ICICIBANK.NS',
            'LT': 'LT.NS',
            'LARSEN': 'LT.NS',
            'HCLTECH': 'HCLTECH.NS',
            'HCL': 'HCLTECH.NS',
            'WIPRO': 'WIPRO.NS',
            'ONGC': 'ONGC.NS',
            'NTPC': 'NTPC.NS',
            'POWERGRID': 'POWERGRID.NS',
            'COALINDIA': 'COALINDIA.NS',
            'MARUTI': 'MARUTI.NS',
            'BAJFINANCE': 'BAJFINANCE.NS',
            'BAJAJ': 'BAJFINANCE.NS',
            'SUNPHARMA': 'SUNPHARMA.NS',
            'DRREDDY': 'DRREDDY.NS',
            'NESTLEIND': 'NESTLEIND.NS',
            'NESTLE': 'NESTLEIND.NS',
            'HINDUNILVR': 'HINDUNILVR.NS',
            'HUL': 'HINDUNILVR.NS',
            'ULTRACEMCO': 'ULTRACEMCO.NS',
            'ADANIPORTS': 'ADANIPORTS.NS',
            'ADANI': 'ADANIPORTS.NS'
        }
        
        if symbol in indian_symbols:
            return indian_symbols[symbol]
        
        # Try with .NS first (NSE), then .BO (BSE)
        return f"{symbol}.NS"
    
    def get_comprehensive_data(self, symbol):
        """Fetch comprehensive stock data"""
        try:
            # Convert to proper Indian symbol format
            formatted_symbol = self.get_indian_symbol(symbol)
            
            # Get stock info using yfinance
            stock = yf.Ticker(formatted_symbol)
            info = stock.info
            
            # Validate if stock exists
            if not info or 'symbol' not in info:
                # Try with .BO if .NS failed
                if formatted_symbol.endswith('.NS'):
                    formatted_symbol = formatted_symbol.replace('.NS', '.BO')
                    stock = yf.Ticker(formatted_symbol)
                    info = stock.info
                
                if not info or 'symbol' not in info:
                    raise ValueError(f"Stock symbol '{symbol}' not found. Please check the symbol and try again.")
            
            # Get historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365 * 10)  # 10 years
            
            # Fetch historical data with retry logic
            hist_data = None
            for attempt in range(3):
                try:
                    hist_data = stock.history(start=start_date, end=end_date)
                    if not hist_data.empty:
                        break
                except Exception as e:
                    if attempt == 2:
                        print(f"Failed to fetch historical data after 3 attempts: {e}")
                    time.sleep(1)
            
            # Get financial data
            annual_data = self._get_annual_financials(stock)
            quarterly_data = self._get_quarterly_financials(stock)
            
            # Compile comprehensive data
            stock_data = {
                'symbol': formatted_symbol,
                'company_name': info.get('longName', info.get('shortName', symbol)),
                'current_price': info.get('currentPrice', info.get('regularMarketPrice', 0)),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', None),
                'roe': self._calculate_roe(info),
                'roce': self._calculate_roce(info),
                'debt_to_equity': info.get('debtToEquity', None),
                'dividend_yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else None,
                'current_ratio': info.get('currentRatio', None),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh', None),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow', None),
                'promoter_holding': self._get_promoter_holding(info),
                'fii_holding': self._get_fii_holding(info),
                'dii_holding': self._get_dii_holding(info),
                'qib_holding': self._get_qib_holding(info),
                'retail_holding': self._get_retail_holding(info),
                'annual_data': annual_data,
                'quarterly_data': quarterly_data,
                'historical_data': hist_data,
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return stock_data
            
        except Exception as e:
            raise Exception(f"Error fetching data for {symbol}: {str(e)}")
    
    def _get_annual_financials(self, stock):
        """Get annual financial data"""
        try:
            # Get financial statements
            financials = stock.financials
            balance_sheet = stock.balance_sheet
            
            if financials.empty:
                return pd.DataFrame()
            
            # Prepare annual data
            annual_data = []
            
            for year in financials.columns:
                year_str = year.strftime('%Y') if hasattr(year, 'strftime') else str(year)
                
                annual_record = {
                    'Year': year_str,
                    'Total Revenue': financials.loc['Total Revenue', year] if 'Total Revenue' in financials.index else None,
                    'Net Income': financials.loc['Net Income', year] if 'Net Income' in financials.index else None,
                    'EPS': self._calculate_eps(financials, year),
                    'Total Assets': balance_sheet.loc['Total Assets', year] if not balance_sheet.empty and 'Total Assets' in balance_sheet.index else None,
                    'Total Debt': balance_sheet.loc['Total Debt', year] if not balance_sheet.empty and 'Total Debt' in balance_sheet.index else None
                }
                annual_data.append(annual_record)
            
            return pd.DataFrame(annual_data).head(10)  # Last 10 years
            
        except Exception as e:
            print(f"Error getting annual financials: {e}")
            return pd.DataFrame()
    
    def _get_quarterly_financials(self, stock):
        """Get quarterly financial data"""
        try:
            # Get quarterly financials
            quarterly_financials = stock.quarterly_financials
            
            if quarterly_financials.empty:
                return pd.DataFrame()
            
            # Prepare quarterly data
            quarterly_data = []
            
            for quarter in quarterly_financials.columns:
                quarter_str = quarter.strftime('%Y-Q%q') if hasattr(quarter, 'strftime') else str(quarter)
                
                quarterly_record = {
                    'Quarter': quarter_str,
                    'Total Revenue': quarterly_financials.loc['Total Revenue', quarter] if 'Total Revenue' in quarterly_financials.index else None,
                    'Net Income': quarterly_financials.loc['Net Income', quarter] if 'Net Income' in quarterly_financials.index else None,
                    'EPS': self._calculate_eps(quarterly_financials, quarter)
                }
                quarterly_data.append(quarterly_record)
            
            return pd.DataFrame(quarterly_data).head(10)  # Last 10 quarters
            
        except Exception as e:
            print(f"Error getting quarterly financials: {e}")
            return pd.DataFrame()
    
    def _calculate_eps(self, financials, period):
        """Calculate EPS from financial data"""
        try:
            net_income = financials.loc['Net Income', period] if 'Net Income' in financials.index else None
            shares_outstanding = financials.loc['Basic Average Shares', period] if 'Basic Average Shares' in financials.index else None
            
            if net_income is not None and shares_outstanding is not None and shares_outstanding != 0:
                return net_income / shares_outstanding
            return None
        except Exception:
            return None
    
    def _calculate_roe(self, info):
        """Calculate Return on Equity"""
        try:
            return info.get('returnOnEquity', None) * 100 if info.get('returnOnEquity') else None
        except Exception:
            return None
    
    def _calculate_roce(self, info):
        """Calculate Return on Capital Employed"""
        try:
            return info.get('returnOnAssets', None) * 100 if info.get('returnOnAssets') else None
        except Exception:
            return None
    
    def _get_promoter_holding(self, info):
        """Extract promoter holding percentage"""
        try:
            # This data might not be directly available in yfinance
            # You would need additional data sources for accurate shareholding patterns
            return info.get('heldPercentInstitutions', None) * 100 if info.get('heldPercentInstitutions') else None
        except Exception:
            return None
    
    def _get_fii_holding(self, info):
        """Extract FII holding percentage"""
        try:
            return info.get('heldPercentInstitutions', None) * 100 if info.get('heldPercentInstitutions') else None
        except Exception:
            return None
    
    def _get_dii_holding(self, info):
        """Extract DII holding percentage"""
        try:
            # Placeholder - would need specialized data source
            return None
        except Exception:
            return None
    
    def _get_qib_holding(self, info):
        """Extract QIB holding percentage"""
        try:
            # Placeholder - would need specialized data source
            return None
        except Exception:
            return None
    
    def _get_retail_holding(self, info):
        """Extract retail holding percentage"""
        try:
            held_by_institutions = info.get('heldPercentInstitutions', 0)
            held_by_insiders = info.get('heldPercentInsiders', 0)
            retail_holding = 100 - (held_by_institutions * 100) - (held_by_insiders * 100)
            return max(0, retail_holding)
        except Exception:
            return None
