import json
from typing import List, TypedDict
from langgraph.graph import StateGraph, END
from app.tools.llm import call_gemini
from langsmith import traceable
from app.prompts.orchestrator_prompt import return_orchestrator_prompt
from app.agents.web_agent import web_workflow

class AgentState(TypedDict, total=False):
    challenge: str
    thoughts: str
    next_agents: List[str]
    code: str
    final_answer: str
    search_results: str
    error: str

@traceable(name="OrchestratorAgent.orchestrate")
def orchestrator_node(state: AgentState) -> AgentState:
    # initial api request that asks LLM what agents/tools should be used
    # also it returns code to be used if code_execution tool is to be used
    prompt = return_orchestrator_prompt(state["challenge"])
    raw = call_gemini(prompt)
    print("[Orchestrator LLM] Raw response:", raw)
    
    try:
        plan = json.loads(raw)
        # save LLM thought process for user ui while he waits for other agent processes to finish
        state["thoughts"] = plan.get("thoughts", "")
        
        agents_from_plan = plan.get("next_agents")
        processed_next_agents: List[str] = []
        if isinstance(agents_from_plan, str):
            # json loads extracts str if there is only one element in an array
            processed_next_agents = [agents_from_plan]
        elif isinstance(agents_from_plan, list):
            processed_next_agents = agents_from_plan
        else:
            print(f"[Orchestrator LLM] Warning: 'next_agents' from LLM had unexpected type: {type(agents_from_plan)}. Defaulting to empty list.")
            processed_next_agents = []
        
        # Ensure web_search_agent is always added 
        if "web_search_agent" not in processed_next_agents:
            processed_next_agents.append("web_search_agent")
        state["next_agents"] = processed_next_agents
        
        # here should be code for exececution if code_execute is selected
        state["code"] = plan.get("code", "")
    except json.JSONDecodeError as e:
        print(f"[Orchestrator LLM] Error parsing JSON: {e}")
        state["error"] = f"Failed to parse LLM JSON: {e}"
        state["next_agents"] = ["Final"]
    return state

def planning_node(state: AgentState) -> AgentState:
    print("[PlanningAgent] (stub) planning would run here.")
    return state

async def run_web_search(state: AgentState):
    print("[WebSearch] Running web_search_agent.")
    
    web_state = {
        "messages": [],
        "code_to_analyze": state["challenge"]
    }
    result = None
    async for event in web_workflow.astream(web_state):
        print(f"[WebSearch] Received event: {event.keys()}")
        if "reports" in event:
            result = event["reports"]
            break
        elif "report" in event and "reports" in event["report"]:
            result = event["report"]["reports"]
            break
    if result:
        return {"search_results": result}
    else:
        return {"search_results": "[Error] Analysis completed but no report found"}

def search_node(state: AgentState) -> AgentState:
    import asyncio
    # Create a new event loop for this thread if one doesn't exist
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        # If we're in a thread without an event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # Run the coroutine in this event loop
    try:
        result = loop.run_until_complete(run_web_search(state))
        return result
    except Exception as e:
        print(f"[WebSearch] Error in search_node: {e}")
        return {"search_results": f"[Error] Web search failed: {e}"}

def execute_code_node(state: AgentState) -> AgentState:
    from app.agents.python_runner import execute_code_node as exe
    # partial state update because of concurrent jobs
    print("entered execute")
    a = exe(state)
    print("executed results:", a)
    return {"final_answer": a} 

def final_node(state: AgentState) -> AgentState:
    print("[FinalNode] Terminating.")
    print(f"Final Answer: {state.get('final_answer')}")
    print(f"Search Results: {state.get('search_results')}")
    print(f"Thoughts: {state.get('thoughts')}")
    return state

def decide_next_step(state: AgentState) -> str:
    #agents = state.get("next_agents").split(",") or []
    next_tasks = state.get("next_agents", [])
    print(f"[DecideNextStep] Next agents determined by orchestrator: {next_tasks}")
    if next_tasks:
        # Check if both web_search and code_execution are requested
        run_search = "web_search_agent" in next_tasks
        run_code = "code_execution_agent" in next_tasks

        tasks_to_run_parallel = []
        if run_search:
            tasks_to_run_parallel.append("WebSearch")
        if run_code:
            # Ensure code exists if we are trying to execute it
            if not state.get("code"):
                print("[DecideNextStep] Code execution requested, but no code found. Skipping.")
            else:
                tasks_to_run_parallel.append("ExecuteCode")
        if "planning_agent" in next_tasks and "Planning" not in tasks_to_run_parallel:
             tasks_to_run_parallel.append("Planning")

        if tasks_to_run_parallel:
            print(f"[DecideNextStep] Returning tasks for parallel/sequential execution: {tasks_to_run_parallel}")
            return tasks_to_run_parallel 

        if "Final" in next_tasks or not tasks_to_run_parallel :
             return END
    if state.get("error"):
        print("[DecideNextStep] Error detected, going to Final.")
        return END
    if state.get("final_answer") and state.get("search_results"): 
        print("[DecideNextStep] Final answer and search results present, going to Final.")
        return END
    print("[DecideNextStep] No specific next tasks or conditions met, going to END as fallback.")
    return END

# This node will act as a join point
def gather_results_node(state: AgentState) -> AgentState:
    print("[GatherResultsNode] Gathering results from parallel tasks.")
    return state

workflow = StateGraph(AgentState)
workflow.add_node("Orchestrate", orchestrator_node)
workflow.add_node("Planning", planning_node)
workflow.add_node("ExecuteCode", execute_code_node)
workflow.add_node("WebSearch", search_node)
workflow.add_node("GatherResults", gather_results_node)
workflow.add_node("Final", final_node)

workflow.set_entry_point("Orchestrate")

workflow.add_conditional_edges(
    "Orchestrate",
    decide_next_step
)

workflow.add_edge("WebSearch", "GatherResults")
workflow.add_edge("ExecuteCode", "GatherResults")
workflow.add_edge("Planning", "GatherResults")
workflow.add_edge("GatherResults", END)

workflow = workflow.compile()