from typing import TypedDict, List, Optional, Annotated
import operator
from langchain_core.prompts import PromptTemplate

class GraphState(TypedDict):
    input: str
    tasks: List[str]
    summaries: Annotated[List[dict], operator.add] 
    report: Optional[str]

summarize_prompt = PromptTemplate.from_template(
    """
    Summarize the following research findings clearly and concisely:

    {info}

    
    """
)
