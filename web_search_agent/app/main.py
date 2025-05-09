from fastapi import FastAPI
from graph.workflow import app as workflow
from pydantic import BaseModel

app = FastAPI()

class CodeRequest(BaseModel):
    code: str

@app.post("/analyze")
async def analyze_code(request: CodeRequest):
    state = {
        "messages": [],
        "code_to_analyze": request.code
    }
    async for event in workflow.astream(state):
        if "report" in event:
            return {"report": event["report"]["reports"]}
    
    return {"error": "Analysis failed"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)