from agents.financials_agent import run_financials_agent
from agents.sentiment_agent import run_sentiment_agent
from agents.catalyst_agent import run_catalyst_agent
from agents.valuation_agent import run_valuation_agent
from agents.risk_agent import run_risk_agent

def route_task(task: str, index: int) -> dict:
    task_lower = task.lower()
    
    if any(x in task_lower for x in ["financial", "revenue", "eps", "p/e", "earnings"]):
        return run_financials_agent(task, index)
    elif any(x in task_lower for x in ["sentiment", "analyst", "bullish", "news"]):
        return run_sentiment_agent(task, index)
    elif any(x in task_lower for x in ["catalyst", "event", "product launch", "investor day", "earnings call"]):
        return run_catalyst_agent(task, index)
    elif any(x in task_lower for x in ["valuation", "peers", "compare", "ev/ebitda"]):
        return run_valuation_agent(task, index)
    elif any(x in task_lower for x in ["risk", "lawsuit", "regulatory", "downside", "investigation"]):
        return run_risk_agent(task, index)
    elif any(x in task_lower for x in ["industry", "sector", "macro", "trends", "market landscape"]):
        return run_valuation_agent(task, index) 
    else:
        return {
            "task": task,
            "summary": "No specialized agent matched. Task was skipped.",
            "type": "unknown",
            "confidence": "Low",
            "sources": []
        }