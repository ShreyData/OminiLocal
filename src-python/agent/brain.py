import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

def get_llm():
    """
    Returns an LLM instance. 
    If GEMINI_API_KEY is present in .env, it uses the Google Gemini API (Gemma 4).
    Otherwise, it falls back to local Ollama.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    
    if api_key:
        print("Using Cloud Mode: Gemini API (gemma-4-26b-a4b-it)")
        return ChatGoogleGenerativeAI(
            model="gemma-4-26b-a4b-it",
            google_api_key=api_key,
            temperature=0,
            streaming=True
        )
    else:
        print("Using Local Mode: Ollama (gemma4:e4b)")
        return ChatOllama(
            model="gemma4:e4b",
            temperature=0,
            streaming=True
        )

def get_system_prompt():
    """
    Provides the core system instructions for the agent.
    Focuses on ReAct reasoning, tool usage, and strict formatting.
    """
    return (
        "You are OmniLocal AI, a high-performance assistant.\n"
        "You have access to a web search tool and a Python interpreter.\n"
        "Follow these rules strictly:\n"
        "1. **Sequential Reasoning**: If a task requires search then calculation, do them in order.\n"
        "2. **Formatting**: ALWAYS use **bold** for key terms, *italics* for emphasis, and ### headers for sections.\n"
        "3. **Tables**: If you have more than 3 data points to compare, use a Markdown table.\n"
        "4. **Python**: When using the Python REPL, show the code you wrote in your thought process.\n"
        "5. **Sources**: Cite your search sources if applicable.\n"
        "6. **Directness**: Be concise but thorough."
    )
