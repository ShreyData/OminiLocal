from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from .state import AgentState
from .brain import get_llm, get_system_prompt
from .tools import get_tools

def architect_node(state: AgentState):
    """
    Decides whether to use tools or proceed to formatting.
    """
    llm = get_llm()
    tools = get_tools()
    llm_with_tools = llm.bind_tools(tools)
    
    system_prompt = get_system_prompt()
    # Prepend system prompt to the messages
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    
    response = llm_with_tools.invoke(messages)
    
    next_step = "format"
    if hasattr(response, "tool_calls") and response.tool_calls:
        next_step = "tools"
        
    return {
        "messages": [response],
        "next_step": next_step
    }

def tools_node(state: AgentState):
    """
    Executes tool calls requested by the architect.
    """
    messages = state["messages"]
    last_message = messages[-1]
    
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        return {"next_step": "architect"}
        
    tools = get_tools()
    tool_map = {tool.name: tool for tool in tools}
    
    new_messages = []
    research_append = ""
    
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        
        # Find the tool in our map
        tool = tool_map.get(tool_name)
        if tool:
            # Execute tool - handling potential dict input if LLM passes it
            if isinstance(tool_args, dict) and len(tool_args) == 1:
                # Many tools take a single string arg, but LLM passes it as a dict
                input_val = list(tool_args.values())[0]
            else:
                input_val = tool_args
                
            try:
                result = tool.invoke(input_val)
            except Exception as e:
                result = f"Error executing tool: {str(e)}"
        else:
            result = f"Tool '{tool_name}' not found."
            
        new_messages.append(ToolMessage(
            tool_call_id=tool_call["id"],
            content=str(result)
        ))
        research_append += f"\nTool: {tool_name}\nInput: {tool_args}\nOutput: {result}\n"
        
    return {
        "messages": new_messages,
        "research_data": (state.get("research_data") or "") + research_append,
        "next_step": "architect"
    }

def stylist_node(state: AgentState):
    """
    Formats the final research into a polished answer.
    """
    llm = get_llm()
    research_data = state.get("research_data", "")
    
    # Extract the original question from the message history
    user_question = "the user's request"
    for m in state["messages"]:
        if isinstance(m, HumanMessage):
            user_question = m.content
            break
            
    system_instructions = (
        "You are a professional analyst and stylist. Your ONLY goal is to take the raw research data and the user's question and create a perfectly formatted answer.\n"
        "Rules: Use bold, italics, ### headers, and Markdown tables for comparisons.\n"
        "Do not mention the tools or research process, just give the final answer."
    )
    
    human_content = (
        f"User Question: {user_question}\n\n"
        f"Research Data gathered:\n{research_data}"
    )
    
    # Using a list of [System, Human] is the most standard and safe way for Gemini
    response = llm.invoke([
        SystemMessage(content=system_instructions),
        HumanMessage(content=human_content)
    ])
    
    # Ensure it returns an AIMessage (which llm.invoke should return)
    return {
        "messages": [response],
        "next_step": "end"
    }
