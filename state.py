from typing import TypedDict, List, Optional, Annotated
import operator
from langchain_core.prompts import PromptTemplate
from typing import List, Dict, Optional, TypedDict

class State(TypedDict):
    input: str
    tasks: List[str]
    summaries: List[Dict]
    final_output: Optional[str]