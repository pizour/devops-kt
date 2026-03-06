"""Demo API for DevOps KT Session 8 (GitOps + APIs)
==============================================

Requirements:
    pip install fastapi uvicorn

Run:
    python3 demo_api.py
    # or directly with uvicorn (for reload):
    uvicorn demo_api:app --host 0.0.0.0 --port 5000 --reload

Access term:
    http://<vm-ip>:5000
"""

from typing import Dict, List, Optional
import time
import uuid

from fastapi import FastAPI, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

app = FastAPI(title="DevOps KT Demo API", version="1.0")

# In-memory storage
engineers: Dict[str, Dict] = {
    "1": {
        "id": "1",
        "name": "Alice",
        "role": "Network Engineer",
        "skills": ["BGP", "OSPF", "firewalls", "VPN"],
        "level": "senior",
    },
    "2": {
        "id": "2",
        "name": "Bob",
        "role": "Systems Engineer",
        "skills": ["Linux", "Ansible", "Docker", "Terraform"],
        "level": "mid",
    },
    "3": {
        "id": "3",
        "name": "Charlie",
        "role": "Cloud Engineer",
        "skills": ["Azure", "Kubernetes", "CI/CD", "Terraform"],
        "level": "junior",
    },
}

VALID_TOKEN = "kt-session-8-token"


class Engineer(BaseModel):
    name: str
    role: str
    skills: List[str] = Field(default_factory=list)
    level: str = "junior"


@app.get("/", summary="Welcome")
def root():
    return {
        "message": "DevOps KT – Demo API",
        "session": 8,
        "docs": "Visit /api/v1/engineers",
        "token": VALID_TOKEN,
    }


@app.get("/health", summary="Health check")
def health():
    return {"status": "healthy", "timestamp": time.time()}


@app.get("/api/v1/engineers", summary="List engineers")
def list_engineers():
    return {"count": len(engineers), "engineers": list(engineers.values())}


@app.get("/api/v1/engineers/{engineer_id}", summary="Retrieve engineer")
def get_engineer(engineer_id: str):
    engineer = engineers.get(engineer_id)
    if not engineer:
        raise HTTPException(status_code=404, detail="Engineer not found")
    return engineer


@app.post("/api/v1/engineers", status_code=201, summary="Create engineer")
def create_engineer(payload: Engineer):
    new_id = str(uuid.uuid4())[:8]
    engineer = payload.dict()
    engineer["id"] = new_id
    engineers[new_id] = engineer
    return engineer


@app.put("/api/v1/engineers/{engineer_id}", summary="Replace engineer")
def replace_engineer(engineer_id: str, payload: Engineer):
    if engineer_id not in engineers:
        raise HTTPException(status_code=404, detail="Engineer not found")

    engineer = payload.dict()
    engineer["id"] = engineer_id
    engineers[engineer_id] = engineer
    return engineer


@app.patch("/api/v1/engineers/{engineer_id}", summary="Update engineer")
def patch_engineer(engineer_id: str, payload: Dict[str, Optional[str]]):
    if engineer_id not in engineers:
        raise HTTPException(status_code=404, detail="Engineer not found")

    allowed = {"name", "role", "skills", "level"}
    unknown = set(payload.keys()) - allowed
    if unknown:
        raise HTTPException(status_code=400, detail={"error": "Unknown fields", "allowed": list(allowed)})

    engineers[engineer_id].update({k: v for k, v in payload.items() if v is not None})
    return engineers[engineer_id]


@app.delete("/api/v1/engineers/{engineer_id}", summary="Delete engineer")
def delete_engineer(engineer_id: str):
    if engineer_id not in engineers:
        raise HTTPException(status_code=404, detail="Engineer not found")
    return {"message": "Deleted", "engineer": engineers.pop(engineer_id)}


@app.get("/api/v1/search", summary="Search by skill")
def search(skill: str):
    skill_lower = skill.lower()
    matches = [e for e in engineers.values() if skill_lower in (s.lower() for s in e.get("skills", []))]
    return {"query": skill, "count": len(matches), "results": matches}


@app.get("/api/v1/slow", summary="Simulate latency")
def slow(seconds: int = 3):
    wait = min(seconds, 10)
    time.sleep(wait)
    return {"message": f"Delayed {wait}s", "tip": "Use --connect-timeout with curl"}


@app.get("/api/v1/error", summary="Simulate server error")
def error():
    raise HTTPException(status_code=500, detail="Simulated server failure")


@app.get("/api/v1/protected", summary="Token protected")
def protected(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Authorization bearer token")
    token = authorization.split(" ", 1)[1]
    if token != VALID_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")
    return {"message": "Authenticated", "authenticated": True}


@app.exception_handler(404)
def not_found(request: Request, exc: HTTPException):
    return JSONResponse(status_code=404, content={"error": "Not found", "path": request.url.path})


@app.exception_handler(405)
def method_not_allowed(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=405,
        content={"error": "Method not allowed", "method": request.method, "path": request.url.path},
    )


if __name__ == "__main__":
    import uvicorn

    print("DevOps KT – Demo API (FastAPI + uvicorn)")
    print("token:", VALID_TOKEN)
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")
