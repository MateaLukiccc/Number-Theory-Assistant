from pydantic import BaseModel

class OrchestratorOutput(BaseModel):
    thoughts: str
    next_agents: str
    should_execute_code: bool
    code: str
    final_answer: str