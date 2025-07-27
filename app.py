import streamlit as st
import pandas as pd
from datetime import datetime
import time
from stock_data import StockDataFetcher
from ai_analysis import AIAnalyzer
from utils import format_currency, format_percentage, validate_stock_symbol

# Page configuration
st.set_page_config(
    page_title="InvestIQ - AI Stock Analysis Platform",
    page_icon="💹",
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

# Custom CSS for modern financial UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    .feature-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid #e9ecef;
    }
    .market-status {
        background: #28a745;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        display: inline-block;
        margin: 0.5rem 0;
    }
    .footer-info {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 2rem;
        text-align: center;
        color: #6c757d;
    }
</style>
""", unsafe_allow_html=True)

# Professional main header
st.markdown("""
<div class="main-header">
    <h1>💹 InvestIQ</h1>
    <h3>Professional AI-Powered Stock Analysis Platform</h3>
    <p>Real-time financial data • Advanced analytics • AI-driven insights</p>
    <div class="market-status">🟢 Markets Open • Real-time Data</div>
</div>
""", unsafe_allow_html=True)

# Key features showcase
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="feature-card">
        <h4>📊 Real-time Data</h4>
        <p>Live stock prices, financial ratios, and market metrics from NSE/BSE</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <h4>🤖 AI Analysis</h4>
        <p>Advanced AI-powered investment insights and recommendations</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <h4>📈 Comprehensive Metrics</h4>
        <p>42+ financial indicators including valuation, growth, and risk metrics</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="feature-card">
        <h4>💼 Professional Reports</h4>
        <p>Detailed quarterly analysis, shareholding patterns, and performance tracking</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Market overview section
st.markdown("### 📈 Start Your Analysis")
st.markdown("Enter any Indian stock symbol or company name to get comprehensive analysis:")

# Popular stocks quick access
st.markdown("**Popular Stocks:**")
col1, col2, col3, col4, col5 = st.columns(5)
popular_stocks = ['TCS', 'INFY', 'RELIANCE', 'HDFCBANK', 'ICICIBANK']

for i, (col, stock) in enumerate(zip([col1, col2, col3, col4, col5], popular_stocks)):
    with col:
        if st.button(f"📊 {stock}", key=f"quick_{stock}", use_container_width=True):
            st.session_state['quick_analysis'] = stock

# Chat interface
st.subheader("💬 AI Stock Analysis Chat")

# Enhanced chat input
user_input = st.chat_input("💼 Enter stock symbol or company name (e.g., 'TCS', 'Infosys', 'RELIANCE.NS')")

# Handle quick analysis buttons
if 'quick_analysis' in st.session_state:
    user_input = st.session_state['quick_analysis']
    del st.session_state['quick_analysis']

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
    
    # Professional stock header with company branding
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); 
                padding: 2rem; border-radius: 15px; color: white; margin: 2rem 0;">
        <h2>🏢 {stock_data['company_name']}</h2>
        <h4>Symbol: {stock_data['symbol']} | {stock_data.get('sector', 'N/A')} Sector</h4>
        <p>{stock_data.get('industry', 'N/A')} • {stock_data.get('country', 'India')}</p>
    </div>
    """, unsafe_allow_html=True)

    # Advanced metrics dashboard
    st.markdown("### 📊 Real-Time Market Data")
    
    # Price and performance row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        price_change = ""
        delta_color = "normal"
        if stock_data.get('year_performance'):
            delta_color = "normal" if stock_data['year_performance'] > 0 else "inverse"
            change_text = f"{stock_data['year_performance']:+.2f}% YTD"
        else:
            change_text = None
        st.metric("Current Price", f"₹{stock_data['current_price']:,.2f}", 
                 delta=change_text, delta_color=delta_color)
        
    with col2:
        st.metric("Market Cap", format_currency(stock_data['market_cap']))
        if stock_data.get('employees'):
            st.caption(f"👥 {stock_data['employees']:,} employees")
            
    with col3:
        st.metric("P/E Ratio", f"{stock_data['pe_ratio']:.2f}" if stock_data.get('pe_ratio') else "N/A")
        if stock_data.get('pb_ratio'):
            st.caption(f"P/B: {stock_data['pb_ratio']:.2f}")
            
    with col4:
        st.metric("52W Range", 
                 f"₹{stock_data['fifty_two_week_high']:,.2f}" if stock_data.get('fifty_two_week_high') else "N/A")
        if stock_data.get('fifty_two_week_low'):
            st.caption(f"Low: ₹{stock_data['fifty_two_week_low']:,.2f}")
            
    with col5:
        st.metric("ROE", f"{stock_data['roe']:.1f}%" if stock_data.get('roe') else "N/A")
        if stock_data.get('dividend_yield'):
            st.caption(f"🎯 Div: {stock_data['dividend_yield']:.2f}%")
    
    # Key financial indicators
    if any([stock_data.get('profit_margins'), stock_data.get('revenue_growth'), stock_data.get('debt_to_equity')]):
        st.markdown("### 💼 Financial Health Indicators")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            profit_margin = stock_data.get('profit_margins')
            if profit_margin:
                color = "🟢" if profit_margin > 15 else "🟡" if profit_margin > 5 else "🔴"
                st.metric("Profit Margin", f"{profit_margin:.1f}%", delta=f"{color}")
            else:
                st.metric("Profit Margin", "N/A")
                
        with col2:
            revenue_growth = stock_data.get('revenue_growth')
            if revenue_growth:
                color = "🟢" if revenue_growth > 10 else "🟡" if revenue_growth > 0 else "🔴"
                st.metric("Revenue Growth", f"{revenue_growth:.1f}%", delta=f"{color}")
            else:
                st.metric("Revenue Growth", "N/A")
                
        with col3:
            debt_eq = stock_data.get('debt_to_equity')
            if debt_eq:
                color = "🟢" if debt_eq < 0.5 else "🟡" if debt_eq < 1 else "🔴"
                st.metric("Debt/Equity", f"{debt_eq:.2f}", delta=f"{color}")
            else:
                st.metric("Debt/Equity", "N/A")
                
        with col4:
            current_ratio = stock_data.get('current_ratio')
            if current_ratio:
                color = "🟢" if current_ratio > 1.5 else "🟡" if current_ratio > 1 else "🔴"
                st.metric("Current Ratio", f"{current_ratio:.2f}", delta=f"{color}")
            else:
                st.metric("Current Ratio", "N/A")
    
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

