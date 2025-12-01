from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import time
import os
import sys

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents.extract_agent import ExtractAgent
from src.agents.verify_agent import VerifyAgent
from src.agents.memory_agent import MemoryAgent
from src.agents.scout_agent import ScoutAgent
from src.tools.real_incident_feed import RealIncidentFeed
from src.config import DEFAULT_MAP_CENTER

app = FastAPI(title="AURA API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# State
class SystemState:
    def __init__(self):
        self.extract_agent = ExtractAgent()
        self.verify_agent = VerifyAgent()
        self.memory_agent = MemoryAgent()
        self.scout_agent = ScoutAgent()
        self.real_feed = RealIncidentFeed()
        self.processed_count = 0
        self.last_activity = time.time()
        self.logs = []

state = SystemState()

# Models
class SimulationRequest(BaseModel):
    mock_mode: bool = True

class LogEntry(BaseModel):
    timestamp: str
    level: str
    message: str

# Endpoints
@app.get("/status")
def get_status():
    return {
        "status": "online",
        "incidents_count": len(state.memory_agent.incidents),
        "processed_count": state.processed_count
    }

@app.post("/reset")
def reset_system():
    global state
    state = SystemState()
    return {"message": "System reset complete"}

@app.get("/incidents")
def get_incidents():
    return state.memory_agent.get_all_incidents()

@app.post("/simulate")
def run_simulation_step(req: SimulationRequest):
    try:
        # 1. Get Data
        text = ""
        source = ""
        
        if req.mock_mode:
            import pandas as pd
            df = pd.read_csv("data/disaster_stream.csv")
            # Loop indefinitely using modulo
            row_index = state.processed_count % len(df)
            row = df.iloc[row_index]
            text = row['text']
            source = row['source']
            state.last_activity = time.time()
        else:
            incident = state.real_feed.get_next_incident()
            if incident:
                text = incident['text']
                source = incident['source']
                state.last_activity = time.time()
            else:
                # Proactive Search Logic
                if time.time() - state.last_activity > 10:
                    import random
                    log_entries = []
                    log_entries.append("System: Idle for 10s. Initiating Proactive Search...")
                    
                    queries = [
                        "latest natural disasters news",
                        "breaking earthquake alerts twitter",
                        "flood warnings global",
                        "wildfire updates reddit",
                        "tsunami warning recent",
                        "site:facebook.com disaster reports public",
                        "site:twitter.com emergency alerts",
                        "site:reddit.com r/disasterupdate"
                    ]
                    query = random.choice(queries)
                    log_entries.append(f"Scout Agent: Proactively searching for '{query}'...")
                    
                    results = state.scout_agent.fetch_updates([query], mock_mode=False)
                    
                    if results:
                        # Use the first result as a new incident lead
                        best_result = results[0]
                        text = best_result.get('content', '')
                        source = f"Proactive Scout ({best_result.get('source', 'Web')})"
                        state.last_activity = time.time()
                        
                        # Continue to processing...
                    else:
                        return {"status": "waiting", "message": "Proactive search yielded no results", "logs": log_entries}
                else:
                    return {"status": "waiting", "message": "No new incidents"}

        # 2. Process
        start_time = time.time()
        
        # Extract
        extracted = state.extract_agent.extract(text, mock_mode=req.mock_mode)
        extracted["source"] = source
        
        if 'log_entries' not in locals():
            log_entries = []
        log_entries.append(f"Ingesting: {text[:50]}...")
        
        if extracted["incident_type"] != "Error":
            log_entries.append(f"Extract Agent: Identified {extracted['incident_type']} at {extracted['location_text']}")
            
            # Scout
            log_entries.append(f"Scout Agent: Generating search strategy...")
            queries = state.scout_agent.generate_strategy(f"{extracted['incident_type']} in {extracted['location_text']}")
            log_entries.append(f"Scout Agent: Executing {len(queries)} search queries...")
            updates = state.scout_agent.fetch_updates(queries, mock_mode=req.mock_mode)
            
            # Verify
            log_entries.append(f"Verify Agent: Cross-referencing {len(updates)} sources...")
            verification = state.verify_agent.verify(extracted, search_results=updates)
            log_entries.append(f"Verify Agent: Credibility Score {verification['credibility_score']}/100")
            
            if verification['is_verified']:
                extracted.update(verification)
                log_entries.append(f"Memory Agent: Consolidating incident...")
                result = state.memory_agent.consolidate(extracted, mock_mode=req.mock_mode)
                if 'incident_id' in result:
                    extracted['id'] = result['incident_id']
                log_entries.append(f"System: {result['action'].upper()} Incident #{result['incident_id']}")
            else:
                log_entries.append("Verify Agent: Rejected (Low Credibility)")
        else:
            log_entries.append("Extract Agent: Extraction Failed")

        state.processed_count += 1
        
        # Only return the incident if it was verified and consolidated
        final_incident = extracted if (extracted["incident_type"] != "Error" and extracted.get("is_verified")) else None

        return {
            "status": "success",
            "logs": log_entries,
            "raw_data": {"text": text, "source": source, "timestamp": time.strftime("%H:%M:%S")},
            "incident": final_incident
        }

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Serve Static Files (Frontend)
app.mount("/", StaticFiles(directory="web", html=True), name="static")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 AURA System Online")
    print("🌍 Dashboard: http://localhost:8000")
    print("="*50 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
