# AI Stock Analysis Assistant - Replit Configuration

## Overview

This is a Streamlit-based AI stock analysis application that provides comprehensive financial analysis of Indian stocks. The application fetches real-time stock data using Yahoo Finance (yfinance), performs AI-powered analysis using multiple LLM providers (Together AI and Groq), and presents the information through an interactive chat interface.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application
- **Interface**: Chat-based UI with tabbed data presentation
- **State Management**: Streamlit session state for chat history and current analysis data
- **Styling**: Custom CSS with Indian market focus (₹ currency formatting)

### Backend Architecture
- **Main Application**: `app.py` - Streamlit app orchestrating the entire workflow
- **Data Layer**: `stock_data.py` - Stock data fetching and processing
- **AI Layer**: `ai_analysis.py` - AI-powered analysis generation
- **Utilities**: `utils.py` - Helper functions for formatting and validation

### Data Processing Pipeline
1. User input parsing and stock symbol extraction
2. Stock data fetching from Yahoo Finance
3. AI analysis generation with fallback providers
4. Data formatting and presentation in structured tabs

## Key Components

### Stock Data Fetcher (`stock_data.py`)
- **Purpose**: Fetches comprehensive stock data from Yahoo Finance
- **Features**: 
  - Indian stock symbol mapping (e.g., TCS → TCS.NS)
  - Historical and real-time data retrieval
  - Error handling with retry mechanisms
  - Rate limiting protection with custom headers

### AI Analyzer (`ai_analysis.py`)
- **Purpose**: Generates intelligent stock analysis using LLM APIs
- **Provider Strategy**: Primary (Together AI) with fallback (Groq)
- **Fallback Mechanism**: Basic analysis generation if AI services fail
- **Analysis Structure**: Structured insights with financial interpretation

### Utility Functions (`utils.py`)
- **Stock Symbol Validation**: Regex-based pattern matching for various input formats
- **Currency Formatting**: Indian currency display (₹, Crore, Lakh notation)
- **Percentage Formatting**: Standardized percentage display with proper handling of null values

### Main Application (`app.py`)
- **Chat Interface**: Streamlit chat components with message history
- **Session Management**: Persistent chat history and analysis caching
- **Service Initialization**: Cached resource initialization for performance
- **Error Handling**: Graceful degradation with user feedback

## Data Flow

1. **User Input**: Natural language queries through chat interface
2. **Symbol Extraction**: Regex-based parsing to identify stock symbols
3. **Data Fetching**: Yahoo Finance API calls with Indian market symbol mapping
4. **AI Processing**: LLM analysis with structured prompt engineering
5. **Response Generation**: Formatted presentation in chat with tabbed data views
6. **State Persistence**: Chat history and analysis caching in session state

## External Dependencies

### APIs and Services
- **Yahoo Finance**: Primary data source via `yfinance` library
- **Together AI**: Primary LLM provider for analysis generation
- **Groq AI**: Secondary LLM provider for fallback scenarios

### Python Libraries
- **streamlit**: Web application framework
- **yfinance**: Yahoo Finance data fetching
- **pandas**: Data manipulation and analysis
- **requests**: HTTP client for API calls

### Environment Variables
- `TOGETHER_API_KEY`: Together AI API authentication
- `GROQ_API_KEY`: Groq AI API authentication (fallback)

## Deployment Strategy

### Platform Considerations
- **Target Platform**: Replit deployment environment
- **Runtime**: Python 3.x with pip package management
- **Environment Setup**: Environment variables for API keys
- **Resource Management**: Streamlit caching for performance optimization

### Configuration Requirements
1. Set API keys in Replit environment variables
2. Install required packages via requirements.txt or pip
3. Configure Streamlit settings for optimal performance
4. Set up session state management for multi-user scenarios

### Performance Optimizations
- **Caching**: Streamlit resource caching for service initialization
- **Session State**: Efficient state management for chat persistence
- **Error Handling**: Graceful fallbacks to ensure application stability
- **Rate Limiting**: Built-in protections for external API calls

### Security Considerations
- API keys stored as environment variables
- No sensitive data persistence beyond session scope
- Input validation to prevent injection attacks
- Rate limiting to prevent API abuse

## Architecture Decisions Rationale

### Multi-Provider AI Strategy
- **Problem**: Single AI provider reliability and availability
- **Solution**: Primary/fallback architecture with Together AI and Groq
- **Benefits**: Increased uptime, cost optimization, performance diversity

### Indian Market Focus
- **Problem**: Generic stock analysis doesn't cater to Indian market specifics
- **Solution**: Custom symbol mapping and currency formatting
- **Benefits**: Better user experience for Indian investors

### Chat-Based Interface
- **Problem**: Complex financial data can be overwhelming
- **Solution**: Conversational interface with structured data presentation
- **Benefits**: Improved accessibility and user engagement

### Streamlit Framework Choice
- **Problem**: Need for rapid development and deployment
- **Solution**: Streamlit for quick prototyping with rich UI components
- **Benefits**: Fast development cycle, built-in state management, easy deployment