from langchain_google_genai import ChatGoogleGenerativeAI
from config import settings
from .states import AnalysisPlan, FinalReport
from dotenv import load_dotenv
load_dotenv()
import os

def get_llm():
    return ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        temperature=0.01,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        google_api_key=os.getenv("GEMINI_API_KEY"),
    ).with_structured_output(AnalysisPlan)
    
def get_report_llm():
    return ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        temperature=0.01,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        google_api_key=os.getenv("GEMINI_API_KEY"),
    ).with_structured_output(FinalReport)