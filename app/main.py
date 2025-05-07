from fastapi import FastAPI, UploadFile, HTTPException
import uvicorn

app = FastAPI()


@app.post("/upload_chall")
async def get_challenge_file(file: UploadFile):
    if not file.filename.endswith(".py"):
        raise HTTPException(status_code=400, detail="Only .py files are allowed.")
    
    contents: str = await file.read()
    return {"filename": file.filename, "contents": contents}

@app.get("/health")
def health_check():
    return {"status": "OK"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)