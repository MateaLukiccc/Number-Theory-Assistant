import aiohttp
import asyncio
from typing import Dict
from langchain_core.tools import tool
from app.core.states import AnalysisPlan
from dotenv import load_dotenv
load_dotenv()
import os

@tool("analyze_code_with_llm")
async def analyze_code_with_llm(code: str) -> AnalysisPlan:
    """Use LLM to identify important fragments and search terms"""
    from app.core.llm import get_llm
    from langchain_core.prompts import ChatPromptTemplate
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
You are a CTF assistant helping users analyze RSA-based challenge code from Capture The Flag competitions.

Your task is to:
1. Analyze the provided RSA challenge code.
2. Identify specific search terms (keywords, phrases, function names, libraries, or techniques) that can be used to find relevant writeups of similar challenges online.
3. Identify general vulnerability concepts or cryptographic weaknesses involved in the code that are commonly exploited in CTFs in rsa.

Return your findings in the following JSON format:
{{
    "writeup_searches\": ["term1", "term2", "term3"],
    "vulnerability_searches": ["vuln1", "vuln2", "vuln3"]
}}
"""),
("user", "{code}")
    ])
    chain = prompt | get_llm()
    response = await chain.ainvoke({"code": code})
    return {"plan": response}

async def search_web(session: aiohttp.ClientSession, query: str) -> Dict:
    async with session.get(
        "https://www.googleapis.com/customsearch/v1",
        params={
            "q": query,
            "cx": "82a174a0e50a94816",
            "key": os.getenv("GOOGLE_SEARCH"),
            "num": 3
        }
    ) as resp:
        return await resp.json()

@tool("execute_security_searches")
async def execute_security_searches(plan: AnalysisPlan) -> Dict:
    """Execute all planned searches concurrently"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        
        for term in plan.writeup_searches:
            tasks.append(search_web(session, f"{term}"))
        
        for term in plan.vulnerability_searches:
            tasks.append(search_web(session, f"{term}"))
        
        results = await asyncio.gather(*tasks)
        res = []
        try:
            for kind in results:
                for type_search in kind["items"]:
                    res.append(f"{type_search["title"]}, {type_search["link"]}")
        except Exception as e:
            print(results)
            print(e)

    return {
        "code_analysis": res[:3], 
        "vulnerability_research": res[3:]
    }

tools = [analyze_code_with_llm, execute_security_searches]
tools_by_name = {tool.name: tool for tool in tools}