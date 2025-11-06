# Backend

## Setup

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
```

3. Run database migrations (if using Alembic):
```bash
alembic upgrade head
```

4. Start the server:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

## Project Structure

```
backend/
├── app/
│   ├── models/          # SQLAlchemy models
│   ├── routes/          # API routes
│   ├── services/        # Business logic
│   ├── utils/           # Utility functions
│   ├── config.py        # Configuration
│   ├── database.py      # Database setup
│   └── schemas.py        # Pydantic schemas
├── main.py              # FastAPI application
└── requirements.txt     # Python dependencies
```

