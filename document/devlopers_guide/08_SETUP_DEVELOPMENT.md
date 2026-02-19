# 08 | Setup & Development
**Subject**: Environment Architecture, Dependency Management, and Deployment Workflows  
**Version**: 1.5.0  

---

## 📑 Table of Contents
1. [Environment Infrastructure](#environment-infrastructure)
2. [Dependency Management (Backend/Frontend)](#dependency-management-backendfrontend)
3. [Database Lifecycle (Alembic)](#database-lifecycle-alembic)
4. [Message Broker & Worker Setup (Redis/Celery)](#message-broker--worker-setup-rediscelery)
5. [Local Development Workflow](#local-development-workflow)
6. [Deployment Best Practices](#deployment-best-practices)

---

## 1. Environment Infrastructure
The platform implements a tiered environment strategy (`LOCAL`, `DEV`, `PROD`) controlled via the `APP_ENV` environment variable.

### 1.1 Config Loading (`config.py`)
The system determines the `.env` file to load dynamically:
*   `PROD` -> `.env.prod`
*   `DEV` -> `.env.dev`
*   Others -> `.env`
This allows for zero-conf toggling between local SQLite/Redis and production PostgreSQL/Managed Redis.

---

## 2. Dependency Management
Standardized package management ensures parity across developer environments and CI/CD pipelines.

### 2.1 Backend (Python 3.10+)
*   **Runtime**: FastAPI / Uvicorn.
*   **Manager**: `pip install -r requirements.txt`.
*   **Key Dependencies**: `sqlalchemy` (ORM), `pydantic-settings` (Config validation), `cryptography` (Security).

### 2.2 Frontend (Node 18+)
*   **Runtime**: Vite / React.
*   **Manager**: `npm install`.
*   **Key Dependencies**: `@tanstack/react-query` (Data fetching), `recharts` (Visualization), `zustand` (State).

---

## 3. Database Lifecycle (Alembic)
The database schema is treated as versioned code.

### 3.1 Migration Workflow
1.  **Generate**: `alembic revision --autogenerate -m "description"` captures model changes.
2.  **Apply**: `alembic upgrade head` syncs the current environment to the latest schema.
*   **SuperAdmin Hook**: On startup, the `main.py` script executes manual `SQL text()` blocks to ensure PostgreSQL ENUM types are created if they don't natively exist in the target database.

---

## 4. Message Broker & Worker Setup (Redis/Celery)
The platform depends on a robust worker pipeline for background tasks (Emails, Reports).

### 4.1 Redis Infrastructure
*   **Role**: Acts as both the `CELERY_BROKER_URL` and the dashboard caching layer.
*   **Default Port**: 6379.
*   **Scaling**: In production, Redis instances are separate from the application server to allow for massive queuing of usage reports.

---

## 5. Local Development Workflow
To start the platform from scratch:

1.  **Orchestration**:
    ```bash
    # Terminal 1: Backend
    uvicorn main:app --reload --port 8081
    
    # Terminal 2: Worker
    celery -A app.core.celery_app worker --loglevel=info
    
    # Terminal 3: Frontend
    npm run dev
    ```
2.  **Tunneling**: For local widget testing (e.g., testing `origin_domain` validation), developers should use tools like `ngrok` or `localtunnel` to provide a public URL for the backend.

---

## 6. Deployment Best Practices
When pushing to high-availability environments:

### 6.1 Server Hardening
*   **Uvicorn Workers**: Set `--workers` to `2x(CPU Cores) + 1` for optimal throughput.
*   **CORS**: Ensure `cors_origins` in `.env.prod` explicitly lists only the customer-facing domains.
*   **SSL**: All management traffic and WebSocket streams **MUST** move over HTTPS/WSS to protect against MITM audio interceptions.

---
**END OF SECTION 08**
