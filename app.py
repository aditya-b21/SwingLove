import streamlit as st
import pandas as pd
from datetime import datetime
import time
from stock_data import StockDataFetcher
from ai_analysis import AIAnalyzer
from utils import format_currency, format_percentage, validate_stock_symbol

# Page configuration
st.set_page_config(
    page_title="AI Stock Analysis Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_stock_data' not in st.session_state:
    st.session_state.current_stock_data = None
if 'current_analysis' not in st.session_state:
    st.session_state.current_analysis = None

# Initialize services
@st.cache_resource
def get_stock_fetcher():
    return StockDataFetcher()

@st.cache_resource
def get_ai_analyzer():
    return AIAnalyzer()

stock_fetcher = get_stock_fetcher()
ai_analyzer = get_ai_analyzer()

# Main header
st.title("🤖 AI Stock Analysis Assistant")
st.markdown("---")

# Chat interface
st.subheader("💬 Ask me to analyze any stock")

# Chat input
user_input = st.chat_input("Type a stock name or symbol (e.g., 'Analyze stock: INFY' or 'TCS')")

# Process new user input
if user_input:
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    # Extract stock symbol from user input
    stock_symbol = validate_stock_symbol(user_input)
    
    if stock_symbol:
        # Add processing message
        st.session_state.chat_history.append({"role": "assistant", "content": f"🔍 Analyzing {stock_symbol}..."})
        
        try:
            # Fetch stock data
            stock_data = stock_fetcher.get_comprehensive_data(stock_symbol)
            st.session_state.current_stock_data = stock_data
            
            # Generate AI analysis
            analysis = ai_analyzer.analyze_stock(stock_data)
            st.session_state.current_analysis = analysis
            
            # Update last message with success
            st.session_state.chat_history[-1] = {
                "role": "assistant", 
                "content": f"✅ Analysis complete for {stock_data['company_name']} ({stock_symbol}). See detailed results below."
            }
            
        except Exception as e:
            # Update last message with error
            st.session_state.chat_history[-1] = {
                "role": "assistant", 
                "content": f"❌ Error analyzing {stock_symbol}: {str(e)}"
            }
    else:
        # Invalid symbol
        st.session_state.chat_history.append({
            "role": "assistant", 
            "content": "❌ Please enter a valid stock symbol like 'TCS', 'INFY', or 'Reliance'."
        })

# Display chat history
for message in st.session_state.chat_history:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.write(message["content"])
    else:
        with st.chat_message("assistant"):
            st.write(message["content"])

# Display analysis results if available
if st.session_state.current_stock_data and st.session_state.current_analysis:
    stock_data = st.session_state.current_stock_data
    analysis = st.session_state.current_analysis
    
    st.markdown("---")
    st.header(f"📊 Analysis: {stock_data['company_name']} ({stock_data['symbol']})")
    
    # Comprehensive stock overview
    st.markdown("### 📈 Key Metrics Overview")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        price_change = ""
        if stock_data.get('year_performance'):
            color = "green" if stock_data['year_performance'] > 0 else "red"
            price_change = f"<span style='color:{color}'>({stock_data['year_performance']:+.2f}% YTD)</span>"
        st.metric("Current Price", f"₹{stock_data['current_price']:.2f}")
        st.markdown(price_change, unsafe_allow_html=True)
        
    with col2:
        st.metric("Market Cap", format_currency(stock_data['market_cap']))
        if stock_data.get('employees'):
            st.caption(f"Employees: {stock_data['employees']:,}")
            
    with col3:
        st.metric("P/E Ratio", f"{stock_data['pe_ratio']:.2f}" if stock_data.get('pe_ratio') else "N/A")
        if stock_data.get('pb_ratio'):
            st.caption(f"P/B: {stock_data['pb_ratio']:.2f}")
            
    with col4:
        st.metric("52W High", f"₹{stock_data['fifty_two_week_high']:.2f}" if stock_data.get('fifty_two_week_high') else "N/A")
        if stock_data.get('fifty_two_week_low'):
            st.caption(f"52W Low: ₹{stock_data['fifty_two_week_low']:.2f}")
            
    with col5:
        st.metric("ROE (%)", f"{stock_data['roe']:.2f}" if stock_data.get('roe') else "N/A")
        if stock_data.get('dividend_yield'):
            st.caption(f"Div Yield: {stock_data['dividend_yield']:.2f}%")
    
    # Company info section
    if stock_data.get('sector') != 'N/A' or stock_data.get('industry') != 'N/A':
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**Sector:** {stock_data.get('sector', 'N/A')}")
        with col2:
            st.info(f"**Industry:** {stock_data.get('industry', 'N/A')}")
        with col3:
            st.info(f"**Country:** {stock_data.get('country', 'India')}")
    
    # Tabbed interface for detailed analysis
    tab1, tab2, tab3, tab4 = st.tabs(["📁 Financial Summary", "📁 Quarterly Analysis", "📁 Key Ratios", "📁 Shareholding Pattern"])
    
    with tab1:
        st.subheader("Financial Summary (Last 5-10 Years)")
        if stock_data['annual_data'] is not None and not stock_data['annual_data'].empty:
            # Format the annual data for display
            annual_display = stock_data['annual_data'].copy()
            if 'Total Revenue' in annual_display.columns:
                annual_display['Total Revenue'] = annual_display['Total Revenue'].apply(lambda x: format_currency(x) if pd.notna(x) else "N/A")
            if 'Net Income' in annual_display.columns:
                annual_display['Net Income'] = annual_display['Net Income'].apply(lambda x: format_currency(x) if pd.notna(x) else "N/A")
            if 'EPS' in annual_display.columns:
                annual_display['EPS'] = annual_display['EPS'].apply(lambda x: f"₹{x:.2f}" if pd.notna(x) else "N/A")
            
            st.dataframe(annual_display, use_container_width=True)
        else:
            st.warning("Annual financial data not available for this stock.")
    
    with tab2:
        st.subheader("Quarterly Analysis (Last 10 Quarters)")
        if stock_data['quarterly_data'] is not None and not stock_data['quarterly_data'].empty:
            # Format the quarterly data for display
            quarterly_display = stock_data['quarterly_data'].copy()
            if 'Total Revenue' in quarterly_display.columns:
                quarterly_display['Total Revenue'] = quarterly_display['Total Revenue'].apply(lambda x: format_currency(x) if pd.notna(x) else "N/A")
            if 'Net Income' in quarterly_display.columns:
                quarterly_display['Net Income'] = quarterly_display['Net Income'].apply(lambda x: format_currency(x) if pd.notna(x) else "N/A")
            if 'EPS' in quarterly_display.columns:
                quarterly_display['EPS'] = quarterly_display['EPS'].apply(lambda x: f"₹{x:.2f}" if pd.notna(x) else "N/A")
            
            st.dataframe(quarterly_display, use_container_width=True)
        else:
            st.warning("Quarterly financial data not available for this stock.")
    
    with tab3:
        st.subheader("Key Financial Ratios")
        
        # Main ratios
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Valuation Ratios**")
            valuation_data = {
                'Ratio': ['P/E Ratio', 'P/B Ratio', 'Price-to-Sales', 'EV/Revenue', 'EV/EBITDA'],
                'Value': [
                    f"{stock_data['pe_ratio']:.2f}" if stock_data.get('pe_ratio') else "N/A",
                    f"{stock_data['pb_ratio']:.2f}" if stock_data.get('pb_ratio') else "N/A",
                    f"{stock_data['price_to_sales']:.2f}" if stock_data.get('price_to_sales') else "N/A",
                    f"{stock_data['ev_to_revenue']:.2f}" if stock_data.get('ev_to_revenue') else "N/A",
                    f"{stock_data['ev_to_ebitda']:.2f}" if stock_data.get('ev_to_ebitda') else "N/A"
                ]
            }
            st.dataframe(pd.DataFrame(valuation_data), use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("**Financial Health Ratios**")
            health_data = {
                'Ratio': ['ROE (%)', 'ROCE (%)', 'Current Ratio', 'Quick Ratio', 'Debt-to-Equity'],
                'Value': [
                    f"{stock_data['roe']:.2f}" if stock_data.get('roe') else "N/A",
                    f"{stock_data['roce']:.2f}" if stock_data.get('roce') else "N/A",
                    f"{stock_data['current_ratio']:.2f}" if stock_data.get('current_ratio') else "N/A",
                    f"{stock_data['quick_ratio']:.2f}" if stock_data.get('quick_ratio') else "N/A",
                    f"{stock_data['debt_to_equity']:.2f}" if stock_data.get('debt_to_equity') else "N/A"
                ]
            }
            st.dataframe(pd.DataFrame(health_data), use_container_width=True, hide_index=True)
        
        # Performance metrics
        st.markdown("**Performance & Growth Metrics**")
        performance_data = {
            'Metric': ['Profit Margin (%)', 'Operating Margin (%)', 'Revenue Growth (%)', 'Earnings Growth (%)', 'Dividend Yield (%)', '1Y Performance (%)'],
            'Value': [
                f"{stock_data['profit_margins']:.2f}" if stock_data.get('profit_margins') else "N/A",
                f"{stock_data['operating_margins']:.2f}" if stock_data.get('operating_margins') else "N/A",
                f"{stock_data['revenue_growth']:.2f}" if stock_data.get('revenue_growth') else "N/A",
                f"{stock_data['earnings_growth']:.2f}" if stock_data.get('earnings_growth') else "N/A",
                f"{stock_data['dividend_yield']:.2f}" if stock_data.get('dividend_yield') else "N/A",
                f"{stock_data['year_performance']:.2f}" if stock_data.get('year_performance') else "N/A"
            ]
        }
        st.dataframe(pd.DataFrame(performance_data), use_container_width=True, hide_index=True)
    
    with tab4:
        st.subheader("Shareholding Pattern (Latest)")
        shareholding_data = {
            'Shareholder Type': ['Promoters', 'FII (Foreign Institutional)', 'DII (Domestic Institutional)', 'QIB (Qualified Institutional)', 'Retail Investors'],
            'Percentage (%)': [
                f"{stock_data['promoter_holding']:.2f}" if stock_data['promoter_holding'] else "N/A",
                f"{stock_data['fii_holding']:.2f}" if stock_data['fii_holding'] else "N/A",
                f"{stock_data['dii_holding']:.2f}" if stock_data['dii_holding'] else "N/A",
                f"{stock_data['qib_holding']:.2f}" if stock_data['qib_holding'] else "N/A",
                f"{stock_data['retail_holding']:.2f}" if stock_data['retail_holding'] else "N/A"
            ]
        }
        shareholding_df = pd.DataFrame(shareholding_data)
        st.dataframe(shareholding_df, use_container_width=True, hide_index=True)
    
    # AI Analysis Section
    st.markdown("---")
    st.header("🤖 AI-Generated Analysis")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("💡 Key Insights")
        if analysis['insights']:
            for i, insight in enumerate(analysis['insights'], 1):
                st.write(f"**{i}.** {insight}")
        else:
            st.info("No specific insights available for this stock.")
    
    with col2:
        st.subheader("📈 Investment Implication")
        if analysis['investment_summary']:
            st.write(analysis['investment_summary'])
        else:
            st.info("Investment analysis not available for this stock.")
    
    # Clear analysis button
    if st.button("🔄 Clear Analysis", type="secondary"):
        st.session_state.current_stock_data = None
        st.session_state.current_analysis = None
        st.session_state.chat_history = []
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666666; font-size: 12px;'>
    AI Stock Analysis Assistant | Data sources: Yahoo Finance, AI-powered insights | 
    Disclaimer: This is for educational purposes only. Not financial advice.
</div>
""", unsafe_allow_html=True)
