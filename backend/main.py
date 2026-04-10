import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()
import yfinance as yf
from typing import TypedDict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
#from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_tavily import TavilySearch
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.output_parsers import StrOutputParser

# 1. API Setup
app = FastAPI(title="Investment Committee API")

# Ensure API keys are loaded (these will be passed via Docker)
llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview", temperature=0)
search_tool = TavilySearch(max_results=3)

class PMDecision(BaseModel):
    analysis_memo: str = Field(description="A 3-paragraph investment memo.")
    recommendation: str = Field(description="Must be strictly: BUY, SELL, or HOLD.")

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
    
    price = info.get("currentPrice", "N/A")
    pe = info.get("trailingPE", "N/A")
    growth = info.get("revenueGrowth", "N/A")
    week_52_high = info.get("fiftyTwoWeekHigh", "N/A")
    week_52_low = info.get("fiftyTwoWeekLow", "N/A")
    
    # Format beautifully for the frontend
    md = f"**Current Price:** ${price}\n\n**P/E Ratio:** {pe}\n\n**Revenue Growth:** {growth}\n\n**52-Week High:** {week_52_high}\n\n**52-Week Low:** {week_52_low}"
    return {"quant_data": md}

def risk_agent(state: CommitteeState):
    """Uses the LLM to convert messy JSON search results into human-readable bullets."""
    query = f"latest financial news and risks for {state['ticker']} stock"
    raw_search = search_tool.invoke({"query": query})
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Risk Analyst. Read this raw search data and summarize the current market sentiment and risks into 3 concise bullet points. Do NOT output JSON."),
        ("user", "Raw Data:\n{data}")
    ])
    
    # We add StrOutputParser() to the end to strip away all the metadata and guarantee a clean string
    chain = prompt | llm | StrOutputParser()
    clean_text = chain.invoke({"data": str(raw_search)})
    
    return {"news_data": clean_text}

def portfolio_manager_agent(state: CommitteeState):
    """Uses structured output to guarantee a Buy/Sell/Hold verdict."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a CIO. Synthesize this data into a 3-paragraph investment memo. You MUST also provide a definitive Buy, Sell, or Hold recommendation."),
        ("user", "Ticker: {ticker}\nQuant: {quant}\nNews: {news}")
    ])
    
    # Force the LLM to return our Pydantic model
    pm_llm = prompt | llm.with_structured_output(PMDecision)
    result = pm_llm.invoke({
        "ticker": state["ticker"], "quant": state["quant_data"], "news": state["news_data"]
    })
    
    return {
        "analysis_memo": result.analysis_memo, 
        "recommendation": result.recommendation
    }

# 3. Compile Graph
workflow = StateGraph(CommitteeState)
workflow.add_node("quant", quant_agent)
workflow.add_node("risk", risk_agent)
workflow.add_node("pm", portfolio_manager_agent)
workflow.set_entry_point("quant")
workflow.add_edge("quant", "risk")
workflow.add_edge("risk", "pm")
workflow.add_edge("pm", END)

memory = MemorySaver()
agent_app = workflow.compile(checkpointer=memory)

# --- FASTAPI ENDPOINTS ---
class AnalysisRequest(BaseModel):
    ticker: str

@app.post("/api/analyze")
async def run_analysis(request: AnalysisRequest):
    try:
        config = {"configurable": {"thread_id": f"run_{request.ticker}"}}
        initial_state = {"ticker": request.ticker.upper()}
        
        final_state = agent_app.invoke(initial_state, config=config)
        return {
            "ticker": final_state["ticker"],
            "quant_data": final_state.get("quant_data"),
            "news_data": final_state.get("news_data"),
            "memo": final_state.get("analysis_memo"),
            "recommendation": final_state.get("recommendation") # Send verdict to frontend
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))