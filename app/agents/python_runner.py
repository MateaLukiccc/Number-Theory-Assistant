from langsmith import traceable
from app.tools.docker_execute import execute_code_in_docker
from app.agents.orchestrator import AgentState


@traceable(name="CodeExecutionAgent.execute")
def execute_code_node(state: AgentState) -> AgentState:
    code = state.get("code")
    if not code:
        state["error"] = "No code provided to execute."
        return state

    try:
        return execute_code_in_docker(code)
    except Exception as e:
        state["error"] = f"Code execution failed: {e}"

    return state