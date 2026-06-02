import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent.graph import app as graph_app
from langchain_core.messages import HumanMessage

app = FastAPI(title="OmniLocal AI Sidecar")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your tauri app origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    thought_process: str
    final_answer: str

@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Endpoint to receive user messages and return agent responses.
    """
    try:
        # Initialize the AgentState
        initial_state = {
            "messages": [HumanMessage(content=request.message)],
            "research_data": "",
            "next_step": ""
        }
        
        # Invoke the LangGraph workflow
        result = graph_app.invoke(initial_state)
        
        # Extract final answer from the last message
        final_answer = result["messages"][-1].content
        
        # Extract thought process (research_data)
        thought_process = result.get("research_data", "")
        if not thought_process:
            thought_process = "I analyzed your request locally."
            
        return {
            "thought_process": thought_process,
            "final_answer": final_answer
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    import os
    mode = "cloud" if os.getenv("GEMINI_API_KEY") else "local"
    return {
        "status": "ok",
        "mode": mode,
        "model": "gemma-4-26b-a4b-it" if mode == "cloud" else "gemma4:e4b"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
