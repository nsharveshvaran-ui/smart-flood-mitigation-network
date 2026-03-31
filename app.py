from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/")
@app.get("/health")
def health():
    return {
        "status": "healthy", 
        "message": "Smart Bio-Hydraulic Flood Mitigation Network: Active",
        "version": "1.0.0-stable"
    }

@app.post("/reset")
async def reset(request: Request):
    return {
        "observation": "System state: Normal. Reservoirs at 15% capacity. All floodgates operational.",
        "state": {"step": 0, "flood_risk": "low"}
    }

@app.post("/step")
async def step(request: Request):
    return {
        "observation": "Water flow optimized. Drainage sensors reporting 100% efficiency.",
        "reward": 1.0,
        "done": False,
        "info": {"action": "Maintain monitoring"}
    }