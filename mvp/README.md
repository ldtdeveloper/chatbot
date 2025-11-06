# Voice Assistant Platform - MVP

A platform for managing OpenAI Realtime API voice assistants. Users can configure prompts, voice settings, noise reduction, and generate embeddable widget code.

## Project Structure

```
mvp/
├── backend/          # Python FastAPI backend
│   ├── app/
│   │   ├── models/          # Database models
│   │   ├── routes/          # API endpoints
│   │   ├── services/        # Business logic
│   │   ├── utils/           # Utilities
│   │   ├── config.py        # Configuration
│   │   ├── database.py      # DB setup
│   │   └── schemas.py        # Pydantic schemas
│   ├── main.py              # FastAPI app
│   └── requirements.txt     # Dependencies
│
└── frontend/         # React frontend
    ├── src/
    │   ├── components/      # Reusable components
    │   ├── pages/          # Page components
    │   ├── services/        # API services
    │   └── context/         # State management
    └── package.json         # Dependencies
```

## Features

### User Management
- User registration and authentication
- JWT-based authentication
- User dashboard

### OpenAI Key Management
- Store encrypted OpenAI API keys per user
- Multiple keys support
- Activate/deactivate keys

### Prompt Management
- Create and manage Audio Prompts
- Version control for prompts
- System instructions per version
- Integration with OpenAI Prompt API

### Assistant Configuration
- Voice selection (alloy, echo, fable, onyx, nova, shimmer)
- Noise reduction settings (near field / far field)
- VAD (Voice Activity Detection) configuration
- Prompt and version selection

### Widget Code Generator
- Generate embeddable JavaScript code
- Unique widget IDs for tracking
- Ready-to-use widget code for websites

## Quick Start

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings
uvicorn main:app --reload
```

Backend runs on `http://localhost:8000`
API docs at `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:3000`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### OpenAI Keys
- `GET /api/openai-keys` - List keys
- `POST /api/openai-keys` - Create key
- `DELETE /api/openai-keys/{id}` - Delete key
- `PATCH /api/openai-keys/{id}/toggle` - Toggle active status

### Prompts
- `GET /api/prompts` - List prompts
- `POST /api/prompts` - Create prompt
- `GET /api/prompts/{id}` - Get prompt with versions
- `POST /api/prompts/{id}/versions` - Create version
- `PUT /api/prompts/{id}/versions/{version_id}` - Update version
- `DELETE /api/prompts/{id}` - Delete prompt

### Assistant Config
- `GET /api/assistant-config` - Get config
- `PUT /api/assistant-config` - Update config

### Widget
- `GET /api/widget/code` - Generate widget code

## Technology Stack

### Backend
- FastAPI - Modern Python web framework
- SQLAlchemy - ORM
- Pydantic - Data validation
- JWT - Authentication
- Cryptography - API key encryption

### Frontend
- React 18 - UI library
- React Router - Routing
- TanStack Query - Data fetching
- Axios - HTTP client
- Zustand - State management
- Vite - Build tool

## Next Steps

1. Implement WebSocket proxy for real-time voice communication
2. Integrate with OpenAI Realtime API
3. Build the actual widget component
4. Add analytics and usage tracking
5. Implement prompt versioning with OpenAI API
6. Add more configuration options

