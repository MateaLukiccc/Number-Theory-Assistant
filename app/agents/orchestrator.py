import json
from typing import List, TypedDict
from langgraph.graph import StateGraph
from app.tools.llm import call_gemini
from langsmith import traceable
from app.prompts.orchestrator_prompt import return_orchestrator_prompt

class AgentState(TypedDict, total=False):
    challenge: str
    thoughts: str
    next_agents: List[str]
    code: str
    final_answer: str
    error: str

@traceable(name="OrchestratorAgent.orchestrate")
def orchestrator_node(state: AgentState) -> AgentState:
    prompt = return_orchestrator_prompt(state["challenge"])
    raw = call_gemini(prompt)
    print("[Orchestrator LLM] Raw response:", raw)
    
    try:
        plan = json.loads(raw)
        state["thoughts"] = plan.get("thoughts", "")
        state["next_agents"] = plan.get("next_agents", [])
        state["code"] = plan.get("code", "")
    except json.JSONDecodeError as e:
        state["error"] = f"Failed to parse LLM JSON: {e}"
        state["next_agents"] = []

    return state


def planning_node(state: AgentState) -> AgentState:
    print("[PlanningAgent] (stub) planning would run here.")
    return state


def execute_code_node(state: AgentState) -> AgentState:
    from app.agents.python_runner import execute_code_node
    state["final_answer"] = execute_code_node(state)
    return state


def final_node(state: AgentState) -> AgentState:
    print("[FinalNode] terminating.")
    return state


def decide_next_step(state: AgentState) -> str:
    agents = state.get("next_agents").split(",") or []
    if "planning_agent" in agents:
        return "Planning"
    if "code_execution_agent" in agents:
        return "ExecuteCode"
    if state.get("final_answer"):
        return "Final"
    # Fallback to Final to avoid infinite loops
    return "Final"


workflow = StateGraph(AgentState)
workflow.add_node("Orchestrate", orchestrator_node)
workflow.add_node("Planning", planning_node)
workflow.add_node("ExecuteCode", execute_code_node)
workflow.add_node("Final", final_node)

workflow.set_entry_point("Orchestrate")
workflow.add_conditional_edges(
    "Orchestrate",
    decide_next_step,
    {
        "Planning": "Planning",
        "ExecuteCode": "ExecuteCode",
        "Final": "Final"
    }
)

workflow = workflow.compile()