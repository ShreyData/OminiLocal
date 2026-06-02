import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent.orchestrator import initialize_agent

app = FastAPI(title="OmniLocal AI Sidecar")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your tauri app origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the agent once
agent_executor = initialize_agent()

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
        # For simplicity, we execute synchronously for now.
        # LangChain's invoke returns a dictionary with 'output' and 'intermediate_steps'.
        response = agent_executor.invoke({"input": request.message})
        
        # We can extract the thought process from intermediate_steps if needed
        # But for now, let's just send the final answer.
        return {
            "thought_process": "Analysis completed.", # Placeholder for step extraction
            "final_answer": response["output"]
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
