import os
from fastapi import FastAPI

app = FastAPI(title="Spotify Syncstream Architect")

@app.get("/")
async def root():
    """Basic landing page to verify the API is reachable."""
    return {
        "message": "Hello from SyncStream Architect!",
        "version": "0.1.0",
        "container_id": os.uname().nodename
    }

@app.get("/hello/{name}")
async def hello_user(name: str):
    """Dynamic route to verify FastAPI routing and parameter handling."""
    return {
        "greeting": f"Hello, {name}!",
        "context": "You are running inside a Docker container."
    }
