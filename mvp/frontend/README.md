# Frontend

## Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Create `.env` file (optional):
```env
VITE_API_BASE_URL=http://localhost:8000
```

3. Start development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Project Structure

```
frontend/
├── src/
│   ├── components/      # Reusable components
│   ├── pages/          # Page components
│   ├── services/        # API services
│   ├── context/         # State management
│   ├── App.jsx          # Main app component
│   └── main.jsx         # Entry point
├── public/              # Static assets
└── package.json         # Dependencies
```

