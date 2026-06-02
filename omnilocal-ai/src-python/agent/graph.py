from langgraph.graph import StateGraph, START, END
from .state import AgentState
from .nodes import architect_node, tools_node, stylist_node

def router(state: AgentState):
    """
    Returns the next step from the state.
    """
    return state["next_step"]

# Initialize StateGraph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("architect", architect_node)
workflow.add_node("tools", tools_node)
workflow.add_node("stylist", stylist_node)

# Define edges
workflow.add_edge(START, "architect")

# Conditional edges from architect
workflow.add_conditional_edges(
    "architect",
    router,
    {
        "tools": "tools",
        "format": "stylist"
    }
)

# Return to architect after tool use
workflow.add_edge("tools", "architect")

# End after styling
workflow.add_edge("stylist", END)

# Compile the graph
app = workflow.compile()