# Add professional footer and showcase when no analysis is displayed
if not st.session_state.current_stock_data:
    st.markdown("---")
    
    # Sample analysis showcase
    st.markdown("### 🔍 What You'll Get")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📊 Comprehensive Financial Analysis:**
        - Real-time stock prices and market data
        - 42+ key financial metrics and ratios
        - Year-over-year performance tracking
        - Quarterly earnings analysis
        - Shareholding pattern breakdown
        """)
        
    with col2:
        st.markdown("""
        **🤖 AI-Powered Insights:**
        - Investment recommendations
        - Risk assessment analysis
        - Growth potential evaluation
        - Market trend analysis
        - Professional investment thesis
        """)
    
    # Market status and timing
    current_time = datetime.now()
    st.markdown(f"""
    <div class="footer-info">
        <h4>📈 Market Information</h4>
        <p><strong>NSE & BSE Data:</strong> Real-time during market hours (9:15 AM - 3:30 PM IST)</p>
        <p><strong>Current Time:</strong> {current_time.strftime('%Y-%m-%d %H:%M:%S')} IST</p>
        <p><strong>Data Source:</strong> Yahoo Finance API • <strong>AI Analysis:</strong> Together AI & Groq</p>
        <br>
        <small>⚠️ <strong>Disclaimer:</strong> This is for educational purposes only. Not financial advice. 
        Please consult a qualified financial advisor for investment decisions.</small>
    </div>
    """, unsafe_allow_html=True)

# Professional footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666666; font-size: 12px; padding: 1rem;'>
    <strong>InvestIQ</strong> - Professional AI Stock Analysis Platform<br>
    Data Sources: Yahoo Finance API | AI Analysis: Together AI & Groq | Real-time NSE/BSE Data<br>
    <small>⚠️ Educational purposes only. Not financial advice. Consult qualified advisors for investment decisions.</small>
</div>
""", unsafe_allow_html=True)
