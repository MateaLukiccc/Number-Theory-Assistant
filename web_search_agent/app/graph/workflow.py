from langgraph.graph import StateGraph
from core.states import AgentState
from core.tools import analyze_code_with_llm, execute_security_searches
from langfuse.decorators import observe

from dotenv import load_dotenv
load_dotenv()

async def plan_analysis(state: AgentState):
    if not state.get("code_to_analyze"):
        return {}
    plan = await analyze_code_with_llm.ainvoke(state["code_to_analyze"])
    state["analysis_plan"] = plan
    return state

async def execute_searches(state: AgentState):
    if not state.get("analysis_plan"):
        return {}
    results = await execute_security_searches.ainvoke(state["analysis_plan"])
    state["search_results"] = results
    return state

@observe
async def generate_report(state: AgentState):
    from core.llm import get_report_llm
    from langchain_core.prompts import ChatPromptTemplate
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
Analyze this RSA CTF challenge. Based on the code and search results, identify:

Challenge type 
The specific RSA vulnerability/weakness present
Step-by-step solution method with required formulas
Reference some online resources that are given in the search results
Also provide references to writeups if they are provided in web search results

Keep your analysis focused and practical for a CTF solver.
Search results: {results}
"""),
("user", "{code}")
    ])
    
    chain = prompt | get_report_llm()
    report = await chain.ainvoke({
        "code": state["code_to_analyze"],
        "results": state["search_results"]
    })
    state["reports"] = report
    return state

workflow = StateGraph(AgentState)
workflow.add_node("plan", plan_analysis)
workflow.add_node("search", execute_searches)
workflow.add_node("report", generate_report)

workflow.set_entry_point("plan")

workflow.add_edge("plan", "search")
workflow.add_edge("search", "report")

app = workflow.compile()