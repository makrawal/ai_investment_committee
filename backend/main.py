import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()
import yfinance as yf
from typing import TypedDict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
#from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_tavily import TavilySearch
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# 1. API Setup
app = FastAPI(title="Investment Committee API")

# Ensure API keys are loaded (these will be passed via Docker)
llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview", temperature=0)
search_tool = TavilySearch(max_results=3)

# 2. Graph State & Nodes (Same logic as before)
class CommitteeState(TypedDict):
    ticker: str
    quant_data: str
    news_data: str
    analysis_memo: str
    recommendation: str # Buy, Sell, or Hold

def quant_agent(state: CommitteeState):
    """Fetches real-time financial metrics using yfinance."""
    ticker_sym = state["ticker"]
    stock = yf.Ticker(ticker_sym)
    info = stock.info
    
    # Extracting a subset of key metrics
    metrics = {
        "Price": info.get("currentPrice"),
        "P/E Ratio": info.get("trailingPE"),
        "52 Week High": info.get("fiftyTwoWeekHigh"),
        "52 Week Low": info.get("fiftyTwoWeekLow"),
        "Revenue Growth": info.get("revenueGrowth")
    }
    
    data_str = f"Financial Metrics for {ticker_sym}: {str(metrics)}"
    return {"quant_data": data_str}

def risk_agent(state: CommitteeState):
    query = f"latest financial news and risks for {state['ticker']} stock"
    
    # The new TavilySearch returns a JSON string instead of a list of dictionaries.
    search_results = search_tool.invoke({"query": query})
    
    # We skip the complex parsing and just pass the raw JSON text directly to the LLM!
    return {"news_data": str(search_results)}

def portfolio_manager_agent(state: CommitteeState):
    """Synthesizes data and writes the final memo."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Chief Investment Officer. Synthesize the Quantitative data and Risk data provided into a professional 3-paragraph investment memo."),
        ("user", "Ticker: {ticker}\n\nQuant Data: {quant}\n\nRisk/News Data: {news}")
    ])
    
    chain = prompt | llm
    result = chain.invoke({
        "ticker": state["ticker"],
        "quant": state["quant_data"],
        "news": state["news_data"]
    })
    
    return {"analysis_memo": result.content}

# 3. Compile Graph
workflow = StateGraph(CommitteeState)

workflow.add_node("quant", quant_agent)
workflow.add_node("risk", risk_agent)
workflow.add_node("pm", portfolio_manager_agent)

workflow.set_entry_point("quant")
workflow.add_edge("quant", "risk")
workflow.add_edge("risk", "pm")
workflow.add_edge("pm", END)

# Adding memory for state persistence
memory = MemorySaver()
agent_app = workflow.compile(checkpointer=memory)


# 4. FastAPI Endpoints
class AnalysisRequest(BaseModel):
    ticker: str

@app.post("/api/analyze")
async def run_analysis(request: AnalysisRequest):
    try:
        config = {"configurable": {"thread_id": f"run_{request.ticker}"}}
        initial_state = {"ticker": request.ticker.upper()}
        
        # Run graph synchronously for the API response
        final_state = agent_app.invoke(initial_state, config=config)
        return {
            "ticker": final_state["ticker"],
            "quant_data": final_state.get("quant_data"),
            "news_data": final_state.get("news_data"),
            "memo": final_state.get("analysis_memo")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))