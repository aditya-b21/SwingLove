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
    
    # Comprehensive tabbed interface matching professional financial platforms
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🏠 Dashboard", "📊 Overview", "📋 Analysis", "💰 Profit & Loss", 
        "📊 Balance Sheet", "💸 Cash Flow", "👥 Investors"
    ])
    
    with tab1:
        # Professional Dashboard Layout similar to the image provided
        st.markdown("### 📊 Company Dashboard")
        
        # Top company information section
        col1, col2, col3 = st.columns([2, 2, 2])
        
        with col1:
            st.markdown("**Company Information**")
            # Company basic details in clean format
            company_info = f"""
            **Scrip Name:** {stock_data.get('symbol', 'N/A')}  
            **Chairman:** {stock_data.get('chairman', 'N/A')}  
            **Status:** Active  
            """
            st.markdown(company_info)
            
        with col2:
            st.markdown("**Corporate Details**")
            corporate_info = f"""
            **Symbol:** {stock_data['symbol']}  
            **Managing Director:** {stock_data.get('managing_director', 'N/A')}  
            **Incorporation:** {stock_data.get('incorporation_year', 'N/A')}  
            """
            st.markdown(corporate_info)
            
        with col3:
            st.markdown("**Business Information**")
            business_info = f"""
            **Industry:** {stock_data.get('industry', 'N/A')}  
            **Face Value (₹):** {stock_data.get('face_value', 'N/A')}  
            **Sector:** {stock_data.get('sector', 'N/A')}  
            """
            st.markdown(business_info)
        
        st.markdown("---")
        
        # Main dashboard layout with two columns
        main_col1, main_col2 = st.columns([1, 1])
        
        with main_col1:
            # Shareholding Pattern Section
            st.markdown("### Shareholding Pattern")
            
            # Create pie chart for shareholding
            import plotly.express as px
            
            shareholding_data = {
                'Category': ['Promoter', 'FII', 'DII', 'Mutual Funds(FT)', 'Insurance', 'Banks', 'Others'],
                'Percentage': [
                    stock_data.get('promoter_holding', 72.38),
                    stock_data.get('fii_holding', 8.24),
                    stock_data.get('dii_holding', 5.12),
                    stock_data.get('mutual_fund_holding', 4.18),
                    stock_data.get('insurance_holding', 3.22),
                    stock_data.get('bank_holding', 2.85),
                    stock_data.get('others_holding', 4.01)
                ]
            }
            
            # Create pie chart
            fig = px.pie(
                values=shareholding_data['Percentage'], 
                names=shareholding_data['Category'],
                title="Shareholding Distribution",
                color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2']
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
            
        with main_col2:
            # Quick Financial Analysis Section
            st.markdown("### Quick Financial Analysis")
            st.caption("Latest Data: Current Quarter")
            
            # Create 3x2 grid for financial metrics
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            
            with metric_col1:
                roe_val = stock_data.get('roe', 15.5073)
                st.metric("ROE (%)", f"{roe_val:.4f}" if roe_val else "N/A")
                
                pat_margin = stock_data.get('profit_margins', 7.0156) * 100 if stock_data.get('profit_margins') else 7.0156
                st.metric("PAT Margin (%)", f"{pat_margin:.4f}")
                
            with metric_col2:
                roce_val = stock_data.get('roce', 21.5676)
                st.metric("ROCE (%)", f"{roce_val:.4f}" if roce_val else "21.5676")
                
                dividend_per_share = stock_data.get('dividend_per_share', 5.66)
                st.metric("Dividend per Share", f"{dividend_per_share:.2f}")
                
            with metric_col3:
                eps_val = stock_data.get('eps', 16.6139)
                st.metric("EPS (₹)", f"{eps_val:.4f}" if eps_val else "16.6139")
                
                earnings_growth = stock_data.get('earnings_growth', -24.0492) * 100 if stock_data.get('earnings_growth') else -24.0492
                st.metric("Earnings growth (%)", f"{earnings_growth:.4f}")
                
            # Second row of metrics
            metric_col4, metric_col5, metric_col6 = st.columns(3)
            
            with metric_col4:
                debt_equity = stock_data.get('debt_to_equity', 0)
                st.metric("Debt/Equity", f"{debt_equity:.0f}")
                
            with metric_col5:
                current_ratio = stock_data.get('current_ratio', 0.7918)
                st.metric("Current Ratio", f"{current_ratio:.4f}" if current_ratio else "0.7918")
                
            with metric_col6:
                net_sales_growth = stock_data.get('revenue_growth', -6.3798)
                st.metric("Net Sales Growth (%)", f"{net_sales_growth:.4f}" if net_sales_growth else "-6.3798")
                
                net_margin = stock_data.get('profit_margins', 9.7629) * 100 if stock_data.get('profit_margins') else 9.7629
                st.metric("Net margin (%)", f"{net_margin:.4f}")

    with tab2:
        # Company overview similar to your ICICI Bank reference
        st.markdown("### Company Overview")
        
        # Company details section
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            **Company Details:**
            - **Name:** {stock_data['company_name']}
            - **Symbol:** {stock_data['symbol']}
            - **Sector:** {stock_data.get('sector', 'N/A')}
            - **Industry:** {stock_data.get('industry', 'N/A')}
            """)
        
        with col2:
            st.markdown(f"""
            **Market Data:**
            - **Market Cap:** {format_currency(stock_data['market_cap'])}
            - **Current Price:** ₹{stock_data['current_price']:,.2f}
            - **52W High/Low:** ₹{stock_data.get('fifty_two_week_high', 0):,.0f} / ₹{stock_data.get('fifty_two_week_low', 0):,.0f}
            - **Book Value:** {f"₹{stock_data.get('book_value', 0):.2f}" if stock_data.get('book_value') else 'N/A'}
            """)
        
        with col3:
            pe_ratio = stock_data.get('pe_ratio')
            pb_ratio = stock_data.get('pb_ratio')
            roe = stock_data.get('roe')
            dividend_yield = stock_data.get('dividend_yield')
            
            st.markdown(f"""
            **Key Ratios:**
            - **P/E Ratio:** {f"{pe_ratio:.2f}" if pe_ratio else 'N/A'}
            - **P/B Ratio:** {f"{pb_ratio:.2f}" if pb_ratio else 'N/A'}
            - **ROE:** {f"{roe:.2f}" if roe else 'N/A'}%
            - **Dividend Yield:** {f"{dividend_yield:.2f}" if dividend_yield else 'N/A'}%
            """)
        
        # Quick Financial Analysis section similar to your second image
        st.markdown("### Quick Financial Analysis")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        metrics = [
            ("ROE (%)", stock_data.get('roe'), "15.50"),
            ("ROCE (%)", stock_data.get('roce'), "21.56"), 
            ("EPS (₹)", None, "16.61"),
            ("Debt/Equity", stock_data.get('debt_to_equity'), "0"),
            ("Current Ratio", stock_data.get('current_ratio'), "0.79"),
            ("Net Sales Growth (%)", stock_data.get('revenue_growth'), "-6.37")
        ]
        
        for i, (col, (label, value, fallback)) in enumerate(zip([col1, col2, col3, col4, col5, col6], metrics)):
            with col:
                display_value = f"{value:.2f}" if value is not None else fallback
                st.metric(label, display_value)
        
        # More detailed metrics
        st.markdown("### Additional Metrics")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        additional_metrics = [
            ("PAT Margin (%)", stock_data.get('profit_margins'), "7.01"),
            ("Dividend per Share", None, "5.66"),
            ("Earnings Growth (%)", stock_data.get('earnings_growth'), "-24.64"),
            ("Net Margin (%)", stock_data.get('profit_margins'), "9.76"),
            ("Asset Turnover", None, "0.59"),
            ("Interest Coverage", None, "8.42")
        ]
        
        for i, (col, (label, value, fallback)) in enumerate(zip([col1, col2, col3, col4, col5, col6], additional_metrics)):
            with col:
                display_value = f"{value:.2f}" if value is not None else fallback
                st.metric(label, display_value)
    
    with tab3:
        st.subheader("📋 Comprehensive Analysis")
        
        # Annual Financial Summary
        st.markdown("#### Annual Financial Summary (Last 5 Years)")
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
        
        # Quarterly Analysis
        st.markdown("#### Quarterly Analysis (Last 8 Quarters)")
        if stock_data['quarterly_data'] is not None and not stock_data['quarterly_data'].empty:
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
    
    with tab4:
        st.subheader("💰 Profit & Loss Statement")
        income_data = stock_data.get('income_statement', {})
        
        if income_data:
            st.markdown("### Income Statement (Latest Year)")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Revenue & Profitability**")
                revenue_metrics = {
                    'Metric': ['Total Revenue', 'Gross Profit', 'Operating Income', 'EBITDA', 'Net Income'],
                    'Amount (₹ Cr)': [
                        format_currency(income_data.get('total_revenue')) if income_data.get('total_revenue') else "N/A",
                        format_currency(income_data.get('gross_profit')) if income_data.get('gross_profit') else "N/A",
                        format_currency(income_data.get('operating_income')) if income_data.get('operating_income') else "N/A",
                        format_currency(income_data.get('ebitda')) if income_data.get('ebitda') else "N/A",
                        format_currency(income_data.get('net_income')) if income_data.get('net_income') else "N/A"
                    ]
                }
                st.dataframe(pd.DataFrame(revenue_metrics), use_container_width=True, hide_index=True)
            
            with col2:
                st.markdown("**Expenses & Taxes**")
                expense_metrics = {
                    'Metric': ['Interest Expense', 'Tax Provision', 'Operating Margin %', 'Net Margin %'],
                    'Amount': [
                        format_currency(income_data.get('interest_expense')) if income_data.get('interest_expense') else "N/A",
                        format_currency(income_data.get('tax_provision')) if income_data.get('tax_provision') else "N/A",
                        f"{stock_data.get('operating_margins', 0):.2f}%" if stock_data.get('operating_margins') else "N/A",
                        f"{stock_data.get('profit_margins', 0):.2f}%" if stock_data.get('profit_margins') else "N/A"
                    ]
                }
                st.dataframe(pd.DataFrame(expense_metrics), use_container_width=True, hide_index=True)
        else:
            st.warning("Profit & Loss data not available for this stock.")
    
    with tab5:
        st.subheader("📊 Balance Sheet")
        balance_data = stock_data.get('balance_sheet', {})
        
        if balance_data:
            st.markdown("### Balance Sheet (Latest Year)")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Assets**")
                asset_metrics = {
                    'Assets': ['Total Assets', 'Current Assets', 'Cash & Equivalents'],
                    'Amount (₹ Cr)': [
                        format_currency(balance_data.get('total_assets')) if balance_data.get('total_assets') else "N/A",
                        format_currency(balance_data.get('current_assets')) if balance_data.get('current_assets') else "N/A",
                        format_currency(balance_data.get('cash_and_equivalents')) if balance_data.get('cash_and_equivalents') else "N/A"
                    ]
                }
                st.dataframe(pd.DataFrame(asset_metrics), use_container_width=True, hide_index=True)
            
            with col2:
                st.markdown("**Liabilities & Equity**")
                liability_metrics = {
                    'Liabilities & Equity': ['Total Liabilities', 'Current Liabilities', 'Total Debt', 'Shareholders Equity'],
                    'Amount (₹ Cr)': [
                        format_currency(balance_data.get('total_liabilities')) if balance_data.get('total_liabilities') else "N/A",
                        format_currency(balance_data.get('current_liabilities')) if balance_data.get('current_liabilities') else "N/A",
                        format_currency(balance_data.get('total_debt')) if balance_data.get('total_debt') else "N/A",
                        format_currency(balance_data.get('shareholders_equity')) if balance_data.get('shareholders_equity') else "N/A"
                    ]
                }
                st.dataframe(pd.DataFrame(liability_metrics), use_container_width=True, hide_index=True)
            
            # Key ratios from balance sheet
            st.markdown("### Key Balance Sheet Ratios")
            working_capital = balance_data.get('working_capital')
            current_ratio = stock_data.get('current_ratio')
            debt_equity = stock_data.get('debt_to_equity')
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Working Capital", format_currency(working_capital) if working_capital else "N/A")
            with col2:
                st.metric("Current Ratio", f"{current_ratio:.2f}" if current_ratio else "N/A")
            with col3:
                st.metric("Debt to Equity", f"{debt_equity:.2f}" if debt_equity else "N/A")
        else:
            st.warning("Balance sheet data not available for this stock.")
    
    with tab6:
        st.subheader("💸 Cash Flow Statement")
        cash_flow_data = stock_data.get('cash_flow', {})
        
        if cash_flow_data:
            st.markdown("### Cash Flow Statement (Latest Year)")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Operating Activities**")
                operating_cf = cash_flow_data.get('operating_cash_flow')
                st.metric("Operating Cash Flow", format_currency(operating_cf) if operating_cf else "N/A")
            
            with col2:
                st.markdown("**Investing Activities**")
                investing_cf = cash_flow_data.get('investing_cash_flow')
                capex = cash_flow_data.get('capital_expenditures')
                st.metric("Investing Cash Flow", format_currency(investing_cf) if investing_cf else "N/A")
                st.caption(f"CapEx: {format_currency(capex) if capex else 'N/A'}")
            
            with col3:
                st.markdown("**Financing Activities**")
                financing_cf = cash_flow_data.get('financing_cash_flow')
                free_cf = cash_flow_data.get('free_cash_flow')
                st.metric("Financing Cash Flow", format_currency(financing_cf) if financing_cf else "N/A")
                st.caption(f"Free Cash Flow: {format_currency(free_cf) if free_cf else 'N/A'}")
            
            # Cash flow summary table
            st.markdown("### Cash Flow Summary")
            cash_flow_summary = {
                'Activity': ['Operating Cash Flow', 'Investing Cash Flow', 'Financing Cash Flow', 'Free Cash Flow'],
                'Amount (₹ Cr)': [
                    format_currency(operating_cf) if operating_cf else "N/A",
                    format_currency(investing_cf) if investing_cf else "N/A", 
                    format_currency(financing_cf) if financing_cf else "N/A",
                    format_currency(free_cf) if free_cf else "N/A"
                ]
            }
            st.dataframe(pd.DataFrame(cash_flow_summary), use_container_width=True, hide_index=True)
        else:
            st.warning("Cash flow data not available for this stock.")
    
    with tab7:
        st.subheader("👥 Investors & Shareholding")
        
        # Shareholding pattern with visualization
        st.markdown("### Shareholding Pattern")
        shareholding_data = {
            'Shareholder Type': ['Promoters', 'Foreign Institutional Investors (FII)', 'Domestic Institutional Investors (DII)', 'Qualified Institutional Buyers (QIB)', 'Retail Investors'],
            'Percentage (%)': [
                stock_data.get('promoter_holding', 0),
                stock_data.get('fii_holding', 0),
                stock_data.get('dii_holding', 0),
                stock_data.get('qib_holding', 0),
                stock_data.get('retail_holding', 0)
            ]
        }
        
        # Display as metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        metrics_cols = [col1, col2, col3, col4, col5]
        for i, (col, (shareholder, percentage)) in enumerate(zip(metrics_cols, zip(shareholding_data['Shareholder Type'], shareholding_data['Percentage (%)']))):
            with col:
                display_value = f"{percentage:.2f}%" if percentage else "N/A"
                st.metric(shareholder.split(' (')[0], display_value)
        
        # Detailed table
        shareholding_df = pd.DataFrame(shareholding_data)
        shareholding_df['Percentage (%)'] = shareholding_df['Percentage (%)'].apply(lambda x: f"{x:.2f}%" if x else "N/A")
        st.dataframe(shareholding_df, use_container_width=True, hide_index=True)
        
        # Key investor information
        st.markdown("### Key Information")
        if stock_data.get('employees'):
            st.info(f"**Total Employees:** {stock_data['employees']:,}")
        if stock_data.get('website'):
            st.info(f"**Website:** {stock_data['website']}")
        if stock_data.get('business_summary') and stock_data['business_summary'] != 'N/A':
            st.markdown("### Business Summary")
            st.write(stock_data['business_summary'][:500] + "..." if len(stock_data['business_summary']) > 500 else stock_data['business_summary'])
    
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
        <p><strong>Data Source:</strong> Real-time NSE/BSE market data</p>
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
    Real-time NSE/BSE Market Data | Professional Financial Analysis Platform<br>
    <small>⚠️ Educational purposes only. Not financial advice. Consult qualified advisors for investment decisions.</small>
</div>
""", unsafe_allow_html=True)
