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
        print(f"DEBUG: Received message: {request.message}")
        # Initialize the AgentState
        initial_state = {
            "messages": [HumanMessage(content=request.message)],
            "research_data": "",
            "next_step": ""
        }
        
        # Invoke the LangGraph workflow
        print("DEBUG: Invoking Graph...")
        result = graph_app.invoke(initial_state)
        print("DEBUG: Graph invocation successful.")
        
        # Extract final answer from the last message
        raw_answer = result["messages"][-1].content
        # Ensure it is a string (Gemini sometimes returns a list of parts)
        if isinstance(raw_answer, list):
            final_answer = "\n".join([str(p.get("text", "")) if isinstance(p, dict) else str(p) for p in raw_answer])
        else:
            final_answer = str(raw_answer)
        
        # Extract thought process (research_data)
        thought_process = str(result.get("research_data", ""))
        if not thought_process or thought_process.strip() == "":
            thought_process = "I analyzed your request locally."
            
        print(f"DEBUG: Sending response. Final Answer length: {len(final_answer)}")
        return {
            "thought_process": thought_process,
            "final_answer": final_answer
        }
    except Exception as e:
        import traceback
        print("DEBUG: ERROR IN CHAT ENDPOINT")
        traceback.print_exc()
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
