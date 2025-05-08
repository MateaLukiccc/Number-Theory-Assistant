from fastapi import FastAPI, UploadFile, HTTPException
import uvicorn
from app.agents.orchestrator import workflow

app = FastAPI()


@app.post("/upload_chall")
async def get_challenge_file(file: UploadFile):
    if not file.filename.endswith(".py"):
        raise HTTPException(status_code=400, detail="Only .py files are allowed.")
    
    contents: str = await file.read()
    initial_state = {
        "challenge": contents
    }

    try:
        final_state = workflow.invoke(initial_state)
        return {
        "filename": file.filename,
        "thoughts":              final_state.get("thoughts"),
        "next_agents":           final_state.get("next_agents"),
        "final_answer":          final_state.get("final_answer"),
        "error":                 final_state.get("error"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "OK"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)