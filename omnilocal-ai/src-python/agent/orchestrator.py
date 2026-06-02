from langchain_classic.agents import AgentExecutor, create_react_agent
from .brain import get_llm, get_system_prompt
from .tools import get_tools
from langchain_core.prompts import PromptTemplate

def initialize_agent():
    """
    Sets up the ReAct agent with tools and the LLM.
    """
    llm = get_llm()
    tools = get_tools()
    
    # We use a standard ReAct prompt but inject our system instructions
    template = (
        "{system_instructions}\n\n"
        "TOOLS:\n"
        "------\n"
        "You have access to the following tools:\n"
        "{tools}\n\n"
        "To use a tool, please use the following format:\n"
        "```\n"
        "Thought: Do I need to use a tool? Yes\n"
        "Action: the action to take, should be one of [{tool_names}]\n"
        "Action Input: the input to the action\n"
        "Observation: the result of the action\n"
        "```\n\n"
        "When you have a response for the user, or if you do not need to use a tool, you MUST use the format:\n"
        "```\n"
        "Thought: Do I need to use a tool? No\n"
        "Final Answer: [your response here]\n"
        "```\n\n"
        "Begin!\n\n"
        "New input: {input}\n"
        "{agent_scratchpad}"
    )

    prompt = PromptTemplate.from_template(template).partial(
        system_instructions=get_system_prompt()
    )

    agent = create_react_agent(llm, tools, prompt)
    
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5  # Prevent infinite loops
    )
