from fastapi import FastAPI

app = FastAPI(title="Spotify SyncStream Architect")

@app.get("/")
async def root():
    return {
        "message": "Spotify SyncStream Architect is live",
        "status": "online"
    }
