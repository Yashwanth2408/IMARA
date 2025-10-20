from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
from pathlib import Path
import asyncio
import json

# Add parent to path
sys.path.append(str(Path(__file__).parent.parent))

from langchain_ollama import OllamaLLM
from agents.research_agents import EnhancedResearcherAgent
from agents.adaptive_router import AdaptiveRouter
from tools.metrics import ResearchMetrics

app = FastAPI(title="IMARA API", version="2.0")

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM
llm = OllamaLLM(model="llama3.2:3b", temperature=0.7)

class ResearchRequest(BaseModel):
    query: str

class AgentStatus(BaseModel):
    agent: str
    status: str
    message: str
    progress: int

@app.get("/")
async def root():
    return {
        "message": "IMARA API v2.0",
        "status": "online",
        "agents": ["researcher", "coder", "reviewer", "presenter"]
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "llm": "llama3.2:3b"}

@app.websocket("/ws/research")
async def research_websocket(websocket: WebSocket):
    """Real-time research with agent updates"""
    await websocket.accept()
    
    try:
        # Receive query
        data = await websocket.receive_json()
        query = data.get("query", "")
        
        # Send start message
        await websocket.send_json({
            "type": "start",
            "message": "Initializing agents..."
        })
        
        # Researcher Agent
        await websocket.send_json({
            "type": "agent_start",
            "agent": "researcher",
            "progress": 25
        })
        
        researcher = EnhancedResearcherAgent(llm)
        router = AdaptiveRouter(llm)
        
        # Routing analysis
        routing_info = router.analyze_query(query)
        await websocket.send_json({
            "type": "routing",
            "data": routing_info
        })
        
        # Research
        result = researcher.research(query)
        await websocket.send_json({
            "type": "agent_complete",
            "agent": "researcher",
            "data": {
                "summary": result['full_summary'],
                "metrics": result.get('quality_metrics', {}),
                "papers": len(result.get('papers', []))
            },
            "progress": 50
        })
        
        # Coder Agent
        await websocket.send_json({
            "type": "agent_start",
            "agent": "coder",
            "progress": 50
        })
        
        code_prompt = f"Generate Python multi-agent code based on: {result['llm_summary'][:300]}"
        code = llm.invoke(code_prompt)
        
        await websocket.send_json({
            "type": "agent_complete",
            "agent": "coder",
            "data": {"code": code},
            "progress": 75
        })
        
        # Reviewer Agent
        await websocket.send_json({
            "type": "agent_start",
            "agent": "reviewer",
            "progress": 75
        })
        
        review_prompt = f"Review this code: {code[:400]}"
        review = llm.invoke(review_prompt)
        
        await websocket.send_json({
            "type": "agent_complete",
            "agent": "reviewer",
            "data": {"review": review},
            "progress": 90
        })
        
        # Final report
        report = {
            "research": result['full_summary'],
            "code": code,
            "review": review,
            "metrics": result.get('quality_metrics', {}),
            "routing": routing_info
        }
        
        await websocket.send_json({
            "type": "complete",
            "data": report,
            "progress": 100
        })
        
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })

@app.post("/api/research")
async def research(request: ResearchRequest):
    """Standard REST endpoint for research"""
    try:
        researcher = EnhancedResearcherAgent(llm)
        result = researcher.research(request.query)
        
        return {
            "success": True,
            "data": {
                "summary": result['full_summary'],
                "metrics": result.get('quality_metrics', {}),
                "papers": len(result.get('papers', []))
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
