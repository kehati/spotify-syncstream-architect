# Project Context: Spotify SyncStream Architect

## 1. Project Overview
**SyncStream Architect** is an intelligent, background music orchestration engine. It continuously monitors a user's Spotify playback and applies dynamic "Strategies" (rules) to govern the music flow (e.g., skipping tracks based on audio features, tempo, or genre).

* **Core Goal:** Automate Spotify playback management using configurable logic.
* **Tech Stack:** Python 3.12+, FastAPI, Redis (Async), Spotify Web API (via `httpx`), Pytest.

---

## 2. Architecture & Design

### 2.1 System Components
The system consists of three primary layers:

1.  **The API Layer (FastAPI):**
    * Exposes endpoints to manage strategies and control the engine.
    * Uses **Dependency Injection** for service access.
    * **Entry Point:** Singleton `app` instance defined in `app/main.py` (No application factory).
2.  **The Core Engine (`SyncStreamEngine`):**
    * A long-running asynchronous background task.
    * **Lifecycle:** Polls Spotify $\rightarrow$ Fetches Active Strategy $\rightarrow$ Evaluates Track $\rightarrow$ Executes Action (e.g., Skip).
    * **State:** Maintains internal state (`is_running`, `current_track`) accessible via `app.state.engine`.
3.  **The Data Layer (Redis):**
    * Persists Strategy Configurations (`StrategyConfig`).
    * Stores the ID of the currently active strategy.
    * Utilizes a connection pool where clients are instantiated per operation (Provider Pattern) to ensure thread safety.

### 2.2 Key Design Patterns
* **Strategy Pattern:** Encapsulates different logic rules (e.g., `VibeCheckStrategy`, `TempoStrategy`) behind a common interface.
* **Factory Pattern:** `StrategyFactory` instantiates specific strategy classes based on the configuration stored in Redis.
* **Provider Pattern:** Redis connections are retrieved from a global pool `redis_manager.get_client()` on demand, ensuring connection health.

---

## 3. Implementation Details

### 3.1 Directory Structure
```text
project_root/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── engine.py       # Control endpoints (Start/Stop/Status)
│   │       └── strategies.py   # CRUD for Strategy Configurations
│   ├── core/
│   │   ├── config.py           # Pydantic Settings
│   │   └── redis.py            # RedisManager (Singleton Pool)
│   ├── models/                 # Pydantic Models (StrategyConfig, etc.)
│   ├── services/
│   │   ├── engine.py           # SyncStreamEngine logic
│   │   ├── strategy_manager.py # Redis abstraction layer
│   │   └── spotify/            # Spotify API Client (Prod & Mock)
│   └── main.py                 # App entry point & Lifespan handler
├── tests/
│   ├── api/                    # FastAPI Endpoints Tests
│   ├── integration/            # Service + Real Redis Tests
│   └── unit/                   # Pure logic tests
├── pyproject.toml
└── CONTEXT.md
```

### 3.2 Redis Schema
* `strategies:catalog` (Hash): Stores JSON representations of strategies. Field = `strategy_id`.
* `strategies:active_id` (String): The ID of the currently enforced strategy.

### 3.3 Critical Dependencies
* `fastapi`
* `redis` (Asyncio support)
* `pydantic-settings`
* `httpx` (Required for SpotifyService and API Tests)
* `pytest` & `pytest-asyncio`

### 3.4 Repository
* **URL:** `https://github.com/kehati/spotify-syncstream-architect`
* **Usage:** This repository serves as the single source of truth for the codebase.
    * **Verification:** Before proposing significant architectural changes, verify existing implementations against the repo.
    * **Structure:** Follow the directory structure in the repo for all new files.

---

## 4. Testing Strategy
The testing suite is divided into **Integration** (Real Resources) and **API** (Mocked Resources).

### 4.1 Integration Tests (`tests/integration/`)
* **Scope:** Tests `StrategyManager` and Redis interactions.
* **Configuration:** Uses `tests/integration/conftest.py`.
* **Mechanism:**
    * Connects to a real Redis instance (Localhost/Docker).
    * Uses `patch.object(redis_manager, 'get_client')` to redirect application code to the test fixture's Redis connection.

### 4.2 API Tests (`tests/api/`)
* **Scope:** Tests FastAPI routers (`/api/v1/...`).
* **Configuration:** Uses `tests/api/conftest.py`.
* **Critical Mechanisms:**
    1.  **Lifespan Override:** Replaces the app's real startup (which connects to Redis/Spotify) with a "No-Op" lifespan to keep tests fast and isolated.
    2.  **State Injection:** Manually injects `mock_engine` into `app.state.engine` so routers can access it.
    3.  **Mock Defaults:** The `mock_engine` explicitly sets attributes like `last_evaluation = None` to prevent `JSON Serialization Error: Object of type Mock is not JSON serializable` (500 Errors).

**Example API Fixture (`conftest.py`):**
```python
@pytest.fixture
def mock_engine(mock_strategy_manager):
    # Relaxed Mock (No spec) allowing dynamic attributes
    mock = AsyncMock()
    mock.strategy_manager = mock_strategy_manager
    mock._stop_event = Mock()
    mock._stop_event.is_set.return_value = False
    
    # SAFE DEFAULTS (Prevents 500 Errors)
    mock.last_evaluation = None 
    mock.current_track = None 
    
    return mock
```

---

## 5. Build & Configuration

### 5.1 Environment Variables
Create a `.env` file for local development:
```ini
PROJECT_NAME="Spotify SyncStream Architect"
DEBUG=True

# Spotify Credentials
SPOTIFY_CLIENT_ID="your_id"
SPOTIFY_CLIENT_SECRET="your_secret"
SPOTIFY_REFRESH_TOKEN="your_token"
SPOTIFY_MOCK_MODE=False  # Set True for local dev without API calls

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Engine
ENGINE_POLL_INTERVAL=10
```

### 5.2 Running the Application
```bash
# Run with UV (or standard uvicorn)
uv run uvicorn app.main:app --reload
```

### 5.3 Running Tests
```bash
# Run all tests
uv run pytest -v

# Run only API tests (Fast)
uv run pytest tests/api/ -v

# Run Integration tests (Requires Redis)
uv run pytest tests/integration/ -v
```

---

## 6. Known Pitfalls & Solutions
1.  **Redis Connection Lifecycle:**
    * *Issue:* Using a single client instance as a class variable causes connection timeouts/closures.
    * *Solution:* Always fetch a client via `redis_manager.get_client()` inside the method scope.
2.  **Testing 500 Errors (JSON Serialization):**
    * *Issue:* API tests returning 500 instead of 200/404.
    * *Cause:* Mock objects returning child Mocks when accessing properties like `active_strategy.id`, which fail Pydantic validation or JSON serialization.
    * *Solution:* Explicitly define return values (e.g., `mock.get_active_strategy.return_value = valid_config_object`) in the test setup.
3.  **Lifespan in Tests:**
    * *Issue:* Tests hanging or failing to connect to Redis.
    * *Solution:* Use `app.router.lifespan_context = noop_lifespan` in API tests to bypass the real startup sequence.
4.  **Router Instantiation & Patching:**
    * *Issue:* `500 Internal Server Error` (Connection Pool not initialized).
    * *Cause:* Routers instantiating global services (`manager = StrategyManager()`) at import time.
    * *Solution:* When patching dependencies in `conftest.py`, target the **instance variable** in the router module (e.g., `app.api.v1.strategies.manager`), OR refactor to use `Depends()`.