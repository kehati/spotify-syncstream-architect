# SyncStream Architect 🎧

**SyncStream Architect** is a real-time playback supervisor for Spotify. It monitors your active listening session and automatically skips tracks that don't align with your current cognitive or emotional goals. Whether you need a deep-work "Focus Guard" or a minimum "Energy Floor" for a workout, Architect acts as a headless DJ that keeps the vibe consistent without manual intervention.

---

## 🛠 Why this exists
Standard Spotify "Radios" and "Discovery" playlists are great, but they often throw in high-energy tracks or lyrical distractions right when you're in a flow state. Architect was built to:
* **Enforce strict audio feature constraints** (instrumentalness, energy, valence) in real-time.
* **Bridge the Gap**: Connect Spotify's deep data (Audio Features) with automated playback control.
* **Stay Headless**: Run as a background service on a server or Raspberry Pi.
* **Stay Flexible**: Switch strategies or tweak thresholds on-the-fly via a REST API.

---

## 🚀 Tech Stack
* **FastAPI**: Core API and background task orchestration.
* **Redis**: High-speed storage for active strategy configurations and state.
* **Spotify Web API**: Real-time playback and audio feature analysis.
* **Structlog**: Structured logging with filename and line-number tracking.
* **Docker**: Full containerization for "set it and forget it" deployment.

---

## 🏗 Spotify System Architecture

The system operates as an asynchronous event loop. Every few seconds, the **Engine** polls your Spotify state, fetches the audio profile of the current song, and passes it to the **Strategy Resolver**. The resolver instantiates the appropriate logic class to make a `KEEP` or `SKIP` decision.



---

## 📦 Installation & Setup

### Prerequisites
* **Spotify Developer App**: Create one at [developer.spotify.com](https://developer.spotify.com/dashboard) and set the redirect URI to `http://localhost:8000/callback`.
* **Docker & Docker Compose**.

### 1. Clone & Configure
```bash
git clone [https://github.com/kehati/spotify-syncstream-architect.git](https://github.com/kehati/spotify-syncstream-architect.git)
cd spotify-syncstream-architect
cp .env.example .env
```
### 2. Environment Variables
Edit your .env file with your credentials:
```bash
# Spotify Credentials
SPOTIFY_CLIENT_ID=mock_id
SPOTIFY_CLIENT_SECRET=mock_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/auth/callback

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Mode Toggle
MOCK_MODE=True
```
### 3. Build & Run
```bash
docker-compose up --build -d
```

## 🧪 Strategies & Logic

The engine handles three core strategies seeded into Redis on startup. Each strategy implements an evaluate() method that checks the AudioFeatures of the current track:

| Strategy Class | ID | Parameter Keys | Skip Condition |
| :--- | :--- | :--- | :--- |
| `FocusGuardStrategy` | `focus` | `instrumentalness`, `energy` | `feat.energy > param` OR `feat.inst < param` |
| `EnergyFloorStrategy` | `energy` | `energy_floor` | `feat.energy < param` |
| `VibeShiftStrategy` | `vibe` | `min_valence` | `feat.valence < param` |

### How to Implement a New Strategy

Adding a new behavior to Spotify Architect is a three-step process.

### 1. Create the Strategy Class
Add a new file in `app/strategies/` that implements an `evaluate` method.

### 2. Register in the Strategy Factory
Map your new strategy id to the class in `app/strategies/strategy_factory.py`

### 3. Seed the new Strategy
Seed the new strategy in `app/core/seeding.py` during startup.

## 📡 API Usage

The Architect API provides a lightweight interface to monitor the engine and manage your playback strategies in real-time. By default, the service is available at `http://localhost:8000/api/v1`.

### 1. Engine & System Status
Monitor the background loop and see which track is currently being analyzed by the active strategy.

**Check Engine Heartbeat:**
```bash
curl http://localhost:8000/api/v1/engine/status
```

### 2. Strategy Catalog
View all available strategies stored in Redis and update their sensitivity thresholds.

* List All Available Strategies:
```bash
curl http://localhost:8000/api/v1/strategies
```
* Update Strategy Parameters:
```bash
curl -X PUT http://localhost:8000/api/v1/strategies/{strategy_id}
    -H "Content-Type: application/json" \
    -d '{"parameters": {"energy": 0.35, "instrumentalness": 0.8}}'
```
### 3. Active Strategy Management
Switch between different strategies on-the-fly without restarting the service.
* Get Current Active Strategy:
```bash
curl http://localhost:8000/api/v1/strategies/active
```
* Switch Active Strategy
```bash
curl -X POST http://localhost:8000/api/v1/strategies/active \
     -H "Content-Type: application/json" \
     -d '{"id": "energy"}'
```

### Response Format
All API responses are in JSON format, providing clear feedback on operations and current states:
```json
{
  "id": "focus",
  "name": "Focus Guard",
  "description": "Skips songs with lyrics or high energy.",
  "is_active": true,
  "parameters": {
    "instrumentalness": 0.75,
    "energy": 0.5
  }
}
```
## 📜 License

This project is licensed under the terms of the [**MIT License**](https://opensource.org/license/mit/).