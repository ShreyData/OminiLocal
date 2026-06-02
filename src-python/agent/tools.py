from langchain_community.tools import DuckDuckGoSearchRun
from langchain_experimental.tools import PythonREPLTool

def get_tools():
    """
    Returns the list of tools available to the agent.
    """
    search = DuckDuckGoSearchRun()
    python_repl = PythonREPLTool()
    
    # We can customize descriptions to help the LLM understand when to use them
    search.description = "Use this to search the internet for real-time information or news."
    python_repl.description = "Use this to execute Python code for math, data analysis, or logic."
    
    return [search, python_repl]
