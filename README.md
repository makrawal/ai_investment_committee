# 🏛️ AI Investment Committee

An AI-powered investment analysis platform that orchestrates multiple specialized agents to deliver holistic, data-backed stock recommendations. The application combines quantitative analysis, risk assessment, and AI-driven portfolio management to provide confident Buy/Sell/Hold verdicts.

---

## Overview

The **AI Investment Committee** simulates an institutional investment process where three AI agents collaborate to analyze stocks:

1. **Quant Analyst** — Fetches real-time financial metrics (price, P/E ratio, revenue growth, 52-week range)
2. **Risk Analyst** — Analyzes latest market news and sentiment using web search
3. **Portfolio Manager (CIO)** — Synthesizes data into a detailed investment memo with a recommendation and confidence score

The system is built on **LangGraph** for orchestration, **FastAPI** for the backend API, and **Streamlit** for an interactive frontend dashboard.

---

## Features

✅ **Real-Time Stock Data** — Pull live metrics from Yahoo Finance  
✅ **Company Metadata** — Display exchange, country, and full company name  
✅ **6-Month Price Chart** — Interactive Streamlit line chart  
✅ **Market Intelligence** — Tavily web search for latest financial news  
✅ **AI-Powered Recommendations** — Buy/Sell/Hold with confidence scoring  
✅ **Detailed Rationale** — Short, human-readable reasoning for each verdict  
✅ **Institutional Grade Memo** — Full 3-paragraph investment analysis  
✅ **Memory & Checkpointing** — LangGraph checkpointing for workflow persistence  

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend (React)               │
│               User input: Stock ticker (e.g., AAPL)         │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP POST /api/analyze
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend Server                    │
│                   LangGraph Workflow                         │
│                                                               │
│  ┌─────────────────┐   ┌──────────────────┐   ┌────────────┐│
│  │ Quant Agent     │──▶│  Risk Agent      │──▶│ PM Agent   ││
│  │ (yfinance)      │   │ (Tavily Search)  │   │ (Gemini)   ││
│  └─────────────────┘   └──────────────────┘   └────────────┘│
│         │       │              │      │            │    │    │
│         ▼       ▼              ▼      ▼            ▼    ▼    │
│    [metrics]  [metadata]  [news]  [sentiment]  [memo] [verdict]
└─────────────────────────────────────────────────────────────┘
                       │ JSON response
                       ▼
┌─────────────────────────────────────────────────────────────┐
│            Frontend Display & Visualization                 │
│  • Listing details (exchange, country, company name)        │
│  • 6-month price trend chart                                │
│  • Color-coded verdict (🟢 BUY, 🔴 SELL, 🟡 HOLD)          │
│  • Confidence score & rationale                             │
│  • Full portfolio manager memo                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | FastAPI, Python | REST API server, orchestration |
| **Orchestration** | LangGraph | Agent workflow & state management |
| **LLM** | Google Gemini 2.5 Flash | AI-powered analysis & recommendations |
| **Financial Data** | yfinance | Real-time stock metrics |
| **Search** | Tavily API | Market news & intelligence |
| **Frontend** | Streamlit | Interactive dashboard UI |
| **Charts** | yfinance + Streamlit | Price visualization |
| **Containerization** | Docker & Docker Compose | Deployment & environment isolation |

---

## Installation & Setup

### Prerequisites

