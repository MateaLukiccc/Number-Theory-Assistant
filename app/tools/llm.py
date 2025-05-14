from google import genai
from google.genai import types
from app.models.dtos import OrchestratorOutput
import os
from dotenv import load_dotenv

load_dotenv()
def call_gemini(prompt: str, model_name: str = "gemini-2.0-flash") -> str:
    client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
    response = client.models.generate_content(
        model=model_name,
        contents=[
            types.Content(
                parts=[
                    {"text": prompt},
                ],
                role="user"
            )
        ],
        config={
        "response_mime_type": "application/json",
        "response_schema": OrchestratorOutput,
        }
    )
    return response.text