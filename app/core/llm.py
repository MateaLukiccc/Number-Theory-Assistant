from langchain_google_genai import ChatGoogleGenerativeAI
from .states import AnalysisPlan, FinalReport
from dotenv import load_dotenv
load_dotenv()
import os

class Settings:
    LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
    LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
    LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

settings = Settings()

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