- Python 3.10+
- Docker & Docker Compose (optional, for containerized deployment)
- API Keys:
  - **Google API Key** — For Gemini LLM (create in [Google AI Console](https://aistudio.google.com/app/apikeys))
  - **Tavily API Key** — For financial news search (get from [tavily.com](https://tavily.com))

### Local Setup

#### 1. Clone & Navigate
```bash
cd ai-investment-committee
```

#### 2. Create `.env` File
```bash
# .env file at project root
GOOGLE_API_KEY=your_google_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
BACKEND_URL=http://localhost:8000
```

#### 3. Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
cd ..
```

#### 4. Install Frontend Dependencies
```bash
cd frontend
pip install -r requirements.txt
cd ..
```

#### 5. Run Backend Server
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`  
API docs: `http://localhost:8000/docs`

#### 6. Run Frontend (In a New Terminal)
```bash
cd frontend
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`

---

## Docker Deployment

### Using Docker Compose

```bash
docker-compose up --build
```

This will:
- Build and start the FastAPI backend on port `8000`
- Build and start the Streamlit frontend on port `8501`
- Both services will read from the `.env` file

Access:
- **Backend API**: http://localhost:8000
- **Frontend Dashboard**: http://localhost:8501

### Stop Services
```bash
docker-compose down
```

---

## API Endpoint

### POST `/api/analyze`

Analyze a stock ticker and return a full investment committee verdict.

#### Request
```json
{
  "ticker": "AAPL"
}
```

#### Response
```json
{
  "ticker": "AAPL",
  "company_name": "Apple Inc.",
  "exchange": "NASDAQ",
  "country": "United States",
  "quant_data": "**Company:** Apple Inc.\n\n**Exchange:** NASDAQ\n\n**Country:** United States\n\n**Current Price:** $150.25\n\n**P/E Ratio:** 28.5\n\n**Revenue Growth:** 0.05\n\n**52-Week High:** $199.62\n\n**52-Week Low:** $124.17",
  "news_data": "• Apple's services revenue continues to grow at double-digit rates\n• Regulatory concerns around app store practices remain a headwind\n• Strong iPhone demand in emerging markets supports growth trajectory",
  "memo": "Apple demonstrates solid fundamental strength with consistent revenue growth and a strong balance sheet. The company's services segment provides recurring revenue stability, while recent product launches show continued innovation. However, regulatory headwinds and market saturation in developed regions present near-term risks.",
  "recommendation": "BUY",
  "confidence_score": "82%",
  "rationale": "Strong fundamentals, growing services revenue, and regulatory resilience support upside. Current valuation is reasonable for the growth profile."
}
```

#### Status Codes
- `200` — Success
- `500` — Server error (check backend logs)

---

## Workflow Logic

The application uses **LangGraph** to orchestrate a three-node agent workflow:

```
Quant Agent → Risk Agent → Portfolio Manager Agent → Final Output
```

### Node Details

| Node | Role | Input | Output |
|------|------|-------|--------|
| **quant_agent** | Quantitative Analyst | Ticker symbol | Financial metrics, company metadata |
| **risk_agent** | Risk Analyst | Ticker + metrics context | Market news, sentiment, risk factors |
| **portfolio_manager_agent** | Chief Investment Officer | All prior data | Investment memo, recommendation, confidence, rationale |

### State Graph
```python
CommitteeState = {
    "ticker": str,
    "company_name": str,
    "country": str,
    "exchange": str,
    "quant_data": str,           # Formatted financial metrics
    "news_data": str,            # Risk analyst summary
    "analysis_memo": str,        # Full 3-paragraph memo
    "recommendation": str,       # BUY, SELL, or HOLD
    "confidence_score": str,     # e.g., "82%"
    "rationale": str,            # Key drivers for the verdict
}
```

---

## Frontend Dashboard

The Streamlit interface provides:

1. **Ticker Input** — Search for any publicly traded stock
2. **Verdict Panel** — Color-coded recommendation with confidence and rationale
3. **Listing Details** — Company name, exchange, and country
4. **Quant Metrics** — Real-time financial metrics (P/E, growth, 52-week range)
5. **Price Chart** — Interactive 6-month closing price trend
6. **Risk Analysis** — Market sentiment and key risks from news search
7. **Investment Memo** — Full institutional-grade analysis from the CIO

---

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | API key for Google Generative AI (Gemini) | ✅ |
| `TAVILY_API_KEY` | API key for Tavily web search | ✅ |
| `BACKEND_URL` | Backend server URL (frontend only) | ❌ (default: `http://localhost:8000`) |

### Customization

#### Change LLM Model
Edit `backend/main.py`:
```python
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
```

#### Adjust Search Results
Edit `backend/main.py`:
```python
search_tool = TavilySearch(max_results=5)  # Default is 3
```

#### Modify Chart Period
Edit `frontend/app.py`:
```python
history = stock.history(period="1y")  # Change from "6mo"
```

---

## Troubleshooting

### Backend won't start
- Check that `.env` contains valid API keys
- Verify Python dependencies: `pip install -r backend/requirements.txt`
- Check port 8000 is not in use: `netstat -an | grep 8000`

### Frontend can't connect to backend
- Ensure backend is running on `http://localhost:8000`
- Check `BACKEND_URL` in frontend `.env` matches
- Verify network connectivity between containers (if using Docker)

### API returns 500 error
- Check backend logs for full error details
- Verify API keys have appropriate permissions
- Try a different ticker symbol (may be delisted)

### yfinance data appears as "N/A"
- Not all tickers have complete financial data
- Ticker may be invalid or recently delisted
- Try major stocks like AAPL, MSFT, NVDA

---

## Example Workflow

1. **User Input**: Enter ticker `NVDA`
2. **Quant Agent** fetches current price ($850.25), P/E (65.3), revenue growth (100%)
3. **Risk Agent** searches for NVIDIA news → finds "AI chip demand strong" + "supply chain stable"
4. **Portfolio Manager Agent** synthesizes into a 3-paragraph memo and assigns:
   - Recommendation: **BUY**
   - Confidence: **88%**
   - Rationale: "Dominant AI market position with strong growth profile and improving margins"
5. **Frontend** displays verdict with chart, metrics, and full analysis
6. **User** makes informed investment decision based on holistic analysis

---

## Future Enhancements

- [ ] Portfolio recommendations (multiple stocks)
- [ ] Historical trend analysis & backtesting
- [ ] Competitor comparison
- [ ] Earnings call transcripts & sentiment analysis
- [ ] ESG scoring integration
- [ ] Risk-adjusted return metrics (Sharpe ratio, etc.)
- [ ] Custom alert thresholds
- [ ] User authentication & saved analyses

---

## License

This project is open source. Use and modify as needed.

---

## Support & Feedback

For issues, questions, or suggestions, open an issue or contact the development team.

---

**Version**: 1.0  
**Last Updated**: April 2026
