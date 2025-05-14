from typing import TypedDict, List, Optional, Annotated, Dict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel

class AnalysisPlan(BaseModel):
    writeup_searches: List[str]
    vulnerability_searches: List[str]

class FinalReport(BaseModel):
    main_concern: str
    detailed_report: str
    recommended_resources: str
    vulnerability_type: str
    mathematical_weakness: str
    key_insight: str
    steps: List[str]

class WebAgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    code_to_analyze: Optional[str]
    analysis_plan: Optional[AnalysisPlan]
    search_results: Optional[dict]
    reports: Dict[str, str]